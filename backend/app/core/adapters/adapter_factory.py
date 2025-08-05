import logging
from typing import Dict, Type
from sqlalchemy.engine import Engine
from .base_adapter import DatabaseAdapter
from .mysql_adapter import MySQLAdapter
from .postgresql_adapter import PostgreSQLAdapter

logger = logging.getLogger(__name__)


class DatabaseAdapterFactory:
    """Factory para criar adaptadores de banco de dados"""
    
    _adapters: Dict[str, Type[DatabaseAdapter]] = {
        "mysql": MySQLAdapter,
        "postgresql": PostgreSQLAdapter,
    }
    
    @classmethod
    def create_adapter(cls, database_type: str, engine: Engine, database_name: str) -> DatabaseAdapter:
        """Cria um adaptador para o tipo de banco especificado"""
        adapter_class = cls._adapters.get(database_type.lower())
        
        if not adapter_class:
            supported_types = ", ".join(cls._adapters.keys())
            raise ValueError(f"Tipo de banco '{database_type}' não suportado. Tipos suportados: {supported_types}")
        
        return adapter_class(engine, database_name)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Retorna os tipos de banco suportados"""
        return list(cls._adapters.keys())
    
    @classmethod
    def register_adapter(cls, database_type: str, adapter_class: Type[DatabaseAdapter]):
        """Registra um novo adaptador"""
        cls._adapters[database_type.lower()] = adapter_class 