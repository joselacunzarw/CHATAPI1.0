"""
Configuración Centralizada - UDCito API
=====================================

Este módulo centraliza toda la configuración de la aplicación,
utilizando Pydantic para validación y gestión de variables de entorno.

Author: Jose Lacunza Kobs
Date: Noviembre 2024
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Utiliza variables de entorno y proporciona valores por defecto.
    """
    
    # === Configuración Base ===
    PROJECT_NAME: str = "UDCito API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # === OpenAI y LangChain ===
    OPENAI_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 5000
    
    # === Rutas de Base de Datos ===
    CHROMA_PATH: str = "/app/data/chroma"
    SQLITE_PATH: str = "/app/data/sqlite"
    
    # === Configuración de Recuperación ===
    RETRIEVER_K: int = 10
    
    # === Google OAuth ===
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # === Autorización ===
    ADMIN_EMAILS: List[str] = []
    VALIDATOR_EMAILS: List[str] = []
    AUTHORIZED_DOMAINS: List[str] = []
    
    # === Base de Datos ===
    DB_TYPE: str = "sqlite"
    SQL_ECHO: bool = False
    
    # === JWT ===
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construye la URL de conexión a la base de datos
        
        Returns:
            str: URL de conexión
        """
        if self.DB_TYPE == "sqlite":
            sqlite_db = Path(self.SQLITE_PATH) / "udcito.db"
            return f"sqlite:///{sqlite_db}"
        
        # Para futuras implementaciones de PostgreSQL/MySQL
        return f"{self.DB_TYPE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ADMIN_EMAILS_LIST(self) -> List[str]:
        """Lista de emails administrativos"""
        if isinstance(self.ADMIN_EMAILS, str):
            return [email.strip() for email in self.ADMIN_EMAILS.split(",")]
        return self.ADMIN_EMAILS
    
    @property
    def VALIDATOR_EMAILS_LIST(self) -> List[str]:
        """Lista de emails validadores"""
        if isinstance(self.VALIDATOR_EMAILS, str):
            return [email.strip() for email in self.VALIDATOR_EMAILS.split(",")]
        return self.VALIDATOR_EMAILS
    
    @property
    def AUTHORIZED_DOMAINS_LIST(self) -> List[str]:
        """Lista de dominios autorizados"""
        if isinstance(self.AUTHORIZED_DOMAINS, str):
            return [domain.strip() for domain in self.AUTHORIZED_DOMAINS.split(",")]
        return self.AUTHORIZED_DOMAINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene una instancia cacheada de la configuración
    
    Returns:
        Settings: Instancia de configuración
    """
    return Settings()

# Instancia global de configuración
settings = get_settings()

# Configuración de logging
import logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)