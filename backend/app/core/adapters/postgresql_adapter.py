from typing import Dict, List, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
from .base_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(DatabaseAdapter):
    """Adaptador específico para PostgreSQL"""
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão PostgreSQL: {e}")
            return False
    
    def get_tables_info(self, sort_by_dependencies: bool = False) -> List[Dict[str, Any]]:
        """Obtém informações das tabelas do PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                # Query específica do PostgreSQL para obter informações das tabelas
                query = """
                SELECT 
                    t.table_name,
                    ROUND(
                        (pg_total_relation_size(c.oid) / 1024.0 / 1024.0), 2
                    ) as size_mb,
                    pg_relation_size(c.oid) as data_length,
                    (pg_total_relation_size(c.oid) - pg_relation_size(c.oid)) as index_length
                FROM information_schema.tables t
                LEFT JOIN pg_class c ON c.relname = t.table_name
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE t.table_schema = 'public'
                AND t.table_type = 'BASE TABLE'
                AND n.nspname = :database_name
                ORDER BY t.table_name
                """
                
                result = conn.execute(text(query), {"database_name": self.database_name})
                
                tables_info = []
                for row in result:
                    # Obtém a contagem exata de registros para cada tabela
                    count_query = f"SELECT COUNT(*) as row_count FROM \"{row.table_name}\""
                    count_result = conn.execute(text(count_query))
                    exact_row_count = count_result.fetchone()[0]
                    
                    tables_info.append({
                        "table_name": row.table_name,
                        "row_count": exact_row_count,
                        "size_mb": float(row.size_mb or 0),
                        "data_length": row.data_length or 0,
                        "index_length": row.index_length or 0
                    })
                
                return tables_info
                
        except Exception as e:
            logger.error(f"Erro ao obter informações das tabelas PostgreSQL: {e}")
            raise
    
    def get_database_summary(self, sort_by_dependencies: bool = False) -> Dict[str, Any]:
        """Obtém um resumo do banco PostgreSQL"""
        tables_info = self.get_tables_info()
        
        total_tables = len(tables_info)
        total_rows = sum(table['row_count'] for table in tables_info)
        total_size_mb = sum(table['size_mb'] for table in tables_info)
        
        return {
            "database_type": "postgresql",
            "database_name": self.database_name,
            "total_tables": total_tables,
            "total_rows": total_rows,
            "total_size_mb": round(total_size_mb, 2),
            "tables": tables_info
        }
    
    def get_connection_url(self, user: str, password: str, host: str, port: int, database: str) -> str:
        """Retorna a URL de conexão PostgreSQL"""
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def get_table_structure(self, table_name: str, remove_foreign_keys: bool = False) -> Dict[str, Any]:
        """Obtém a estrutura da tabela PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                # Obtém o CREATE TABLE (simulado)
                query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND table_schema = 'public'
                ORDER BY ordinal_position
                """
                
                result = conn.execute(text(query), {"table_name": table_name})
                columns = []
                for row in result:
                    columns.append({
                        "column_name": row[0],
                        "data_type": row[1],
                        "is_nullable": row[2],
                        "column_default": row[3],
                        "character_maximum_length": row[4]
                    })
                
                if not columns:
                    raise ValueError(f"Tabela '{table_name}' não encontrada")
                
                # Constrói CREATE TABLE SQL
                create_table_sql = f"CREATE TABLE {table_name} (\n"
                column_definitions = []
                for col in columns:
                    col_def = f"    {col['column_name']} {col['data_type']}"
                    if col['is_nullable'] == 'NO':
                        col_def += " NOT NULL"
                    if col['column_default']:
                        col_def += f" DEFAULT {col['column_default']}"
                    column_definitions.append(col_def)
                
                create_table_sql += ",\n".join(column_definitions)
                create_table_sql += "\n);"
                
                return {
                    "table_name": table_name,
                    "create_table_sql": create_table_sql,
                    "columns": columns
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estrutura da tabela PostgreSQL {table_name}: {e}")
            raise
    
    def get_table_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém os dados da tabela PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                # Obtém nomes das colunas
                columns_result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = 'public' ORDER BY ordinal_position"))
                columns = [col[0] for col in columns_result]
                
                # Constrói query com LIMIT se especificado
                query = f"SELECT * FROM {table_name}"
                if limit:
                    query += f" LIMIT {limit}"
                
                result = conn.execute(text(query))
                
                data = []
                for row in result:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    data.append(row_dict)
                
                return data
                
        except Exception as e:
            logger.error(f"Erro ao obter dados da tabela PostgreSQL {table_name}: {e}")
            raise
    
    def create_table(self, table_name: str, structure_sql: str) -> bool:
        """Cria uma tabela no banco PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(structure_sql))
                conn.commit()
                logger.info(f"Tabela '{table_name}' criada com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela PostgreSQL {table_name}: {e}")
            return False
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insere dados na tabela PostgreSQL"""
        if not data:
            return True
        
        try:
            with self.engine.connect() as conn:
                # Obtém nomes das colunas do primeiro registro
                columns = list(data[0].keys())
                
                # Constrói query de INSERT
                placeholders = ", ".join([f":{col}" for col in columns])
                columns_str = ", ".join([f'"{col}"' for col in columns])
                query = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
                
                # Executa INSERT em lotes
                batch_size = 1000
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    conn.execute(text(query), batch)
                
                conn.commit()
                logger.info(f"{len(data)} registros inseridos na tabela '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao inserir dados na tabela PostgreSQL {table_name}: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica se a tabela existe no PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table AND table_schema = 'public'"),
                    {"table": table_name}
                )
                count = result.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Erro ao verificar existência da tabela PostgreSQL {table_name}: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """Remove a tabela se existir no PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.commit()
                logger.info(f"Tabela '{table_name}' removida com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao remover tabela PostgreSQL {table_name}: {e}")
            return False 