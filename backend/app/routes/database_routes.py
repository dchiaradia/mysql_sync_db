from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any
import logging
from ..services.database_service import DatabaseService
from ..models.table_info import (
    DatabaseSummary, 
    ConnectionStatus, 
    SyncComparison, 
    HealthCheck,
    MigrationResult
)
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/database", tags=["database"])


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Endpoint para verificar a saúde da aplicação"""
    try:
        connections = DatabaseService.test_connections()
        return HealthCheck(
            status="healthy",
            connections=connections,
            version=settings.app_version
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthCheck(
            status="unhealthy",
            connections=ConnectionStatus(source=False, destination=False),
            version=settings.app_version
        )





@router.get("/source/tables", response_model=DatabaseSummary)
async def get_source_tables(sort_by_dependencies: bool = Query(False, description="Ordenar por dependências de foreign keys")):
    """Obtém informações das tabelas do banco de origem"""
    try:
        return DatabaseService.get_source_tables(sort_by_dependencies=sort_by_dependencies)
    except Exception as e:
        logger.error(f"Erro ao obter tabelas do source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter tabelas do banco de origem: {str(e)}"
        )


@router.get("/destination/tables", response_model=DatabaseSummary)
async def get_destination_tables():
    """Obtém informações das tabelas do banco de destino"""
    try:
        return DatabaseService.get_destination_tables()
    except Exception as e:
        logger.error(f"Erro ao obter tabelas do destination: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter tabelas do banco de destino: {str(e)}"
        )


@router.get("/compare", response_model=SyncComparison)
async def compare_databases():
    """Compara os bancos de origem e destino"""
    try:
        return DatabaseService.compare_databases()
    except Exception as e:
        logger.error(f"Erro ao comparar bancos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comparar bancos: {str(e)}"
        )


@router.get("/summary", response_model=Dict[str, Any])
async def get_database_summary():
    """Obtém um resumo completo dos bancos de dados"""
    try:
        source_summary = DatabaseService.get_source_tables()
        destination_summary = DatabaseService.get_destination_tables()
        comparison = DatabaseService.compare_databases()
        
        return {
            "source": source_summary.dict(),
            "destination": destination_summary.dict(),
            "comparison": comparison.dict(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro ao obter resumo dos bancos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo dos bancos: {str(e)}"
        )


@router.post("/migrate/{table_name}", response_model=MigrationResult)
async def migrate_table(
    table_name: str,
    overwrite: bool = Query(False, description="Sobrescrever tabela se existir no destino")
):
    """Migra uma tabela do banco de origem para o banco de destino"""
    try:
        result = DatabaseService.migrate_table(table_name, overwrite)
        return MigrationResult(**result)
    except Exception as e:
        logger.error(f"Erro ao migrar tabela {table_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao migrar tabela {table_name}: {str(e)}"
        )


@router.post("/migrate-batch", response_model=Dict[str, Any])
async def migrate_batch(
    overwrite: bool = Query(False, description="Sobrescrever tabelas se existirem no destino"),
    max_tables: int = Query(10, description="Número máximo de tabelas para migrar")
):
    """Migra múltiplas tabelas na ordem correta de dependências"""
    try:
        # Obtém tabelas ordenadas por dependências
        source_tables = DatabaseService.get_source_tables(sort_by_dependencies=True)
        
        results = []
        migrated_count = 0
        
        for table in source_tables.tables[:max_tables]:
            try:
                result = DatabaseService.migrate_table(table.table_name, overwrite)
                results.append(result)
                migrated_count += 1
                
                if result["success"]:
                    logger.info(f"Tabela {table.table_name} migrada com sucesso")
                else:
                    logger.warning(f"Falha na migração da tabela {table.table_name}: {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                logger.error(f"Erro ao migrar tabela {table.table_name}: {e}")
                results.append({
                    "success": False,
                    "table_name": table.table_name,
                    "error": str(e),
                    "message": f"Erro na migração da tabela {table.table_name}"
                })
        
        return {
            "success": True,
            "total_tables": len(source_tables.tables),
            "migrated_count": migrated_count,
            "max_tables": max_tables,
            "results": results,
            "message": f"Migração em lote concluída: {migrated_count} tabelas processadas"
        }
        
    except Exception as e:
        logger.error(f"Erro na migração em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na migração em lote: {str(e)}"
        ) 