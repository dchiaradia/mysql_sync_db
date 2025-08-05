from typing import Dict, List, Any
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
import logging
from .base_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class MySQLAdapter(DatabaseAdapter):
    """Adaptador específico para MySQL"""
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco MySQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão MySQL: {e}")
            return False
    
    def get_tables_info(self, sort_by_dependencies: bool = False) -> List[Dict[str, Any]]:
        """Obtém informações das tabelas do MySQL"""
        try:
            with self.engine.connect() as conn:
                # Query específica do MySQL para obter informações das tabelas
                query = """
                SELECT 
                    t.TABLE_NAME as table_name,
                    ROUND(((t.DATA_LENGTH + t.INDEX_LENGTH) / 1024 / 1024), 2) as size_mb,
                    t.DATA_LENGTH as data_length,
                    t.INDEX_LENGTH as index_length
                FROM information_schema.TABLES t
                WHERE t.TABLE_SCHEMA = :database_name
                ORDER BY t.TABLE_NAME
                """
                
                result = conn.execute(text(query), {"database_name": self.database_name})
                
                tables_info = []
                for row in result:
                    # Obtém a contagem exata de registros para cada tabela
                    count_query = f"SELECT COUNT(*) as row_count FROM `{row.table_name}`"
                    count_result = conn.execute(text(count_query))
                    exact_row_count = count_result.fetchone()[0]
                    
                    tables_info.append({
                        "table_name": row.table_name,
                        "row_count": exact_row_count,
                        "size_mb": float(row.size_mb or 0),
                        "data_length": row.data_length or 0,
                        "index_length": row.index_length or 0
                    })
                
                # Se solicitado, ordena por dependências
                if sort_by_dependencies:
                    tables_info = self._sort_tables_by_dependencies(tables_info)
                
                return tables_info
                
        except Exception as e:
            logger.error(f"Erro ao obter informações das tabelas MySQL: {e}")
            raise
    
    def get_database_summary(self, sort_by_dependencies: bool = False) -> Dict[str, Any]:
        """Obtém um resumo do banco MySQL"""
        tables_info = self.get_tables_info(sort_by_dependencies=sort_by_dependencies)
        
        total_tables = len(tables_info)
        total_rows = sum(table['row_count'] for table in tables_info)
        total_size_mb = sum(table['size_mb'] for table in tables_info)
        
        return {
            "database_type": "mysql",
            "database_name": self.database_name,
            "total_tables": total_tables,
            "total_rows": total_rows,
            "total_size_mb": round(total_size_mb, 2),
            "tables": tables_info
        }
    
    def get_connection_url(self, user: str, password: str, host: str, port: int, database: str) -> str:
        """Retorna a URL de conexão MySQL"""
        # Usa charset mais compatível para bancos reais
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8&autocommit=true"
    
    def get_connection_url_with_fallback(self, user: str, password: str, host: str, port: int, database: str) -> str:
        """Retorna a URL de conexão MySQL com fallback de charset"""
        # Lista de charsets para tentar em ordem de preferência
        charsets = ['utf8', 'utf8mb4', 'latin1']
        
        for charset in charsets:
            try:
                url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}&autocommit=true"
                # Testa a conexão
                test_engine = create_engine(url, pool_pre_ping=True, echo=False)
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info(f"Charset {charset} funcionou para {host}:{port}/{database}")
                return url
            except Exception as e:
                logger.warning(f"Charset {charset} falhou para {host}:{port}/{database}: {e}")
                continue
        
        # Se nenhum charset funcionar, usa utf8 como padrão
        logger.warning(f"Usando charset utf8 como fallback para {host}:{port}/{database}")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8&autocommit=true"
    
    def get_table_structure(self, table_name: str, remove_foreign_keys: bool = True) -> Dict[str, Any]:
        """Obtém a estrutura da tabela MySQL (SHOW CREATE TABLE)"""
        try:
            with self.engine.connect() as conn:
                # Obtém o CREATE TABLE
                result = conn.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
                row = result.fetchone()
                
                if not row:
                    raise ValueError(f"Tabela '{table_name}' não encontrada")
                
                create_table_sql = row[1]
                
                # Remove foreign keys se solicitado
                if remove_foreign_keys:
                    create_table_sql = self._remove_foreign_keys(create_table_sql)
                
                # Obtém informações das colunas
                columns_result = conn.execute(text(f"DESCRIBE `{table_name}`"))
                columns = []
                for col_row in columns_result:
                    columns.append({
                        "field": col_row[0],
                        "type": col_row[1],
                        "null": col_row[2],
                        "key": col_row[3],
                        "default": col_row[4],
                        "extra": col_row[5]
                    })
                
                return {
                    "table_name": table_name,
                    "create_table_sql": create_table_sql,
                    "columns": columns
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estrutura da tabela MySQL {table_name}: {e}")
            raise
    
    def _remove_foreign_keys(self, create_table_sql: str) -> str:
        """Remove foreign keys do CREATE TABLE SQL"""
        import re
        
        # Remove CONSTRAINT FOREIGN KEY
        # Padrão: CONSTRAINT `nome_constraint` FOREIGN KEY (`coluna`) REFERENCES `tabela` (`coluna`)
        pattern = r',\s*CONSTRAINT\s+`[^`]+`\s+FOREIGN\s+KEY\s*\([^)]+\)\s+REFERENCES\s+`[^`]+`\s*\([^)]+\)\s*(?:ON\s+DELETE\s+[^,]+)?\s*(?:ON\s+UPDATE\s+[^,]+)?'
        create_table_sql = re.sub(pattern, '', create_table_sql, flags=re.IGNORECASE)
        
        # Remove KEY que são foreign keys
        # Padrão: KEY `fk_nome_idx` (`coluna`)
        pattern2 = r',\s*KEY\s+`fk_[^`]+`\s*\([^)]+\)'
        create_table_sql = re.sub(pattern2, '', create_table_sql, flags=re.IGNORECASE)
        
        # Limpa vírgulas duplas que podem ter ficado
        create_table_sql = re.sub(r',\s*,', ',', create_table_sql)
        create_table_sql = re.sub(r',\s*\)', ')', create_table_sql)
        
        # Garante que o charset seja compatível
        create_table_sql = re.sub(r'DEFAULT\s+CHARSET=\w+', 'DEFAULT CHARSET=utf8', create_table_sql, flags=re.IGNORECASE)
        
        # Garante que o engine seja compatível
        create_table_sql = re.sub(r'ENGINE=\w+', 'ENGINE=InnoDB', create_table_sql, flags=re.IGNORECASE)
        
        # Garante que a tabela tenha a definição completa
        if not re.search(r'ENGINE=\w+', create_table_sql, re.IGNORECASE):
            # Adiciona após o fechamento dos parênteses
            create_table_sql = create_table_sql.rstrip() + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        else:
            # Se já tem ENGINE, garante que está fora dos parênteses
            create_table_sql = re.sub(r'\)\s*ENGINE=', ') ENGINE=', create_table_sql, flags=re.IGNORECASE)
        
        logger.info("Foreign keys removidas e charset/engine ajustados do CREATE TABLE")
        return create_table_sql
    
    def _get_table_dependencies(self, table_name: str) -> List[str]:
        """Obtém as dependências (foreign keys) de uma tabela"""
        try:
            with self.engine.connect() as conn:
                query = """
                SELECT 
                    REFERENCED_TABLE_NAME
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = :database_name 
                AND TABLE_NAME = :table_name 
                AND REFERENCED_TABLE_NAME IS NOT NULL
                """
                
                result = conn.execute(text(query), {
                    "database_name": self.database_name,
                    "table_name": table_name
                })
                
                dependencies = []
                for row in result:
                    if row[0] and row[0] not in dependencies:
                        dependencies.append(row[0])
                
                return dependencies
                
        except Exception as e:
            logger.error(f"Erro ao obter dependências da tabela {table_name}: {e}")
            return []
    
    def _sort_tables_by_dependencies(self, tables_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordena tabelas por dependências usando topological sort"""
        try:
            # Cria grafo de dependências
            dependencies = {}
            table_names = [table['table_name'] for table in tables_info]
            
            for table_name in table_names:
                deps = self._get_table_dependencies(table_name)
                dependencies[table_name] = deps
            
            # Topological sort
            sorted_tables = []
            visited = set()
            temp_visited = set()
            
            def visit(table_name):
                if table_name in temp_visited:
                    # Ciclo detectado - retorna tabelas em ordem alfabética
                    logger.warning(f"Ciclo de dependências detectado para {table_name}")
                    return sorted(table_names)
                
                if table_name in visited:
                    return
                
                temp_visited.add(table_name)
                
                # Visita dependências primeiro
                for dep in dependencies.get(table_name, []):
                    if dep in table_names:  # Só considera dependências que existem
                        visit(dep)
                
                temp_visited.remove(table_name)
                visited.add(table_name)
                sorted_tables.append(table_name)
            
            # Visita todas as tabelas
            for table_name in table_names:
                if table_name not in visited:
                    visit(table_name)
            
            # Reorganiza tables_info na ordem ordenada
            table_dict = {table['table_name']: table for table in tables_info}
            ordered_tables = []
            
            for table_name in sorted_tables:
                if table_name in table_dict:
                    ordered_tables.append(table_dict[table_name])
            
            # Adiciona tabelas que não foram processadas (se houver)
            for table in tables_info:
                if table['table_name'] not in sorted_tables:
                    ordered_tables.append(table)
            
            logger.info(f"Tabelas ordenadas por dependências: {len(ordered_tables)} tabelas")
            return ordered_tables
            
        except Exception as e:
            logger.error(f"Erro ao ordenar tabelas por dependências: {e}")
            # Em caso de erro, retorna ordem alfabética
            return sorted(tables_info, key=lambda x: x['table_name'])
    
    def get_table_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém os dados da tabela MySQL"""
        try:
            with self.engine.connect() as conn:
                # Obtém nomes das colunas
                columns_result = conn.execute(text(f"SHOW COLUMNS FROM `{table_name}`"))
                columns = [col[0] for col in columns_result]
                
                # Constrói query com LIMIT se especificado
                query = f"SELECT * FROM `{table_name}`"
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
            logger.error(f"Erro ao obter dados da tabela MySQL {table_name}: {e}")
            raise
    
    def create_table(self, table_name: str, structure_sql: str) -> bool:
        """Cria uma tabela no banco MySQL"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(structure_sql))
                conn.commit()
                logger.info(f"Tabela '{table_name}' criada com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela MySQL {table_name}: {e}")
            return False
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insere dados na tabela MySQL"""
        if not data:
            return True
        
        try:
            with self.engine.connect() as conn:
                # Obtém nomes das colunas do primeiro registro
                columns = list(data[0].keys())
                
                # Constrói query de INSERT
                placeholders = ", ".join([f":{col}" for col in columns])
                columns_str = ", ".join([f"`{col}`" for col in columns])
                query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
                
                # Executa INSERT em lotes
                batch_size = 1000
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    conn.execute(text(query), batch)
                
                conn.commit()
                logger.info(f"{len(data)} registros inseridos na tabela '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao inserir dados na tabela MySQL {table_name}: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica se a tabela existe no MySQL"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :db AND table_name = :table"),
                    {"db": self.database_name, "table": table_name}
                )
                count = result.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Erro ao verificar existência da tabela MySQL {table_name}: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """Remove a tabela se existir no MySQL"""
        try:
            with self.engine.connect() as conn:
                # Desabilita foreign key checks temporariamente
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                # Reabilita foreign key checks
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                conn.commit()
                logger.info(f"Tabela '{table_name}' removida com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao remover tabela MySQL {table_name}: {e}")
            return False 