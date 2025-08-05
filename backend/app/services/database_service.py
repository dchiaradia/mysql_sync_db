from typing import Dict, List, Optional, Any
import logging
from ..core.database import db_manager
from ..models.table_info import DatabaseSummary, ConnectionStatus, SyncComparison

logger = logging.getLogger(__name__)


class DatabaseService:
    """Serviço para operações de banco de dados"""
    
    @staticmethod
    def test_connections() -> ConnectionStatus:
        """Testa as conexões com os bancos de dados"""
        try:
            results = db_manager.test_connections()
            return ConnectionStatus(**results)
        except Exception as e:
            logger.error(f"Erro ao testar conexões: {e}")
            raise
    
    @staticmethod
    def get_source_tables(sort_by_dependencies: bool = False) -> DatabaseSummary:
        """Obtém informações das tabelas do banco de origem"""
        try:
            summary = db_manager.get_database_summary('source', sort_by_dependencies=sort_by_dependencies)
            return DatabaseSummary(**summary)
        except Exception as e:
            logger.error(f"Erro ao obter tabelas do banco source: {e}")
            raise
    
    @staticmethod
    def get_destination_tables(sort_by_dependencies: bool = False) -> DatabaseSummary:
        """Obtém informações das tabelas do banco de destino"""
        try:
            summary = db_manager.get_database_summary('destination', sort_by_dependencies=sort_by_dependencies)
            return DatabaseSummary(**summary)
        except Exception as e:
            logger.error(f"Erro ao obter tabelas do banco destination: {e}")
            raise
    
    @staticmethod
    def compare_databases() -> SyncComparison:
        """Compara os bancos de origem e destino"""
        try:
            source_summary = DatabaseService.get_source_tables()
            destination_summary = DatabaseService.get_destination_tables()
            
            # Encontra diferenças entre os bancos
            differences = DatabaseService._find_differences(source_summary, destination_summary)
            
            return SyncComparison(
                source_summary=source_summary,
                destination_summary=destination_summary,
                differences=differences
            )
        except Exception as e:
            logger.error(f"Erro ao comparar bancos: {e}")
            raise
    
    @staticmethod
    def _find_differences(source: DatabaseSummary, destination: DatabaseSummary) -> List[Dict]:
        """Encontra diferenças entre os bancos source e destination"""
        differences = []
        
        # Cria dicionários para facilitar a busca
        source_tables = {table.table_name: table for table in source.tables}
        destination_tables = {table.table_name: table for table in destination.tables}
        
        # Tabelas que existem apenas no source
        for table_name in source_tables:
            if table_name not in destination_tables:
                differences.append({
                    "type": "missing_in_destination",
                    "table_name": table_name,
                    "source_info": source_tables[table_name].dict(),
                    "destination_info": None
                })
        
        # Tabelas que existem apenas no destination
        for table_name in destination_tables:
            if table_name not in source_tables:
                differences.append({
                    "type": "missing_in_source",
                    "table_name": table_name,
                    "source_info": None,
                    "destination_info": destination_tables[table_name].dict()
                })
        
        # Tabelas que existem em ambos, mas com diferenças
        for table_name in source_tables:
            if table_name in destination_tables:
                source_table = source_tables[table_name]
                dest_table = destination_tables[table_name]
                
                if (source_table.row_count != dest_table.row_count or
                    abs(source_table.size_mb - dest_table.size_mb) > 0.01):
                    differences.append({
                        "type": "different_data",
                        "table_name": table_name,
                        "source_info": source_table.dict(),
                        "destination_info": dest_table.dict(),
                        "row_count_diff": source_table.row_count - dest_table.row_count,
                        "size_diff_mb": round(source_table.size_mb - dest_table.size_mb, 2)
                    })
        
        return differences
    
    @staticmethod
    def migrate_table(table_name: str, overwrite: bool = False) -> Dict[str, Any]:
        """Migra uma tabela do banco de origem para o banco de destino"""
        try:
            result = db_manager.migrate_table(table_name, overwrite)
            return result
        except Exception as e:
            logger.error(f"Erro ao migrar tabela {table_name}: {e}")
            raise 