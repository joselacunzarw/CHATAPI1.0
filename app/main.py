"""
FastAPI Main Application - UDCito
================================

Este es el archivo principal de la API del Asistente Virtual de la Universidad del Chubut.
Maneja todas las rutas, la configuración de la API y la integración de los diferentes componentes.

Autor: [Tu Nombre]
Fecha: Noviembre 2024
Versión: 1.0.0
"""

# === Importaciones Estándar ===
import time
from datetime import datetime
from typing import List, Dict, Optional

# === Importaciones FastAPI ===
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# === Importaciones Locales ===
from app.core import recuperar_documentos, consultar_llm
from app.monitoring.health import health_checker
from app.monitoring.metrics import metrics_collector

# === Modelos de Datos ===
class Question(BaseModel):
    """Modelo para las preguntas del usuario"""
    question: str = Field(
        ..., 
        min_length=1,
        description="Pregunta del usuario",
        example="¿Cuáles son los requisitos de inscripción?"
    )

class ChatMessage(BaseModel):
    """Modelo para los mensajes del chat"""
    role: str = Field(
        ..., 
        pattern="^(user|assistant)$",
        description="Rol del mensaje (usuario o asistente)"
    )
    content: str = Field(
        ..., 
        min_length=1,
        description="Contenido del mensaje"
    )

class ChatRequest(BaseModel):
    """Modelo para las solicitudes de chat"""
    question: str = Field(
        ..., 
        min_length=1,
        description="Pregunta actual del usuario"
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="Historial de la conversación"
    )

class DocumentResponse(BaseModel):
    """Modelo para las respuestas con documentos"""
    documentos: List[str] = Field(
        ...,
        description="Lista de documentos relevantes encontrados"
    )

class ChatResponse(BaseModel):
    """Modelo para las respuestas del chat"""
    reply: str = Field(
        ...,
        description="Respuesta del asistente"
    )

# === Inicialización de la Aplicación ===
app = FastAPI(
    title="UDCito API",
    description="API para el asistente virtual de la Universidad del Chubut",
    version="1.0.0",
    docs_url="/docs",  # URL para la documentación Swagger
    redoc_url="/redoc"  # URL para la documentación ReDoc
)

# === Configuración de CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Middleware para Métricas ===
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Middleware para registrar métricas de cada request
    
    Args:
        request: Request entrante
        call_next: Siguiente middleware o endpoint
    """
    start_time = time.time()
    try:
        # Procesar la request
        response = await call_next(request)
        
        # Registrar métricas de éxito
        metrics_collector.record_request(
            success=True,
            response_time=time.time() - start_time
        )
        return response
    except Exception as e:
        # Registrar métricas de error
        metrics_collector.record_request(
            success=False,
            response_time=time.time() - start_time
        )
        raise

# === Endpoints de Monitoreo ===
@app.get(
    "/health",
    tags=["Monitoreo"],
    summary="Verificar estado del sistema",
    description="Realiza un health check completo del sistema y sus componentes"
)
async def health_check():
    """
    Endpoint de health check que verifica el estado del sistema
    
    Returns:
        dict: Estado actual del sistema y sus componentes
    """
    return await health_checker.check_health()

@app.get(
    "/metrics",
    tags=["Monitoreo"],
    summary="Obtener métricas del sistema",
    description="Retorna métricas de uso y rendimiento del sistema"
)
async def get_metrics():
    """
    Endpoint para obtener métricas del sistema
    
    Returns:
        dict: Métricas actuales del sistema
    """
    return metrics_collector.get_current_metrics()

# === Endpoints del Chat ===
@app.post(
    "/recuperar_documentos",
    response_model=DocumentResponse,
    tags=["Documentos"],
    summary="Recuperar documentos relevantes",
    description="Busca y retorna documentos relevantes para una pregunta"
)
async def recuperar_docs(question: Question):
    """
    Endpoint para recuperar documentos relevantes basados en una pregunta
    
    Args:
        question (Question): Pregunta del usuario
    
    Returns:
        DocumentResponse: Lista de documentos relevantes
    
    Raises:
        HTTPException: Si hay error en la recuperación
    """
    if not question.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La pregunta no puede estar vacía"
        )

    try:
        documentos = recuperar_documentos(question.question)
        return DocumentResponse(documentos=[doc.page_content for doc in documentos])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar documentos: {str(e)}"
        )

@app.post(
    "/consultar",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Consultar al asistente",
    description="Realiza una consulta al asistente utilizando el historial de chat"
)
async def consultar(request: ChatRequest):
    """
    Endpoint principal para consultar al asistente
    
    Args:
        request (ChatRequest): Pregunta actual e historial de chat
    
    Returns:
        ChatResponse: Respuesta del asistente
    
    Raises:
        HTTPException: Si hay error en la consulta
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La pregunta no puede estar vacía"
        )

    try:
        # Recuperar documentos relevantes
        contexto = recuperar_documentos(request.question)
        
        # Consultar al LLM
        respuesta = consultar_llm(
            contexto, 
            request.question,
            [{"role": msg.role, "content": msg.content} for msg in request.history]
        )
        
        return ChatResponse(reply=respuesta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la consulta: {str(e)}"
        )

# === Inicio de la Aplicación ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=False
    )