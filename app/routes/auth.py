"""
Rutas de Autenticación - UDCito API
=================================

Endpoints relacionados con autenticación y gestión de usuarios.
Maneja el flujo de autenticación con Google OAuth y gestión de sesiones.

Autor: [Tu Nombre]
Fecha: Noviembre 2024
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.user_service import user_service
from app.db.models import UserRole

router = APIRouter(prefix="/auth", tags=["Autenticación"])
security = HTTPBearer()

# === Modelos de Datos ===
class GoogleLoginRequest(BaseModel):
    """Modelo para solicitud de login con Google"""
    token: str = "Token ID de Google"

class UserResponse(BaseModel):
    """Modelo para respuesta con información de usuario"""
    email: str
    name: str
    role: str
    picture_url: Optional[str] = None
    permissions: list

class LoginResponse(BaseModel):
    """Modelo para respuesta de login exitoso"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

# === Endpoints ===
@router.post("/login/google", response_model=LoginResponse)
async def google_login(request: GoogleLoginRequest):
    """
    Endpoint para login con Google OAuth.
    Verifica el token y crea/actualiza el usuario.
    
    Args:
        request: Token ID de Google
        
    Returns:
        LoginResponse con información del usuario y token de acceso
    """
    try:
        # Verificar token de Google
        google_info = await user_service.verify_google_token(request.token)
        
        # Obtener o crear usuario
        user = await user_service.get_or_create_user(google_info)
        
        # Actualizar último login
        await user_service.update_last_login(user.email)
        
        # Generar token de acceso
        access_token = create_access_token(user.email)
        
        return LoginResponse(
            user=UserResponse(
                email=user.email,
                name=user.full_name,
                role=user.role.value,
                picture_url=user.picture_url,
                permissions=UserRole.get_permissions(user.role)
            ),
            access_token=access_token
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando login"
        )

@router.get("/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtiene el perfil del usuario actual.
    Requiere token de autenticación.
    """
    try:
        # Verificar token
        user_email = verify_access_token(credentials.credentials)
        
        # Obtener perfil
        profile = await user_service.get_user_profile(user_email)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        return UserResponse(**profile)
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

# Funciones auxiliares para JWT (implementar en un módulo separado)
def create_access_token(email: str) -> str:
    """Crea un token JWT de acceso"""
    # Implementar generación de JWT
    pass

def verify_access_token(token: str) -> str:
    """Verifica un token JWT y retorna el email del usuario"""
    # Implementar verificación de JWT
    pass