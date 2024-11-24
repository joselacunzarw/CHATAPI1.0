"""
Configuración de Base de Datos - UDCito API
=========================================

Este módulo maneja la configuración y conexión a la base de datos.
Soporta múltiples backends (SQLite, PostgreSQL, MySQL) y proporciona
utilidades para la gestión de conexiones y sesiones.

Características:
- Configuración basada en variables de entorno
- Soporte para múltiples tipos de base de datos
- Manejo seguro de conexiones con context managers
- Sistema de migraciones integrado
- Logging detallado

Autor: Jose Lacunza
Fecha: Noviembre 2024
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import os
from pathlib import Path
import logging
from typing import Generator, Optional

# Configuración de logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de conexiones y configuración de base de datos.
    
    Proporciona una interfaz unificada para:
    - Configuración de conexiones
    - Gestión de sesiones
    - Utilidades de base de datos
    """
    
    def __init__(self):
        """Inicializa el gestor de base de datos"""
        self._engine: Optional[Engine] = None
        self._SessionLocal = None
        self._connect_args = {}
        self.setup_database()
        
    def setup_database(self):
        """
        Configura la conexión a la base de datos según variables de entorno.
        
        Variables de entorno utilizadas:
        - DB_TYPE: Tipo de base de datos ('sqlite', 'postgresql', 'mysql')
        - DB_HOST: Host de la base de datos
        - DB_PORT: Puerto de la base de datos
        - DB_USER: Usuario
        - DB_PASSWORD: Contraseña
        - DB_NAME: Nombre de la base de datos
        - SQLITE_PATH: Ruta para archivo SQLite
        """
        try:
            db_type = os.getenv('DB_TYPE', 'sqlite').lower()
            
            if db_type == 'sqlite':
                db_url = self._setup_sqlite()
            else:
                db_url = self._setup_sql_database(db_type)
                
            self._create_engine(db_url)
            logger.info(f"Base de datos configurada exitosamente: {db_type}")
            
        except Exception as e:
            logger.error(f"Error configurando base de datos: {str(e)}")
            raise

    def _setup_sqlite(self) -> str:
        """
        Configura base de datos SQLite
        
        Returns:
            URL de conexión para SQLite
        """
        # Configurar ruta de SQLite
        db_path = Path(os.getenv('SQLITE_PATH', './data/sqlite'))
        db_path.mkdir(parents=True, exist_ok=True)
        
        db_file = db_path / 'udcito.db'
        self._connect_args = {"check_same_thread": False}
        
        # Configurar eventos específicos de SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Configura opciones de SQLite para mejor performance"""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
            
        return f"sqlite:///{db_file}"

    def _setup_sql_database(self, db_type: str) -> str:
        """
        Configura base de datos SQL (PostgreSQL/MySQL)
        
        Args:
            db_type: Tipo de base de datos ('postgresql' o 'mysql')
            
        Returns:
            URL de conexión para la base de datos
        """
        # Obtener configuración
        db_user = os.getenv('DB_USER', 'udcito')
        db_pass = os.getenv('DB_PASSWORD', 'udcito')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'udcito')
        
        return f"{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    def _create_engine(self, db_url: str):
        """
        Crea el engine de SQLAlchemy con la configuración apropiada
        
        Args:
            db_url: URL de conexión a la base de datos
        """
        self._engine = create_engine(
            db_url,
            connect_args=self._connect_args,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=os.getenv('SQL_ECHO', '').lower() == 'true'
        )
        
        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """
        Context manager para obtener una sesión de base de datos.
        
        Yields:
            Sesión de SQLAlchemy
            
        Example:
            ```python
            with db_manager.get_db() as db:
                users = db.query(User).all()
            ```
        """
        if not self._SessionLocal:
            raise RuntimeError("Base de datos no inicializada")
            
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_engine(self) -> Engine:
        """
        Obtiene el engine de SQLAlchemy
        
        Returns:
            SQLAlchemy Engine
        """
        if not self._engine:
            raise RuntimeError("Engine de base de datos no inicializado")
        return self._engine

    def check_connection(self) -> bool:
        """
        Verifica la conexión a la base de datos
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            with self.get_db() as db:
                db.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Error verificando conexión: {str(e)}")
            return False

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de utilidad para acceso fácil
def get_db() -> Generator[Session, None, None]:
    """
    Utilidad para obtener una sesión de base de datos.
    Para uso con FastAPI Depends.
    
    Example:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    """
    with db_manager.get_db() as db:
        yield db