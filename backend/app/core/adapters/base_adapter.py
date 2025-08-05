from abc import ABC, abstractmethod
from typing import Dict, List, Any
from sqlalchemy.engine import Engine


class DatabaseAdapter(ABC):
    """Interface base para adaptadores de banco de dados"""
    
    def __init__(self, engine: Engine, database_name: str):
        self.engine = engine
        self.database_name = database_name
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        pass
    
    @abstractmethod
    def get_tables_info(self, sort_by_dependencies: bool = False) -> List[Dict[str, Any]]:
        """Obtém informações das tabelas do banco"""
        pass
    
    @abstractmethod
    def get_database_summary(self, sort_by_dependencies: bool = False) -> Dict[str, Any]:
        """Obtém um resumo do banco de dados"""
        pass
    
    @abstractmethod
    def get_connection_url(self, user: str, password: str, host: str, port: int, database: str) -> str:
        """Retorna a URL de conexão específica do banco"""
        pass
    
    @abstractmethod
    def get_table_structure(self, table_name: str, remove_foreign_keys: bool = False) -> Dict[str, Any]:
        """Obtém a estrutura da tabela (CREATE TABLE)"""
        pass
    
    @abstractmethod
    def get_table_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém os dados da tabela"""
        pass
    
    @abstractmethod
    def create_table(self, table_name: str, structure_sql: str) -> bool:
        """Cria uma tabela no banco de destino"""
        pass
    
    @abstractmethod
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insere dados na tabela"""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Verifica se a tabela existe"""
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> bool:
        """Remove a tabela se existir"""
        pass 