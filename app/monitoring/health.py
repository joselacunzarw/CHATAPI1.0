"""
Módulo de Health Check para UDCito con logging detallado
"""

import os
import psutil
import time
import logging
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field

# === Configuración de Logging ===
logger = logging.getLogger("health_check")
logger.setLevel(logging.INFO)

# === Modelos de Datos ===
class SystemCheck(BaseModel):
    """Estado detallado del sistema"""
    status: str = Field(..., description="Estado de este componente")
    cpu_percent: float = Field(..., description="Uso de CPU")
    memory_used_percent: float = Field(..., description="Uso de memoria")
    disk_used_percent: float = Field(..., description="Uso de disco")
    disk_free_gb: float = Field(..., description="Espacio libre en disco (GB)")
    uptime_hours: float = Field(..., description="Tiempo de actividad en horas")
    details: Dict = Field(..., description="Detalles adicionales")

class DatabaseCheck(BaseModel):
    """Estado detallado de la base de datos"""
    status: str = Field(..., description="Estado de este componente")
    chroma_path: str = Field(..., description="Ruta de ChromaDB")
    path_exists: bool = Field(..., description="¿Existe la ruta?")
    path_writable: bool = Field(..., description="¿Se puede escribir?")
    details: Dict = Field(..., description="Detalles adicionales")

class APICheck(BaseModel):
    """Estado de la API"""
    status: str = Field(..., description="Estado de este componente")
    endpoint_count: int = Field(..., description="Número de endpoints")
    active_connections: int = Field(..., description="Conexiones activas")
    details: Dict = Field(..., description="Detalles adicionales")

class HealthResponse(BaseModel):
    """Respuesta detallada del health check"""
    overall_status: str = Field(..., description="Estado general del sistema")
    timestamp: datetime = Field(default_factory=datetime.now)
    checks: Dict[str, Dict] = Field(..., description="Resultados de cada verificación")
    environment: str = Field(..., description="Ambiente de ejecución")
    version: str = Field(..., description="Versión de la API")

class HealthChecker:
    """Clase para realizar verificaciones detalladas del sistema"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self._last_check = None
        self._check_interval = 30
        logger.info(f"🚀 Iniciando HealthChecker v{self.version} en ambiente {self.environment}")

    def _check_system(self) -> SystemCheck:
        """Verifica el estado del sistema"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            uptime = time.time() - psutil.boot_time()
            
            details = {
                "total_memory_gb": round(memory.total / (1024**3), 2),
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "total_disk_gb": round(disk.total / (1024**3), 2),
                "cpu_count": psutil.cpu_count()
            }
            
            status = "healthy"
            if cpu > 80 or memory.percent > 80 or disk.percent > 80:
                status = "degraded"
            if cpu > 90 or memory.percent > 90 or disk.percent > 90:
                status = "critical"

            logger.info(f"💻 Sistema - Estado: {status}")
            logger.info(f"   CPU: {cpu}% | Memoria: {memory.percent}% | Disco: {disk.percent}%")
            
            return SystemCheck(
                status=status,
                cpu_percent=cpu,
                memory_used_percent=memory.percent,
                disk_used_percent=disk.percent,
                disk_free_gb=round(disk.free / (1024**3), 2),
                uptime_hours=round(uptime / 3600, 2),
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Error en verificación del sistema: {str(e)}")
            return SystemCheck(
                status="error",
                cpu_percent=0,
                memory_used_percent=0,
                disk_used_percent=0,
                disk_free_gb=0,
                uptime_hours=0,
                details={"error": str(e)}
            )

    def _check_database(self) -> DatabaseCheck:
        """Verifica el estado de la base de datos"""
        try:
            chroma_path = os.getenv('CHROMA_PATH', '/app/data/chroma')
            path_exists = os.path.exists(chroma_path)
            path_writable = os.access(chroma_path, os.W_OK) if path_exists else False
            
            details = {
                "path_readable": os.access(chroma_path, os.R_OK) if path_exists else False,
                "is_directory": os.path.isdir(chroma_path) if path_exists else False,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(chroma_path)).isoformat() if path_exists else None
            }
            
            status = "healthy"
            if not path_exists:
                status = "critical"
            elif not path_writable:
                status = "degraded"

            logger.info(f"📁 Base de Datos - Estado: {status}")
            logger.info(f"   Ruta: {chroma_path}")
            logger.info(f"   Accesible: {path_exists} | Escribible: {path_writable}")
            
            return DatabaseCheck(
                status=status,
                chroma_path=chroma_path,
                path_exists=path_exists,
                path_writable=path_writable,
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Error en verificación de base de datos: {str(e)}")
            return DatabaseCheck(
                status="error",
                chroma_path="unknown",
                path_exists=False,
                path_writable=False,
                details={"error": str(e)}
            )

    def _check_api(self) -> APICheck:
        """Verifica el estado de la API"""
        try:
            details = {
                "startup_time": datetime.now().isoformat(),
                "debug_mode": os.getenv("DEBUG", "False") == "True",
                "workers": int(os.getenv("WORKERS", 4))
            }
            
            logger.info(f"🌐 API - Estado: healthy")
            logger.info(f"   Workers: {details['workers']} | Debug: {details['debug_mode']}")
            
            return APICheck(
                status="healthy",
                endpoint_count=4,
                active_connections=0,
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Error en verificación de API: {str(e)}")
            return APICheck(
                status="error",
                endpoint_count=0,
                active_connections=0,
                details={"error": str(e)}
            )

    async def check_health(self) -> HealthResponse:
        """Realiza una verificación completa del sistema"""
        logger.info("\n🔍 Iniciando verificación de salud del sistema")
        
        checks = {
            "system": self._check_system(),
            "database": self._check_database(),
            "api": self._check_api()
        }
        
        checks_dict = {
            name: check.dict() 
            for name, check in checks.items()
        }
        
        overall_status = "healthy"
        if any(check.status == "critical" for check in checks.values()):
            overall_status = "unhealthy"
        elif any(check.status == "degraded" for check in checks.values()):
            overall_status = "degraded"

        logger.info(f"\n✨ Resultado Final: {overall_status}")
        
        return HealthResponse(
            overall_status=overall_status,
            checks=checks_dict,
            environment=self.environment,
            version=self.version
        )

# Instancia global del health checker
health_checker = HealthChecker()