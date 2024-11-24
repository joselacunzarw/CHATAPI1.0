"""
Modelos de Base de Datos - UDCito API
====================================

Este módulo define los modelos de SQLAlchemy para la persistencia de datos
relacionados con usuarios y sus actividades. Incluye:

- Modelo de Usuario: Almacena información de usuarios y sus roles
- Modelo de Actividad: Registra acciones y eventos de usuarios
- Enums y constantes relacionadas

Autor: Jose Lacunza Kobs
Fecha: Noviembre 2024
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime
from typing import Dict, Optional

# === Enumeraciones ===
class UserRole(str, Enum):
    """
    Define los roles disponibles en el sistema.
    
    Roles:
        ADMIN: Acceso total al sistema y gestión de usuarios
        VALIDATOR: Puede validar contenido y gestionar ciertos aspectos
        USER: Usuario básico del sistema
    """
    ADMIN = "admin"
    VALIDATOR = "validator"
    USER = "user"

    @classmethod
    def get_permissions(cls, role: str) -> list:
        """
        Retorna los permisos asociados a cada rol
        
        Args:
            role: Rol del usuario
            
        Returns:
            Lista de permisos disponibles para el rol
        """
        PERMISSIONS = {
            cls.ADMIN: ['all'],
            cls.VALIDATOR: ['validate_content', 'view_users', 'edit_content'],
            cls.USER: ['view_content', 'ask_questions']
        }
        return PERMISSIONS.get(role, [])

# === Modelos ===
class User:
    """
    Modelo de Usuario
    
    Almacena la información principal de usuarios incluyendo:
    - Datos de autenticación de Google
    - Información personal básica
    - Metadatos y seguimiento de actividad
    """
    __tablename__ = "users"

    # Campos de identificación
    email = Column(String, primary_key=True, index=True, 
                  comment="Email del usuario (identificador principal)")
    google_id = Column(String, unique=True, index=True, 
                      comment="ID único de Google")
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER,
                 comment="Rol del usuario en el sistema")
    
    # Estado y control
    is_active = Column(Boolean, default=True, 
                      comment="Indica si el usuario está activo")
    
    # Información personal
    given_name = Column(String, comment="Nombre proporcionado por Google")
    family_name = Column(String, comment="Apellido proporcionado por Google")
    full_name = Column(String, comment="Nombre completo")
    picture_url = Column(String, nullable=True, 
                        comment="URL de la imagen de perfil de Google")
    locale = Column(String, nullable=True, 
                   comment="Configuración regional del usuario")
    
    # Campos de auditoría
    created_at = Column(DateTime, server_default=func.now(), 
                       comment="Fecha de creación del usuario")
    updated_at = Column(DateTime, onupdate=func.now(), 
                       comment="Última actualización del registro")
    last_login = Column(DateTime, nullable=True, 
                       comment="Último inicio de sesión exitoso")
    last_seen = Column(DateTime, nullable=True, 
                      comment="Última actividad registrada")
    created_by = Column(String, nullable=True, 
                       comment="Email del admin que creó el usuario")
    
    # Datos adicionales
    metadata = Column(JSON, default=dict, 
                     comment="Información adicional en formato JSON")

    def to_dict(self) -> Dict:
        """
        Convierte el usuario a un diccionario.
        Útil para APIs y caché.
        
        Returns:
            Dict con la información del usuario
        """
        return {
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'name': {
                'given': self.given_name,
                'family': self.family_name,
                'full': self.full_name
            },
            'picture_url': self.picture_url,
            'locale': self.locale,
            'dates': {
                'created': self.created_at.isoformat() if self.created_at else None,
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'last_seen': self.last_seen.isoformat() if self.last_seen else None
            },
            'permissions': UserRole.get_permissions(self.role)
        }

    @classmethod
    def from_google_info(cls, google_info: Dict, role: UserRole = UserRole.USER) -> 'User':
        """
        Crea una instancia de Usuario desde la información de Google.
        
        Args:
            google_info: Información proporcionada por Google OAuth
            role: Rol inicial del usuario
            
        Returns:
            Nueva instancia de User
        """
        return cls(
            email=google_info['email'],
            google_id=google_info['sub'],
            role=role,
            given_name=google_info.get('given_name'),
            family_name=google_info.get('family_name'),
            full_name=google_info.get('name'),
            picture_url=google_info.get('picture'),
            locale=google_info.get('locale'),
            metadata={
                'google_verified_email': google_info.get('email_verified', False),
                'hd': google_info.get('hd'),  # hosted domain
                'creation_context': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'google_oauth'
                }
            }
        )

class UserActivity:
    """
    Modelo para registro de actividades de usuarios
    
    Almacena un historial detallado de acciones realizadas por los usuarios,
    útil para auditoría y seguimiento.
    """
    __tablename__ = "user_activities"

    # Campos principales
    id = Column(String, primary_key=True, 
                comment="Identificador único de la actividad (UUID)")
    user_email = Column(String, index=True, 
                       comment="Email del usuario que realizó la actividad")
    activity_type = Column(String, 
                          comment="Tipo de actividad (login, update_role, etc)")
    timestamp = Column(DateTime, server_default=func.now(), 
                      comment="Momento de la actividad")
    
    # Detalles adicionales
    details = Column(JSON, default=dict, 
                    comment="Información adicional de la actividad")

    def to_dict(self) -> Dict:
        """
        Convierte la actividad a un diccionario
        
        Returns:
            Dict con la información de la actividad
        """
        return {
            'id': self.id,
            'user_email': self.user_email,
            'activity_type': self.activity_type,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }