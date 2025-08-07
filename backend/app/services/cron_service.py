from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from ..models.cron_job import CronJobCreate, CronJobResponse, CronJobStatus
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class CronService:
    def __init__(self):
        # Configuração do scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        self.scheduler.start()
        
        # Armazenamento local dos jobs (em produção, usar banco de dados)
        self.jobs: Dict[str, Dict] = {}
    
    async def create_cron_job(self, job_data: CronJobCreate) -> CronJobResponse:
        """Cria um novo cron job para sincronização automática"""
        try:
            # Validar expressão cron
            CronTrigger.from_crontab(job_data.cron_expression)
            
            job_id = str(uuid.uuid4())
            created_at = datetime.now()
            
            # Criar o job no scheduler
            job = self.scheduler.add_job(
                func=self._execute_sync_job,
                trigger=CronTrigger.from_crontab(job_data.cron_expression),
                args=[job_id, job_data.overwrite, job_data.max_tables],
                id=job_id,
                name=job_data.name,
                replace_existing=True
            )
            
            # Armazenar informações do job
            job_info = {
                "id": job_id,
                "name": job_data.name,
                "cron_expression": job_data.cron_expression,
                "description": job_data.description,
                "status": CronJobStatus.ACTIVE,
                "next_run": job.next_run_time,
                "created_at": created_at,
                "last_run": None,
                "overwrite": job_data.overwrite,
                "max_tables": job_data.max_tables
            }
            
            self.jobs[job_id] = job_info
            
            logger.info(f"Cron job criado com sucesso: {job_data.name} (ID: {job_id})")
            
            return CronJobResponse(**job_info)
            
        except Exception as e:
            logger.error(f"Erro ao criar cron job: {e}")
            raise Exception(f"Erro ao criar cron job: {str(e)}")
    
    def list_cron_jobs(self) -> List[CronJobResponse]:
        """Lista todos os cron jobs"""
        try:
            jobs = []
            for job_id, job_info in self.jobs.items():
                # Atualizar next_run do scheduler
                scheduler_job = self.scheduler.get_job(job_id)
                if scheduler_job:
                    job_info["next_run"] = scheduler_job.next_run_time
                    job_info["status"] = CronJobStatus.ACTIVE if scheduler_job.next_run_time else CronJobStatus.PAUSED
                else:
                    job_info["status"] = CronJobStatus.REMOVED
                
                jobs.append(CronJobResponse(**job_info))
            
            return jobs
            
        except Exception as e:
            logger.error(f"Erro ao listar cron jobs: {e}")
            raise Exception(f"Erro ao listar cron jobs: {str(e)}")
    
    def delete_cron_job(self, job_id: str) -> bool:
        """Remove um cron job"""
        try:
            if job_id not in self.jobs:
                raise Exception(f"Cron job com ID {job_id} não encontrado")
            
            # Remover do scheduler
            self.scheduler.remove_job(job_id)
            
            # Remover do armazenamento local
            del self.jobs[job_id]
            
            logger.info(f"Cron job removido com sucesso: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover cron job {job_id}: {e}")
            raise Exception(f"Erro ao remover cron job: {str(e)}")
    
    async def _execute_sync_job(self, job_id: str, overwrite: bool, max_tables: int):
        """Função executada pelo cron job para sincronização"""
        try:
            logger.info(f"Iniciando execução do cron job {job_id}")
            
            # Atualizar last_run
            if job_id in self.jobs:
                self.jobs[job_id]["last_run"] = datetime.now()
            
            # Executar sincronização
            source_tables = DatabaseService.get_source_tables(sort_by_dependencies=True)
            
            results = []
            migrated_count = 0
            
            for table in source_tables.tables[:max_tables]:
                try:
                    result = DatabaseService.migrate_table(table.table_name, overwrite)
                    results.append(result)
                    
                    if result["success"]:
                        migrated_count += 1
                        logger.info(f"Cron job {job_id}: Tabela {table.table_name} migrada com sucesso")
                    else:
                        logger.warning(f"Cron job {job_id}: Falha na migração da tabela {table.table_name}")
                        
                except Exception as e:
                    logger.error(f"Cron job {job_id}: Erro ao migrar tabela {table.table_name}: {e}")
                    results.append({
                        "success": False,
                        "table_name": table.table_name,
                        "error": str(e)
                    })
            
            logger.info(f"Cron job {job_id} concluído: {migrated_count} tabelas migradas de {len(source_tables.tables[:max_tables])}")
            
        except Exception as e:
            logger.error(f"Erro na execução do cron job {job_id}: {e}")
    
    def get_job_count(self) -> int:
        """Retorna o número total de cron jobs"""
        return len(self.jobs)
    
    def shutdown(self):
        """Desliga o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()


# Instância global do serviço
cron_service = CronService() 