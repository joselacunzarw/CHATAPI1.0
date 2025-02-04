"""
Core.py - Módulo Principal del Asistente UDCito
==============================================

Este módulo implementa la funcionalidad central del asistente virtual de la Universidad del Chubut.
Maneja la carga de configuración, la conexión con OpenAI y la lógica de consultas.

Mejoras implementadas:
✅ Uso del historial en la consulta de recuperación.
✅ Reformulación de preguntas para mejorar el contexto.
✅ Reordenamiento de documentos recuperados (Reranking).
✅ Búsqueda híbrida (Embeddings + Texto).
✅ Preparación para MultiQuery Retriever (sin implementarlo todavía).

Cada una de estas mejoras puede ser comentada si no deseas usarla, sin afectar el resto del código.

Autor: Jose Lacunza Kobs
Fecha: Enero 2025
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.retrievers.multi_query import MultiQueryRetriever

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
                "Eres un Chatbot asistente de la Universidad del Chubut. "
                "Responde usando solo la información del siguiente contexto, teniendo en cuenta tambien el historial de conversacion. "
                "Usa un tono formal y profesional. "
                "No inventes información y responde solo con datos verificados. "
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




# ==========================================
# FUNCIONES AUXILIARES PARA MEJORAS
# ==========================================

def reformular_pregunta(history: list, question: str) -> str:
    """Reformula la pregunta para hacerla más clara y con contexto."""
    try:
        reformulacion = llm.invoke(input=[
            SystemMessage(content="Reformula la pregunta del humano teniendo en cuenta el contexto y el historial, tu respuesta se utilizara para recuperar informacion de la base vectorial y contestar la pregunta del humano."),
            HumanMessage(content=f"Historial: {history[-3:]}"),
            HumanMessage(content=f"Pregunta: {question}")
        ])
        logger.info("✅ Reformulación recibida")
        logger.info(f"🔄 Reformulación: {reformulacion.content}")

        return reformulacion.content
    except Exception as e:
        logger.error(f"❌ Error en reformulación: {str(e)}")
        return question  # Devuelve la original si falla

def reordenar_documentos(query: str, documentos: list) -> list:
    """Reordena los documentos recuperados según su relevancia."""
    try:
        documentos_rankeados = sorted(
            documentos,
            key=lambda doc: llm.invoke(input=[
                SystemMessage(content="Evalúa la relevancia del documento."),
                HumanMessage(content=f"Consulta: {query}"),
                HumanMessage(content=f"Documento: {doc.page_content}")
            ]).content,
            reverse=True
        )
        return documentos_rankeados
    except Exception as e:
        logger.error(f"❌ Error en reordenamiento: {str(e)}")
        return documentos  # Devuelve los documentos en su orden original

def recuperar_documentos_hibrido(query: str, history: list) -> list:
    """Usa búsqueda híbrida (Embeddings + Texto completo) para mejorar la recuperación."""
    try:
        # ✅ Convertir `history` en una lista de strings
        historial_completo = " ".join([msg.content for msg in history[-3:]]) if history else ""

        # ✅ Enriquecer la consulta con historial (si hay)
        consulta_enriquecida = f"{historial_completo} {query}".strip()

        # Recuperación semántica (Embeddings)
        documentos_semanticos = retriever.invoke(input=consulta_enriquecida)

        # Recuperación por palabras clave (Texto completo)
        documentos_texto = db.similarity_search(consulta_enriquecida, k=5)

        # ✅ Solución: Usar un diccionario para eliminar duplicados
        documentos_unicos = {doc.page_content: doc for doc in documentos_semanticos + documentos_texto}.values()

        return list(documentos_unicos)
    except Exception as e:
        logger.error(f"❌ Error en recuperación híbrida: {str(e)}")
        return []


# ==========================================
# FUNCIÓN PRINCIPAL DE RECUPERACIÓN DE DOCUMENTOS
# ==========================================

def recuperar_documentos(query: str, history: list) -> list:
    """
    Recupera documentos relevantes basándose en la consulta y el historial.
    
    Incorpora mejoras opcionales que pueden comentarse según necesidad.
    """
    try:
        # 1️⃣ Reformulación de la pregunta (Opcional)
        query = reformular_pregunta(history, query)  # 💬 Comentar para desactivar

        # 2️⃣ Recuperación de documentos con búsqueda híbrida (Opcional)

        documentos = recuperar_documentos_multiquery(query, history)  # 🔍 Comentar para usar embbedings
        #documentos = recuperar_documentos_hibrido(query, history)  # 🔍 Comentar para usar solo embeddings

        # 3️⃣ Reordenamiento de documentos (Opcional)
       # documentos = reordenar_documentos(query, documentos)  # 📄 Comentar si no quieres usar reranking

        return documentos
    except Exception as e:
        logger.error(f"❌ Error en recuperación de documentos: {str(e)}")
        return []

# ==========================================
# PREPARACIÓN PARA MULTIQUERY RETRIEVER
# ==========================================

def recuperar_documentos_multiquery(query: str, history: list) -> list:
    """
    📌 Recupera documentos usando `MultiQuery Retriever`.

    🛠️ ¿Cómo funciona?
    1️⃣ Usa un modelo LLM para generar varias versiones de la consulta original.
    2️⃣ Ejecuta cada consulta reformulada en la base de datos vectorial.
    3️⃣ Fusiona los resultados y elimina duplicados.

    Args:
        query (str): Pregunta original del usuario.
        history (list): Historial de conversación (no se usa en esta versión, pero puede usarse en el futuro).

    Returns:
        list: Lista de documentos únicos encontrados.
    """
    try:
        # ✅ Configuramos el retriever MultiQuery con el modelo de lenguaje
        multiquery_retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,  # 🔍 Base de datos vectorial
            llm=llm,  # 🧠 Modelo de lenguaje para generar consultas múltiples
            include_original=True  # ✅ Incluir la consulta original en la búsqueda
        )

        # ✅ Ejecutamos la recuperación con múltiples consultas generadas
        documentos_multiquery = multiquery_retriever.get_relevant_documents(query)

        # ✅ Eliminamos duplicados usando `page_content` como clave
        documentos_unicos = {doc.page_content: doc for doc in documentos_multiquery}.values()

        return list(documentos_unicos)

    except Exception as e:
        logger.error(f"❌ Error en recuperación MultiQuery: {str(e)}")
        return []
