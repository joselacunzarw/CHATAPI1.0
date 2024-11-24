"""
Core.py - Módulo Principal del Asistente UDCito
==============================================

Este módulo implementa la funcionalidad central del asistente virtual de la Universidad del Chubut.
Maneja la carga de configuración, la conexión con OpenAI, y la lógica de consultas.

Componentes principales:
1. Gestión de variables de entorno
2. Inicialización de servicios (embeddings, base de datos, LLM)
3. Funciones de consulta y recuperación de documentos

Autor: Jose Lacunza Kobs
Fecha: Noviembre 2024
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# =====================================
# Configuración inicial de logging
# =====================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Limpiar cualquier API key existente para evitar conflictos
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

def load_environment():
    """
    Carga y valida las variables de entorno desde el archivo .env
    
    El archivo .env debe contener:
    - OPENAI_API_KEY: Clave de API de OpenAI
    - EMBEDDING_MODEL_NAME: Nombre del modelo de embeddings
    - MODEL_NAME: Modelo de GPT a utilizar
    - TEMPERATURE: Temperatura para generación de respuestas
    - MAX_TOKENS: Límite de tokens en respuestas
    - RETRIEVER_K: Número de documentos a recuperar
    - DATA_PATH: Ruta a los datos
    - CHROMA_PATH: Ruta a la base de datos Chroma
    
    Returns:
        dict: Diccionario con todas las variables de configuración
    """
    # Buscar el archivo .env en la carpeta actual
    env_path = Path('.env')
    
    # Verificar que existe el archivo
    if not env_path.exists():
        raise ValueError("❌ Archivo .env no encontrado en la ruta actual")
    
    # Cargar variables de entorno
    load_dotenv(env_path)
    logger.info(f"📂 Archivo .env cargado desde: {env_path.absolute()}")
    
    # Validar API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY no configurada en .env")
    if not api_key.startswith('sk-'):
        raise ValueError("❌ OPENAI_API_KEY con formato incorrecto")
    
    logger.info("✅ Variables de entorno cargadas correctamente")
    
    # Retornar configuración completa
    return {
        'OPENAI_API_KEY': api_key,
        'EMBEDDING_MODEL_NAME': os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small'),
        'DATA_PATH': os.getenv('DATA_PATH'),
        'CHROMA_PATH': os.getenv('CHROMA_PATH'),
        'MODEL_NAME': os.getenv('MODEL_NAME', 'gpt-4-turbo-preview'),  # Corregido el modelo por defecto
        'TEMPERATURE': float(os.getenv('TEMPERATURE', '0.7')),
        'MAX_TOKENS': int(os.getenv('MAX_TOKENS', '5000')),
        'RETRIEVER_K': int(os.getenv('RETRIEVER_K', '10'))
    }

def initialize_services():
    """
    Inicializa todos los servicios necesarios para el funcionamiento del asistente:
    1. Embeddings de OpenAI
    2. Base de datos Chroma
    3. Recuperador de documentos
    4. Modelo de lenguaje (LLM)
    
    Returns:
        tuple: (embeddings, db, retriever, llm)
    """
    try:
        # Cargar configuración
        config = load_environment()
        
        # Establecer API key en variables de entorno
        os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
        
        # 1. Inicializar servicio de embeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=config['OPENAI_API_KEY']
        )
        
        # 2. Validar y configurar base de datos Chroma
        if not config['CHROMA_PATH']:
            raise ValueError("❌ CHROMA_PATH no configurado en .env")
        
        db = Chroma(
            persist_directory=config['CHROMA_PATH'],
            embedding_function=embeddings
        )
        
        # 3. Configurar recuperador de documentos
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config['RETRIEVER_K']}
        )
        
        # 4. Inicializar modelo de lenguaje
        llm = ChatOpenAI(
            model_name=config['MODEL_NAME'],
            temperature=config['TEMPERATURE'],
            max_tokens=config['MAX_TOKENS'],
            openai_api_key=config['OPENAI_API_KEY']
        )
        
        logger.info("✅ Servicios inicializados correctamente")
        return embeddings, db, retriever, llm
        
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {str(e)}")
        raise

# =====================================
# Inicialización Global de Servicios
# =====================================
try:
    embeddings, db, retriever, llm = initialize_services()
except Exception as e:
    logger.error(f"❌ Error crítico durante la inicialización: {str(e)}")
    raise

def test_openai_connection():
    """
    Verifica la conexión con OpenAI realizando una prueba de embeddings
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        _ = embeddings.embed_query("test")
        logger.info("✅ Conexión con OpenAI verificada")
        return True
    except Exception as e:
        logger.error(f"❌ Error de conexión con OpenAI: {str(e)}")
        return False

def recuperar_documentos(query: str) -> list:
    """
    Recupera documentos relevantes de la base de datos según la consulta
    
    Args:
        query (str): Consulta del usuario
        
    Returns:
        list: Lista de documentos relevantes
    """
    try:
        docs = retriever.invoke(input=query)
        for doc in docs:
            logger.info(f"📄 Documento recuperado: {doc.metadata}")
        return docs
    except Exception as e:
        logger.error(f"❌ Error en recuperación: {str(e)}")
        return []

def consultar_llm(context_docs: list, question: str, history: list) -> str:
    """
    Realiza una consulta al modelo de lenguaje usando el contexto y el historial
    
    Args:
        context_docs (list): Lista de documentos de contexto
        question (str): Pregunta del usuario
        history (list): Historial de conversación
        
    Returns:
        str: Respuesta del modelo
    """
    try:
        # Unir todo el contexto en un solo texto
        context = "\n".join([doc.page_content for doc in context_docs])
        
        # Crear mensaje del sistema con instrucciones
        system_message = SystemMessage(
            content=(
                "Eres UDCito un asistente de la Universidad del Chubut. "
                "Responde usando solo la información del siguiente contexto. "
                "Si la información no es suficiente, indícalo. "
                f"Contexto: {context}"
            )
        )

        # Construir lista de mensajes con el historial
        messages = [system_message]
        for msg in history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))

        # Agregar la pregunta actual
        messages.append(HumanMessage(content=question))
        
        # Obtener respuesta del modelo
        logger.info("💭 Enviando consulta al LLM...")
        response = llm.invoke(input=messages)
        logger.info("✅ Respuesta recibida")
        
        return response.content

    except Exception as e:
        logger.error(f"❌ Error en consulta: {str(e)}")
        return f"Lo siento, ocurrió un error: {str(e)}"

# =====================================
# Verificación inicial de conexión
# =====================================
if not test_openai_connection():
    raise ConnectionError("❌ No se pudo establecer conexión con OpenAI")