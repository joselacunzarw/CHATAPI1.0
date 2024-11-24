# UDCito API - Asistente Virtual Universidad del Chubut 🎓
![Versión](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-blue)
![Docker](https://img.shields.io/badge/Docker-required-blue)

## 📑 Tabla de Contenidos
- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso de la API](#-uso-de-la-api)
- [Monitoreo](#-monitoreo)
- [Guía para Desarrolladores](#-guía-para-desarrolladores)
- [Troubleshooting](#-troubleshooting)
- [Soporte](#-soporte)

## 📋 Descripción
UDCito es un asistente virtual potenciado por IA diseñado específicamente para la Universidad del Chubut. 
Utiliza tecnología RAG (Retrieval-Augmented Generation) para proporcionar respuestas precisas y contextualizadas
basadas en la documentación institucional oficial.

### Características Principales:
- 🤖 Respuestas basadas en documentación oficial
- 🔍 Búsqueda semántica avanzada
- 💬 Manejo de conversaciones contextuales
- 📊 Monitoreo y métricas en tiempo real
- 🔒 Seguridad y validación de datos
- 📚 Base de conocimiento actualizable

## 🏗 Arquitectura

### Tecnologías Core:
| Tecnología | Versión | Uso |
|------------|---------|-----|
| FastAPI | latest | Framework web API REST |
| LangChain | 0.3.0 | Orquestación de LLMs |
| ChromaDB | 0.4.22 | Base de datos vectorial |
| OpenAI | - | Modelos de lenguaje |
| Docker | - | Contenedorización |

### Estructura del Proyecto:
```plaintext
ChatAPI/
├── app/
│   ├── __init__.py
│   ├── core.py              # Lógica central RAG
│   ├── main.py             # Endpoints API
│   └── monitoring/         # Monitoreo
│       ├── __init__.py
│       ├── health.py      # Health checks
│       └── metrics.py     # Métricas
├── data/
│   ├── chroma/            # BD vectorial
│   └── sqlite/            # BD relacional
├── docs/                  # Documentación adicional
├── tests/                # Tests unitarios/integración
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## 🔧 Requisitos

### Requisitos de Sistema:
- CPU: 2 cores mínimo (4+ recomendado)
- RAM: 4GB mínimo (8GB+ recomendado)
- Almacenamiento: 20GB+ SSD recomendado
- OS: Linux, Windows, macOS

### Software Requerido:
- Python 3.11+
- Docker 20.10+
- Docker Compose v2+
- Git

### Credenciales Necesarias:
- OpenAI API Key
- Credenciales de desarrollo UDC (opcional)

## 📦 Instalación

### 1. Usando Docker (Recomendado):
```bash
# Clonar repositorio
git clone https://github.com/tuorganizacion/udcito-api.git
cd udcito-api

# Configurar ambiente
cp .env.example .env
# Editar .env con tus credenciales

# Construir y ejecutar
docker-compose up -d --build

# Verificar instalación
curl http://localhost:8000/health
```

### 2. Instalación Manual (Desarrollo):
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env con configuración local

# Ejecutar
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Verificación Post-Instalación:
```bash
# Health Check
curl http://localhost:8000/health

# Documentación API
# Abrir en navegador:
# http://localhost:8000/docs
```

### Requerimientos de Red:
- Puerto 8000 disponible
- Acceso a api.openai.com
- Conexión a Internet estable

### Consideraciones de Seguridad:
1. Nunca exponer directamente sin proxy reverso
2. Configurar CORS apropiadamente
3. Implementar rate limiting en producción
4. Usar HTTPS en producción
## ⚙️ Configuración Detallada

### Variables de Entorno (.env)

#### 1. API Keys y Autenticación
```env
# API Key de OpenAI
OPENAI_API_KEY=sk-...

# Configuración de seguridad (opcional)
API_KEY_HEADER=X-API-Key
API_KEY=tu-api-key-local
```

| Variable | Descripción | Valor Default | Impacto |
|----------|-------------|---------------|----------|
| OPENAI_API_KEY | Clave de API de OpenAI | - | Crítico - Sin esto no funciona |
| API_KEY_HEADER | Nombre del header para auth | X-API-Key | Seguridad |
| API_KEY | Clave para autenticación local | - | Seguridad |

#### 2. Configuración de Modelos

```env
# Modelo de Embeddings
EMBEDDING_MODEL_NAME=text-embedding-3-small

# Modelo de Lenguaje Principal
MODEL_NAME=gpt-4o

# Parámetros de Generación
TEMPERATURE=0.7
MAX_TOKENS=5000
```

| Variable | Opciones | Uso Recomendado | Impacto en Costos |
|----------|----------|-----------------|-------------------|
| EMBEDDING_MODEL_NAME | text-embedding-3-small<br>text-embedding-3-large | small: uso general<br>large: alta precisión | small: $0.00002/1K tokens<br>large: $0.00013/1K tokens |
| MODEL_NAME | gpt-4o<br>gpt-3.5-turbo<br>gpt-4-turbo-preview | gpt-4o: precisión<br>gpt-3.5: velocidad<br>gpt-4-turbo: balance | gpt-4o: $0.03/1K<br>gpt-3.5: $0.002/1K<br>gpt-4-turbo: $0.01/1K |

##### Temperatura (TEMPERATURE)
- **Rango**: 0.0 a 1.0
- **Efectos**:
  ```
  0.0 → Respuestas consistentes y deterministas
  0.3 → Bueno para información factual
  0.7 → Balance creatividad/precisión
  1.0 → Máxima creatividad
  ```
- **Recomendaciones por caso de uso**:
  | Caso de Uso | Temperatura | Razón |
  |-------------|-------------|-------|
  | Información académica | 0.1-0.3 | Precisión necesaria |
  | Preguntas generales | 0.5-0.7 | Balance |
  | Interacción casual | 0.7-0.9 | Más personalidad |

##### Tokens Máximos (MAX_TOKENS)
- **Consideraciones**:
  ```
  1K tokens ≈ 750 palabras
  1 página ≈ 2K tokens
  ```
- **Recomendaciones**:
  | Tipo de Respuesta | Tokens | Uso Típico |
  |-------------------|--------|------------|
  | Corta | 1000-2000 | Respuestas puntuales |
  | Media | 3000-4000 | Explicaciones detalladas |
  | Larga | 5000+ | Documentación extensa |

#### 3. Configuración de Base de Datos

```env
# Rutas de Bases de Datos
CHROMA_PATH=/app/data/chroma
SQLITE_PATH=/app/data/sqlite

# Parámetros de Recuperación
RETRIEVER_K=10
```

| Variable | Descripción | Consideraciones | Mantenimiento |
|----------|-------------|-----------------|---------------|
| CHROMA_PATH | Ubicación BD vectorial | Necesita permisos de escritura | Backup regular |
| SQLITE_PATH | Ubicación BD relacional | Monitorear crecimiento | Vacuum periódico |
| RETRIEVER_K | Docs a recuperar | Más = mejor contexto pero más lento | Ajustar según uso |

#### 4. Configuración de Rendimiento

```env
# Configuración del Servidor
WORKERS=4
BACKLOG=2048
TIMEOUT=60

# Límites y Caché
RATE_LIMIT=100/minute
CACHE_TTL=3600
```

| Variable | Descripción | Cálculo Recomendado | Notas |
|----------|-------------|---------------------|-------|
| WORKERS | Procesos worker | (2 × CPU cores) + 1 | Balancear con RAM |
| BACKLOG | Cola de conexiones | 1024-4096 | Según tráfico |
| TIMEOUT | Timeout en segundos | 30-120 | Según complejidad |

### Perfiles de Configuración

#### Desarrollo
```env
ENVIRONMENT=development
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=2000
RETRIEVER_K=5
WORKERS=2
```

#### Producción
```env
ENVIRONMENT=production
MODEL_NAME=gpt-4o
TEMPERATURE=0.5
MAX_TOKENS=5000
RETRIEVER_K=10
WORKERS=4
```

#### Alta Precisión
```env
MODEL_NAME=gpt-4o
TEMPERATURE=0.2
MAX_TOKENS=8000
RETRIEVER_K=15
EMBEDDING_MODEL_NAME=text-embedding-3-large
```

### Cambios que Requieren Atención

#### Requieren Reinicio:
- Cambios en WORKERS
- Modificación de MODEL_NAME
- Actualización de API_KEY

#### Requieren Reindexación:
- Cambio de EMBEDDING_MODEL_NAME
- Modificación de estructura de documentos
- Actualización de CHROMA_PATH

#### Afectan Costos:
- Incremento de MAX_TOKENS
- Cambio a modelos más potentes
- Aumento de RETRIEVER_K

### Monitoreo de Configuración

```bash
# Ver configuración actual
curl http://localhost:8000/health

# Verificar variables cargadas
docker-compose exec api env

# Logs de configuración
docker-compose logs -f | grep "CONFIG"
```
## 🚀 Uso de la API

### Endpoints Principales

#### 1. Health Check
```http
GET /health
```

**Descripción**: Verifica el estado del sistema y sus componentes.

**Respuesta Exitosa**:
```json
{
  "overall_status": "healthy",
  "timestamp": "2024-11-21T15:30:45.123456",
  "checks": {
    "system": {
      "status": "healthy",
      "cpu_percent": 45.2,
      "memory_used_percent": 62.8,
      "disk_used_percent": 75.1,
      "disk_free_gb": 120.5,
      "uptime_hours": 48.5,
      "details": {
        "total_memory_gb": 16.0,
        "available_memory_gb": 6.0,
        "total_disk_gb": 500.0,
        "cpu_count": 8
      }
    },
    "database": {
      "status": "healthy",
      "chroma_path": "/app/data/chroma",
      "path_exists": true,
      "path_writable": true
    }
  },
  "version": "1.0.0"
}
```

#### 2. Consulta al Asistente
```http
POST /consultar
```

**Request Body**:
```json
{
  "question": "¿Cuáles son los requisitos de inscripción?",
  "history": [
    {
      "role": "user",
      "content": "Hola, necesito información"
    },
    {
      "role": "assistant",
      "content": "¡Hola! ¿En qué puedo ayudarte?"
    }
  ]
}
```

**Headers Requeridos**:
```http
Content-Type: application/json
```

**Respuesta Exitosa**:
```json
{
  "reply": "Para inscribirte en la Universidad del Chubut necesitas presentar la siguiente documentación:\n1. DNI original y copia\n2. Título secundario legalizado\n3. ..."
}
```

#### 3. Recuperación de Documentos
```http
POST /recuperar_documentos
```

**Request Body**:
```json
{
  "query": "inscripción"
}
```

**Respuesta Exitosa**:
```json
{
  "documentos": [
    {
      "content": "El proceso de inscripción comienza en marzo...",
      "metadata": {
        "source": "reglamento_academico.pdf",
        "page": 1
      }
    }
  ]
}
```

### Ejemplos de Uso

#### Python con Requests
```python
import requests
import json

class UDCitoClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self):
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def consultar(self, pregunta, historial=None):
        if historial is None:
            historial = []
            
        data = {
            "question": pregunta,
            "history": historial
        }
        
        response = self.session.post(
            f"{self.base_url}/consultar",
            json=data
        )
        return response.json()

# Ejemplo de uso
client = UDCitoClient()

# Verificar estado
health = client.check_health()
print(f"Estado del sistema: {health['overall_status']}")

# Realizar consulta
respuesta = client.consultar("¿Qué carreras ofrecen?")
print(f"Respuesta: {respuesta['reply']}")
```

#### cURL
```bash
# Health Check
curl http://localhost:8000/health

# Consulta Simple
curl -X POST http://localhost:8000/consultar \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuáles son los requisitos?",
    "history": []
  }'

# Recuperar Documentos
curl -X POST http://localhost:8000/recuperar_documentos \
  -H "Content-Type: application/json" \
  -d '{
    "query": "inscripción"
  }'
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

class UDCitoAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.api = axios.create({ baseURL });
    }

    async checkHealth() {
        const { data } = await this.api.get('/health');
        return data;
    }

    async consultar(question, history = []) {
        const { data } = await this.api.post('/consultar', {
            question,
            history
        });
        return data;
    }
}

// Ejemplo de uso
async function main() {
    const client = new UDCitoAPI();
    
    try {
        // Verificar estado
        const health = await client.checkHealth();
        console.log('Estado:', health.overall_status);
        
        // Realizar consulta
        const respuesta = await client.consultar(
            '¿Cuándo comienzan las inscripciones?'
        );
        console.log('Respuesta:', respuesta.reply);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

### Manejo de Errores

#### Códigos de Estado HTTP
| Código | Significado | Acción Recomendada |
|--------|-------------|-------------------|
| 200 | Éxito | Procesar respuesta |
| 400 | Error en request | Verificar datos enviados |
| 401 | No autorizado | Verificar API key |
| 429 | Rate limit | Implementar backoff |
| 500 | Error interno | Contactar soporte |

#### Ejemplos de Errores Comunes:
```json
{
  "detail": "Invalid request format",
  "code": "INVALID_REQUEST",
  "params": {
    "field": "question",
    "error": "required"
  }
}
```

#### Manejo de Rate Limiting:
```python
def consultar_con_retry(client, pregunta, max_intentos=3):
    for intento in range(max_intentos):
        try:
            return client.consultar(pregunta)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                tiempo_espera = int(e.response.headers.get('Retry-After', 5))
                time.sleep(tiempo_espera)
                continue
            raise
    raise Exception("Máximo de intentos alcanzado")
```
## 👩‍💻 Guía para Desarrolladores

### Agregar un Nuevo Endpoint

#### 1. Definir Modelos de Datos
```python
# app/models/my_endpoint.py
from pydantic import BaseModel, Field
from typing import List, Optional

class MyRequestModel(BaseModel):
    """
    Modelo para la solicitud del nuevo endpoint
    """
    param1: str = Field(
        ...,
        description="Descripción del parámetro",
        min_length=1,
        example="ejemplo"
    )
    param2: Optional[int] = Field(
        None,
        description="Parámetro opcional",
        ge=0,
        example=42
    )

class MyResponseModel(BaseModel):
    """
    Modelo para la respuesta del nuevo endpoint
    """
    result: str = Field(..., description="Resultado de la operación")
    status: bool = Field(..., description="Estado de la operación")
    details: Optional[dict] = Field(None, description="Detalles adicionales")
```

#### 2. Implementar la Lógica
```python
# app/services/my_service.py
from app.models.my_endpoint import MyRequestModel, MyResponseModel
from app.core import logger

async def process_my_request(data: MyRequestModel) -> MyResponseModel:
    """
    Procesa la lógica del nuevo endpoint
    
    Args:
        data: Datos de la solicitud
    
    Returns:
        MyResponseModel: Resultado procesado
        
    Raises:
        ValueError: Si hay errores de validación
    """
    try:
        # Tu lógica aquí
        result = f"Procesado: {data.param1}"
        
        return MyResponseModel(
            result=result,
            status=True,
            details={"processed_at": datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"Error procesando solicitud: {str(e)}")
        raise
```

#### 3. Agregar el Endpoint
```python
# app/main.py o en un router separado
from fastapi import APIRouter, HTTPException, status
from app.models.my_endpoint import MyRequestModel, MyResponseModel
from app.services.my_service import process_my_request

router = APIRouter()

@router.post(
    "/mi_endpoint",
    response_model=MyResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Mi Servicio"],
    summary="Descripción corta del endpoint",
    description="Descripción detallada de lo que hace el endpoint"
)
async def mi_endpoint(
    request: MyRequestModel
) -> MyResponseModel:
    """
    Documentación detallada del endpoint
    
    Args:
        request: Datos de la solicitud
        
    Returns:
        MyResponseModel: Respuesta procesada
        
    Raises:
        HTTPException: Cuando ocurre un error
    """
    try:
        response = await process_my_request(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
```

#### 4. Agregar Tests
```python
# tests/test_mi_endpoint.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_mi_endpoint_success():
    """Test caso exitoso"""
    response = client.post(
        "/mi_endpoint",
        json={
            "param1": "test",
            "param2": 42
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == True
    assert "test" in data["result"]

def test_mi_endpoint_validation_error():
    """Test error de validación"""
    response = client.post(
        "/mi_endpoint",
        json={
            "param1": "",  # Viola min_length
            "param2": -1   # Viola ge
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_mi_endpoint_service():
    """Test unitario del servicio"""
    request = MyRequestModel(param1="test", param2=42)
    response = await process_my_request(request)
    assert response.status == True
```

### Buenas Prácticas

#### 1. Estructura de Código
```plaintext
app/
├── models/          # Modelos Pydantic
├── services/        # Lógica de negocio
├── routers/         # Endpoints agrupados
├── core/            # Funcionalidad central
└── utils/           # Utilidades comunes
```

#### 2. Convenciones de Código
```python
# Nombres de clases: PascalCase
class UserRequest(BaseModel):
    pass

# Nombres de funciones/variables: snake_case
async def process_user_request(data: UserRequest):
    pass

# Constantes: MAYÚSCULAS
MAX_RETRIES = 3
```

#### 3. Logging
```python
# Configurar logger en cada módulo
logger = logging.getLogger(__name__)

# Usar niveles apropiados
logger.debug("Información detallada para debugging")
logger.info("Información general del flujo")
logger.warning("Advertencias que requieren atención")
logger.error("Errores que afectan la operación")
logger.critical("Errores que requieren acción inmediata")
```

#### 4. Manejo de Errores
```python
# Errores personalizados
class AppError(Exception):
    """Base para errores de la aplicación"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)

# Usar en endpoints
@router.post("/endpoint")
async def endpoint():
    try:
        result = await process_something()
    except AppError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": e.message,
                "code": e.code
            }
        )
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Errores de Conexión
```bash
# Verificar estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart
```

#### 2. Problemas de Memoria
```bash
# Ver uso de recursos
docker stats

# Limpiar cachés
docker system prune -f

# Aumentar límites en docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 3. Errores de Base de Datos
```bash
# Verificar permisos
ls -la data/chroma/

# Verificar espacio
df -h

# Backup de emergencia
tar -czf backup.tar.gz data/
```

#### 4. Problemas de Rendimiento
```bash
# Monitorear tiempos de respuesta
curl -w "\nTiempo total: %{time_total}s\n" http://localhost:8000/health

# Identificar cuellos de botella
docker-compose logs -f | grep "SLOW"
```

### Herramientas de Diagnóstico

#### 1. Health Check Detallado
```bash
curl -v http://localhost:8000/health
```

#### 2. Métricas del Sistema
```bash
curl http://localhost:8000/metrics
```

#### 3. Logs en Tiempo Real
```bash
# Todos los logs
docker-compose logs -f

# Filtrar por tipo
docker-compose logs -f | grep "ERROR"
docker-compose logs -f | grep "WARN"

# Logs específicos
docker-compose logs -f api
```

### Lista de Verificación para Problemas

1. **API No Responde:**
   - [ ] Verificar status de contenedores
   - [ ] Comprobar logs
   - [ ] Verificar puertos y firewall
   - [ ] Comprobar recursos del sistema

2. **Errores en Consultas:**
   - [ ] Verificar formato de request
   - [ ] Comprobar API key de OpenAI
   - [ ] Verificar conexión a Internet
   - [ ] Revisar logs de errores

3. **Problemas de Performance:**
   - [ ] Monitorear uso de recursos
   - [ ] Verificar configuración de workers
   - [ ] Comprobar índices de base de datos
   - [ ] Analizar tiempos de respuesta

### Mantenimiento Preventivo

1. **Diario:**
   - Monitorear logs
   - Verificar health check
   - Revisar uso de recursos

2. **Semanal:**
   - Backup de bases de datos
   - Análisis de métricas
   - Limpieza de logs antiguos

3. **Mensual:**
   - Actualización de dependencias
   - Revisión de índices
   - Optimización de configuración
   ## 🤝 Contribución y Desarrollo

### Flujo de Trabajo para Contribuciones

#### 1. Preparación del Ambiente
```bash
# Clonar repositorio
git clone https://github.com/tuorganizacion/udcito-api.git
cd udcito-api

# Crear rama feature
git checkout -b feature/mi-nueva-funcionalidad

# Preparar ambiente desarrollo
cp .env.example .env.dev
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

#### 2. Estándares de Código
```python
# Usar type hints
def procesar_datos(texto: str) -> dict:
    pass

# Docstrings informativos
def mi_funcion():
    """
    Descripción corta.

    Descripción más detallada que puede
    ocupar múltiples líneas.

    Args:
        param1: Descripción del parámetro

    Returns:
        Descripción del valor retornado

    Raises:
        ValueError: Cuándo y por qué
    """
    pass
```

#### 3. Tests
```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_mi_modulo.py -v
```

### Guías de Estilo

#### Python
- Seguir PEP 8
- Máximo 88 caracteres por línea
- Usar type hints
- Docstrings en todos los módulos y funciones públicas

#### Commits
```bash
# Formato
<tipo>(<alcance>): <descripción>

# Ejemplos
feat(auth): agregar autenticación JWT
fix(db): corregir conexión a Chroma
docs(api): actualizar documentación endpoints
```

#### Pull Requests
- Título descriptivo
- Descripción detallada
- Referencias a issues
- Lista de cambios principales
- Capturas de pantalla (si aplica)

## 📞 Soporte y Contacto

### Canales de Soporte

#### 1. Soporte Técnico
- Email: soporte.tecnico@udc.edu.ar
- Horario: Lunes a Viernes 8:00-18:00 (ARG)
- SLA: 24-48 horas hábiles

#### 2. Problemas de API
- Crear issue en GitHub
- Incluir logs relevantes
- Describir pasos para reproducir
- Adjuntar ejemplos de request/response

#### 3. Documentación
- Wiki del proyecto: [link]
- Documentación API: http://localhost:8000/docs
- Guías: /docs/guides/

### Reportar Problemas

```markdown
### Descripción del Problema
[Descripción clara y concisa]

### Pasos para Reproducir
1. [Primer paso]
2. [Segundo paso]
3. [etc...]

### Comportamiento Esperado
[Qué debería ocurrir]

### Comportamiento Actual
[Qué está ocurriendo]

### Logs
```log
[Pegar logs relevantes aquí]
```

### Información Adicional
- Versión de la API: [ej. 1.0.0]
- Ambiente: [dev/prod]
- Sistema Operativo: [ej. Ubuntu 22.04]
```

## 📝 Mantenimiento

### Tareas Periódicas

#### Diarias
- [ ] Verificar health checks
- [ ] Monitorear uso de recursos
- [ ] Revisar logs de errores

#### Semanales
- [ ] Backup de bases de datos
- [ ] Actualizar índices si necesario
- [ ] Revisar métricas de uso

#### Mensuales
- [ ] Actualizar dependencias
- [ ] Revisar y actualizar documentación
- [ ] Análisis de performance

### Procedimientos de Actualización

#### 1. Actualizar Dependencias
```bash
# Verificar actualizaciones disponibles
pip list --outdated

# Actualizar requirements.txt
pip freeze > requirements.txt

# Actualizar contenedor
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Backup de Datos
```bash
# Backup completo
./scripts/backup.sh

# Backup selectivo
./scripts/backup.sh --only-db
```

#### 3. Restauración
```bash
# Restaurar último backup
./scripts/restore.sh latest

# Restaurar backup específico
./scripts/restore.sh 2024-11-21
```

## 📄 Licencia y Avisos Legales

### Licencia MIT

```
MIT License

Copyright (c) 2024 Universidad del Chubut

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Avisos de Terceros

Este proyecto utiliza las siguientes tecnologías de terceros:

- **OpenAI API**: Sujeto a términos y condiciones de OpenAI
- **FastAPI**: Licencia MIT
- **LangChain**: Licencia MIT
- **ChromaDB**: Licencia Apache 2.0

### Información de Contacto

- **Equipo de Desarrollo**
  - Email: desarrollo@udc.edu.ar
  - GitHub: @udc-dev
  
- **Soporte Técnico**
  - Email: soporte.tecnico@udc.edu.ar
  - Tel: +54 (XXX) XXX-XXXX

- **Universidad del Chubut**
  - Web: https://www.udc.edu.ar
  - Dirección: [Dirección Física]

---

**Nota**: Este README está en constante evolución. Última actualización: Noviembre 2024.