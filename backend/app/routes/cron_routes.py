from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from ..services.cron_service import cron_service
from ..models.cron_job import (
    CronJobCreate, 
    CronJobResponse, 
    CronJobList, 
    CronJobDelete
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cron", tags=["cron"])


@router.post("/jobs", response_model=CronJobResponse, status_code=status.HTTP_201_CREATED)
async def create_cron_job(job_data: CronJobCreate):
    """
    Cadastra um novo cron job para executar a sincronização automática de todas as tabelas
    
    - **name**: Nome do cron job
    - **cron_expression**: Expressão cron (ex: '0 */6 * * *' para a cada 6 horas)
    - **description**: Descrição opcional do cron job
    - **overwrite**: Se deve sobrescrever tabelas existentes no destino
    - **max_tables**: Número máximo de tabelas para migrar por execução
    """
    try:
        return await cron_service.create_cron_job(job_data)
    except Exception as e:
        logger.error(f"Erro ao criar cron job: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/jobs", response_model=CronJobList)
async def list_cron_jobs():
    """
    Lista todos os cron jobs cadastrados
    
    Retorna uma lista com todos os cron jobs ativos, incluindo informações sobre:
    - Status do job
    - Próxima execução
    - Última execução
    - Configurações de sincronização
    """
    try:
        jobs = cron_service.list_cron_jobs()
        return CronJobList(
            jobs=jobs,
            total=len(jobs)
        )
    except Exception as e:
        logger.error(f"Erro ao listar cron jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar cron jobs: {str(e)}"
        )


@router.delete("/jobs/{job_id}", response_model=CronJobDelete)
async def delete_cron_job(job_id: str):
    """
    Remove um cron job específico
    
    - **job_id**: ID único do cron job a ser removido
    """
    try:
        success = cron_service.delete_cron_job(job_id)
        return CronJobDelete(
            success=success,
            message=f"Cron job {job_id} removido com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao remover cron job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/jobs/count")
async def get_cron_job_count():
    """
    Retorna o número total de cron jobs cadastrados
    """
    try:
        count = cron_service.get_job_count()
        return {"total_jobs": count}
    except Exception as e:
        logger.error(f"Erro ao obter contagem de cron jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter contagem de cron jobs: {str(e)}"
        ) 