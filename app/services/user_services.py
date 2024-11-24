"""
Servicio de Gestión de Usuarios - UDCito API
==========================================

Este módulo implementa la lógica de negocio para la gestión de usuarios,
incluyendo creación, actualización, autenticación y autorización.

Características:
- Gestión de usuarios con Google OAuth
- Sistema de roles y permisos
- Registro de actividad de usuarios
- Caché de datos frecuentes

Autor: Jose Lacunza Kobs
Fecha: Noviembre 2024
"""

from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List
from uuid import uuid4
from google.oauth2 import id_token
from google.auth.transport import requests

from app.db.models import User, UserActivity, UserRole
from app.db.database import db_manager
from app.config import settings

# Configuración de logging
logger = logging.getLogger(__name__)

class UserService:
    """
    Servicio principal para la gestión de usuarios.
    Implementa toda la lógica de negocio relacionada con usuarios.
    """
    
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
    
    async def verify_google_token(self, token: str) -> Dict:
        """
        Verifica la validez de un token de Google y extrae la información.
        
        Args:
            token: Token ID de Google
            
        Returns:
            Dict con la información del usuario verificada
            
        Raises:
            ValueError: Si el token es inválido
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Emisor del token no válido')
                
            return idinfo
            
        except Exception as e:
            logger.error(f"Error verificando token de Google: {str(e)}")
            raise ValueError("Token inválido o expirado")

    async def get_or_create_user(self, google_info: Dict) -> User:
        """
        Obtiene un usuario existente o crea uno nuevo basado en la info de Google.
        
        Args:
            google_info: Información del usuario de Google
            
        Returns:
            User: Instancia del usuario
        """
        try:
            with db_manager.get_db() as db:
                # Verificar si el usuario existe
                user = db.query(User).filter(User.email == google_info['email']).first()
                
                if user:
                    # Actualizar información si es necesario
                    self._update_user_info(user, google_info)
                    db.commit()
                    return user
                
                # Determinar rol inicial
                initial_role = self._determine_initial_role(google_info['email'])
                
                # Crear nuevo usuario
                user = User.from_google_info(google_info, role=initial_role)
                db.add(user)
                
                # Registrar actividad
                self._register_activity(
                    db,
                    user.email,
                    'user_created',
                    {'initial_role': initial_role.value}
                )
                
                db.commit()
                logger.info(f"Nuevo usuario creado: {user.email}")
                return user
                
        except Exception as e:
            logger.error(f"Error en get_or_create_user: {str(e)}")
            raise

    def _determine_initial_role(self, email: str) -> UserRole:
        """
        Determina el rol inicial de un usuario basado en su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            UserRole: Rol asignado
        """
        if email in settings.ADMIN_EMAILS_LIST:
            return UserRole.ADMIN
        if email in settings.VALIDATOR_EMAILS_LIST:
            return UserRole.VALIDATOR
        return UserRole.USER

    def _update_user_info(self, user: User, google_info: Dict):
        """
        Actualiza la información de un usuario existente.
        
        Args:
            user: Usuario a actualizar
            google_info: Nueva información de Google
        """
        user.picture_url = google_info.get('picture', user.picture_url)
        user.given_name = google_info.get('given_name', user.given_name)
        user.family_name = google_info.get('family_name', user.family_name)
        user.full_name = google_info.get('name', user.full_name)
        user.locale = google_info.get('locale', user.locale)
        user.metadata.update({
            'last_google_update': datetime.utcnow().isoformat(),
            'google_verified_email': google_info.get('email_verified', False)
        })

    def _register_activity(self, db, user_email: str, activity_type: str, details: Dict = None):
        """
        Registra una actividad de usuario.
        
        Args:
            db: Sesión de base de datos
            user_email: Email del usuario
            activity_type: Tipo de actividad
            details: Detalles adicionales
        """
        activity = UserActivity(
            id=str(uuid4()),
            user_email=user_email,
            activity_type=activity_type,
            details=details or {}
        )
        db.add(activity)

    async def update_last_login(self, email: str) -> bool:
        """
        Actualiza la marca de tiempo del último login.
        
        Args:
            email: Email del usuario
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            with db_manager.get_db() as db:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    user.last_login = datetime.utcnow()
                    user.last_seen = datetime.utcnow()
                    
                    self._register_activity(
                        db,
                        email,
                        'user_login',
                        {'login_time': datetime.utcnow().isoformat()}
                    )
                    
                    db.commit()
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando último login: {str(e)}")
            return False

    async def check_authorization(self, email: str, required_role: UserRole) -> bool:
        """
        Verifica si un usuario tiene el rol requerido.
        
        Args:
            email: Email del usuario
            required_role: Rol requerido
            
        Returns:
            bool: True si está autorizado
        """
        try:
            with db_manager.get_db() as db:
                user = db.query(User).filter(
                    User.email == email,
                    User.is_active == True
                ).first()
                
                if not user:
                    return False
                
                # Admin tiene todos los permisos
                if user.role == UserRole.ADMIN:
                    return True
                    
                # Validator puede hacer todo excepto acciones de admin
                if user.role == UserRole.VALIDATOR and required_role != UserRole.ADMIN:
                    return True
                    
                return user.role == required_role
                
        except Exception as e:
            logger.error(f"Error verificando autorización: {str(e)}")
            return False

    async def get_user_activities(
        self,
        email: str,
        limit: int = 50,
        activity_type: str = None
    ) -> List[Dict]:
        """
        Obtiene el historial de actividades de un usuario.
        
        Args:
            email: Email del usuario
            limit: Límite de registros a retornar
            activity_type: Filtro por tipo de actividad
            
        Returns:
            List[Dict]: Lista de actividades
        """
        try:
            with db_manager.get_db() as db:
                query = db.query(UserActivity)\
                    .filter(UserActivity.user_email == email)\
                    .order_by(UserActivity.timestamp.desc())
                
                if activity_type:
                    query = query.filter(UserActivity.activity_type == activity_type)
                
                activities = query.limit(limit).all()
                return [activity.to_dict() for activity in activities]
                
        except Exception as e:
            logger.error(f"Error obteniendo actividades: {str(e)}")
            return []

    async def get_user_profile(self, email: str) -> Optional[Dict]:
        """
        Obtiene el perfil completo de un usuario.
        
        Args:
            email: Email del usuario
            
        Returns:
            Dict: Información completa del usuario o None si no existe
        """
        try:
            with db_manager.get_db() as db:
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    return None
                    
                # Obtener últimas actividades
                recent_activities = await self.get_user_activities(email, limit=5)
                
                # Construir perfil completo
                profile = user.to_dict()
                profile.update({
                    'recent_activities': recent_activities,
                    'permissions': UserRole.get_permissions(user.role)
                })
                
                return profile
                
        except Exception as e:
            logger.error(f"Error obteniendo perfil: {str(e)}")
            return None

# Instancia global del servicio
user_service = UserService()