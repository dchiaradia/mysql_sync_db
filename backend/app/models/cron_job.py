from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CronJobStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    REMOVED = "removed"


class CronJobCreate(BaseModel):
    name: str = Field(..., description="Nome do cron job")
    cron_expression: str = Field(..., description="Expressão cron (ex: '0 */6 * * *' para a cada 6 horas)")
    description: Optional[str] = Field(None, description="Descrição do cron job")
    overwrite: bool = Field(False, description="Sobrescrever tabelas se existirem no destino")
    max_tables: int = Field(10, description="Número máximo de tabelas para migrar")


class CronJobResponse(BaseModel):
    id: str
    name: str
    cron_expression: str
    description: Optional[str]
    status: CronJobStatus
    next_run: Optional[datetime]
    created_at: datetime
    last_run: Optional[datetime]
    overwrite: bool
    max_tables: int


class CronJobList(BaseModel):
    jobs: List[CronJobResponse]
    total: int


class CronJobDelete(BaseModel):
    success: bool
    message: str 