from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Tipo de banco de dados
    database_type: str = "mysql"
    
    # Configurações do Banco Source
    source_user: str = "root"
    source_password: str = "password"
    source_db: str = "source_db"
    source_host: str = "mysql_source"
    source_port: int = 3306
    
    # Configurações do Banco Destination
    destination_user: str = "root"
    destination_password: str = "password"
    destination_db: str = "destination_db"
    destination_host: str = "mysql_destination"
    destination_port: int = 3306
    
    # Configurações da aplicação
    debug: bool = True
    app_name: str = "Database Sync API"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 