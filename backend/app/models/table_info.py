from pydantic import BaseModel
from typing import List, Optional


class TableInfo(BaseModel):
    """Modelo para informações de uma tabela"""
    table_name: str
    row_count: int
    size_mb: float
    data_length: int
    index_length: int


class DatabaseSummary(BaseModel):
    """Modelo para resumo de um banco de dados"""
    database_type: str
    database_name: str
    total_tables: int
    total_rows: int
    total_size_mb: float
    tables: List[TableInfo]


class ConnectionStatus(BaseModel):
    """Modelo para status das conexões"""
    source: bool
    destination: bool


class SyncComparison(BaseModel):
    """Modelo para comparação entre bancos source e destination"""
    source_summary: DatabaseSummary
    destination_summary: DatabaseSummary
    differences: List[dict]


class HealthCheck(BaseModel):
    """Modelo para health check da aplicação"""
    status: str
    connections: ConnectionStatus
    version: str


class MigrationResult(BaseModel):
    """Modelo para resultado de migração"""
    success: bool
    table_name: str
    records_migrated: int = 0
    overwritten: bool = False
    error: Optional[str] = None
    message: str 