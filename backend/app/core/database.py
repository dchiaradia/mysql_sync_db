from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Any
import logging
from .config import settings
from .adapters.adapter_factory import DatabaseAdapterFactory

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.source_engine = None
        self.destination_engine = None
        self.source_adapter = None
        self.destination_adapter = None
        self._create_engines()
        self._create_adapters()
    
    def _create_engines(self):
        """Cria as conexões com os bancos de dados source e destination"""
        try:
            # Cria adaptadores para obter URLs de conexão
            temp_source_adapter = DatabaseAdapterFactory.create_adapter(
                settings.database_type, 
                None, 
                settings.source_db
            )
            temp_dest_adapter = DatabaseAdapterFactory.create_adapter(
                settings.database_type, 
                None, 
                settings.destination_db
            )
            
            # Engine para banco de origem
            if hasattr(temp_source_adapter, 'get_connection_url_with_fallback'):
                source_url = temp_source_adapter.get_connection_url_with_fallback(
                    settings.source_user,
                    settings.source_password,
                    settings.source_host,
                    settings.source_port,
                    settings.source_db
                )
            else:
                source_url = temp_source_adapter.get_connection_url(
                    settings.source_user,
                    settings.source_password,
                    settings.source_host,
                    settings.source_port,
                    settings.source_db
                )
            self.source_engine = create_engine(
                source_url,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_timeout=30,
                max_overflow=10,
                echo=settings.debug
            )
            
            # Engine para banco de destino
            if hasattr(temp_dest_adapter, 'get_connection_url_with_fallback'):
                destination_url = temp_dest_adapter.get_connection_url_with_fallback(
                    settings.destination_user,
                    settings.destination_password,
                    settings.destination_host,
                    settings.destination_port,
                    settings.destination_db
                )
            else:
                destination_url = temp_dest_adapter.get_connection_url(
                    settings.destination_user,
                    settings.destination_password,
                    settings.destination_host,
                    settings.destination_port,
                    settings.destination_db
                )
            self.destination_engine = create_engine(
                destination_url,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_timeout=30,
                max_overflow=10,
                echo=settings.debug
            )
            
            logger.info("Conexões com bancos de dados criadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar conexões com bancos de dados: {e}")
            raise
    
    def _create_adapters(self):
        """Cria os adaptadores para os bancos de dados"""
        try:
            self.source_adapter = DatabaseAdapterFactory.create_adapter(
                settings.database_type,
                self.source_engine,
                settings.source_db
            )
            
            self.destination_adapter = DatabaseAdapterFactory.create_adapter(
                settings.database_type,
                self.destination_engine,
                settings.destination_db
            )
            
            logger.info("Adaptadores de banco de dados criados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar adaptadores de banco de dados: {e}")
            raise
    
    def test_connections(self) -> Dict[str, bool]:
        """Testa as conexões com os bancos de dados"""
        results = {"source": False, "destination": False}
        
        try:
            results["source"] = self.source_adapter.test_connection()
            if results["source"]:
                logger.info("Conexão com banco source OK")
        except Exception as e:
            logger.error(f"Erro na conexão com banco source: {e}")
        
        try:
            results["destination"] = self.destination_adapter.test_connection()
            if results["destination"]:
                logger.info("Conexão com banco destination OK")
        except Exception as e:
            logger.error(f"Erro na conexão com banco destination: {e}")
        
        return results
    
    def get_tables_info(self, database_type: str, sort_by_dependencies: bool = False) -> List[Dict]:
        """
        Obtém informações das tabelas do banco especificado
        database_type: 'source' ou 'destination'
        sort_by_dependencies: Se True, ordena por dependências de foreign keys
        """
        if database_type not in ['source', 'destination']:
            raise ValueError("database_type deve ser 'source' ou 'destination'")
        
        adapter = self.source_adapter if database_type == 'source' else self.destination_adapter
        
        try:
            return adapter.get_tables_info(sort_by_dependencies=sort_by_dependencies)
        except Exception as e:
            logger.error(f"Erro ao obter informações das tabelas do banco {database_type}: {e}")
            raise
    
    def get_database_summary(self, database_type: str, sort_by_dependencies: bool = False) -> Dict:
        """
        Obtém um resumo do banco de dados especificado
        sort_by_dependencies: Se True, ordena por dependências de foreign keys
        """
        adapter = self.source_adapter if database_type == 'source' else self.destination_adapter
        
        try:
            return adapter.get_database_summary(sort_by_dependencies=sort_by_dependencies)
        except Exception as e:
            logger.error(f"Erro ao obter resumo do banco {database_type}: {e}")
            raise
    
    def migrate_table(self, table_name: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Migra uma tabela do banco de origem para o banco de destino
        
        Args:
            table_name: Nome da tabela a ser migrada
            overwrite: Se True, sobrescreve a tabela se ela existir no destino
        
        Returns:
            Dict com informações sobre a migração
        """
        try:
            logger.info(f"Iniciando migração da tabela '{table_name}' com overwrite={overwrite}")
            
            # Verifica se a tabela existe no source
            if not self.source_adapter.table_exists(table_name):
                raise ValueError(f"Tabela '{table_name}' não existe no banco de origem")
            
            # Verifica se a tabela existe no destination
            table_exists_dest = self.destination_adapter.table_exists(table_name)
            logger.info(f"Tabela '{table_name}' existe no destino: {table_exists_dest}")
            

            
            # Obtém estrutura da tabela do source (preservando foreign keys)
            structure_info = self.source_adapter.get_table_structure(table_name, remove_foreign_keys=False)
            create_table_sql = structure_info["create_table_sql"]
            
            # Remove tabela do destination se existir e overwrite=True
            if table_exists_dest and overwrite:
                logger.info(f"Removendo tabela existente '{table_name}' do destino (overwrite={overwrite})")
                if not self.destination_adapter.drop_table(table_name):
                    raise Exception(f"Falha ao remover tabela existente '{table_name}' do destino")
                logger.info(f"Tabela '{table_name}' removida com sucesso")
            elif table_exists_dest and not overwrite:
                logger.info(f"Tabela '{table_name}' já existe no destino e overwrite=False")
                raise ValueError(f"Tabela '{table_name}' já existe no banco de destino. Use overwrite=True para sobrescrever")
            
            # Cria tabela no destination
            logger.info(f"Criando tabela '{table_name}' no destino")
            if not self.destination_adapter.create_table(table_name, create_table_sql):
                raise Exception(f"Falha ao criar tabela '{table_name}' no destino")
            
            # Obtém dados da tabela do source
            logger.info(f"Obtendo dados da tabela '{table_name}' do source")
            data = self.source_adapter.get_table_data(table_name)
            
            # Insere dados no destination
            if data:
                logger.info(f"Inserindo {len(data)} registros na tabela '{table_name}' do destino")
                if not self.destination_adapter.insert_data(table_name, data):
                    raise Exception(f"Falha ao inserir dados na tabela '{table_name}' do destino")
            
            logger.info(f"Migração da tabela '{table_name}' concluída com sucesso")
            
            return {
                "success": True,
                "table_name": table_name,
                "records_migrated": len(data),
                "overwritten": table_exists_dest and overwrite,
                "message": f"Tabela '{table_name}' migrada com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro na migração da tabela '{table_name}': {e}")
            return {
                "success": False,
                "table_name": table_name,
                "error": str(e),
                "message": f"Falha na migração da tabela '{table_name}'"
            }


# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager() 