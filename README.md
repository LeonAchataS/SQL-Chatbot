# 🏠 Real Estate Chatbot - SQL Agent

Chatbot conversacional para búsqueda de propiedades inmobiliarias usando LangGraph, OpenAI y PostgreSQL.

## 📋 Descripción

Sistema de agente inteligente que guía al usuario en la búsqueda de departamentos mediante una conversación natural. Recopila 5 filtros esenciales (distrito, área mínima, estado, presupuesto, dormitorios) y hasta 3 filtros opcionales (pet-friendly, balcón, terraza, amoblado, baños) para generar y ejecutar consultas SQL dinámicamente contra una base de datos PostgreSQL.

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **AI/ML**: LangChain, LangGraph, OpenAI GPT-4
- **Base de Datos**: PostgreSQL, asyncpg
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Validación**: Pydantic V2

## 📁 Estructura del Proyecto

```
real_estate_agent/
├── models/
│   ├── settings.py          # Configuración con Pydantic V2 (env vars)
│   ├── state.py             # AgentState - Estado conversacional
│   └── schemas.py           # Schemas FastAPI (Request/Response)
├── tools/
│   ├── property_tools.py    # Tools para filtros (extracción, preguntas)
│   └── sql_tools.py         # Tools para SQL (generación, validación, ejecución)
├── prompts/
│   ├── system_prompts.py    # Prompts del sistema para LLM
│   └── examples.py          # Few-shot examples
├── nodes/
│   ├── __init__.py          # Exporta todos los nodos
│   ├── receive_message.py   # Recibe mensaje del usuario
│   ├── extract_filters.py   # Extrae filtros con LLM
│   ├── check_completion.py  # Verifica completitud (Router)
│   ├── ask_missing_filter.py    # Pregunta por filtro faltante
│   ├── ask_additional.py    # Pregunta por filtros opcionales
│   ├── collect_optional.py  # Recolecta opcionales (Router)
│   ├── generate_sql.py      # Genera SQL con LLM
│   ├── validate_sql.py      # Valida seguridad SQL (Router)
│   ├── execute_sql.py       # Ejecuta query en PostgreSQL
│   └── format_results.py    # Formatea respuesta final
├── db/
│   ├── __init__.py          # Expone instancia global `db`
│   └── connection.py        # DatabaseManager con asyncpg
├── frontend/
│   ├── index.html           # UI del chatbot
│   ├── style.css            # Estilos minimalistas
│   └── script.js            # Lógica y API calls
├── pipeline.py              # StateGraph + SessionManager
├── main.py                  # FastAPI app (ejecutable)
├── dependencies.py          # Dependencias FastAPI
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
└── README.md
```

## 🔄 Flujo del Agente (StateGraph)

```
START → receive_message → extract_filters → check_completion
                                                    ↓
                            ┌───────────────────────┴───────────────────┐
                            ↓                                           ↓
                  ask_missing_filter                      ask_additional_filters
                            ↓                                           ↓
                          END                              collect_optional_filters
                                                                        ↓
                                                        ┌───────────────┴──────────┐
                                                        ↓                          ↓
                                                extract_filters              generate_sql
                                                (más opcionales)                   ↓
                                                                            validate_sql
                                                                                   ↓
                                                                    ┌──────────────┴─────────┐
                                                                    ↓                        ↓
                                                            execute_sql              format_results
                                                                    ↓                      (error)
                                                            format_results
                                                                    ↓
                                                                  END
```

**Routers (Conditional Edges):**
- `check_completion`: Filtros completos → adicionales | incompletos → pregunta
- `collect_optional`: Listo → SQL | no listo → más filtros
- `validate_sql`: Válido → ejecutar | inválido → error

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.11+
- PostgreSQL 15+
- OpenAI API Key

### Setup

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd real_estate_agent

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales:
# - OPENAI_API_KEY
# - DATABASE_URL
# - DATABASE_SCHEMA

# 4. Ejecutar backend
python main.py
```

Backend disponible en: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### Frontend

```bash
# Abrir frontend/index.html en navegador
# O usar Live Server en VS Code
```

## 📡 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/chat` | Enviar mensaje del usuario |
| `GET` | `/properties/{session_id}` | Obtener propiedades encontradas |
| `GET` | `/session/{session_id}` | Info de sesión (debug) |
| `POST` | `/session/{session_id}/reset` | Reiniciar sesión |
| `GET` | `/health` | Health check |

### Ejemplo Request/Response

**POST /chat**
```json
// Request
{
  "session_id": "uuid-opcional",
  "message": "Busco departamento en San Isidro"
}

// Response
{
  "session_id": "uuid",
  "response": "¿Cuál es el área mínima que necesitas?",
  "filters": {
    "distrito": "San Isidro",
    "area_min": null,
    "essential_count": 1,
    "is_complete": false
  },
  "ready_to_search": false,
  "properties_found": null
}
```

## 🗄️ Esquema de Base de Datos

Schema: `property_infrastructure`

**Tablas principales:**
- `propiedad`: Propiedades (departamentos, locales, etc.)
- `edificio`: Edificios/complejos

**Campos clave en `propiedad`:**
- numero, piso, tipo, area, dormitorios, banios
- balcon, terraza, amoblado, permite_mascotas
- valor_comercial, estado
- edificio_id (FK → edificio.id)

**Campos clave en `edificio`:**
- nombre, direccion, distrito

## 🔑 Variables de Entorno (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0

# PostgreSQL
DATABASE_URL=postgresql://user:pass@host:port/dbname
DATABASE_SCHEMA=property_infrastructure

# Configuración
MAX_OPTIONAL_FILTERS=3
PROPERTIES_LIMIT=5
SESSION_TIMEOUT=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧠 Características Clave

- ✅ **Sesiones persistentes**: Mantiene contexto entre mensajes (en memoria)
- ✅ **SQL seguro**: Validación estricta (solo SELECT, sin SQL injection)
- ✅ **Conversacional**: Extrae múltiples filtros de un solo mensaje
- ✅ **Corrección automática**: Reintenta SQL hasta 3 veces si falla
- ✅ **Límites configurables**: 5 esenciales + máx 3 opcionales
- ✅ **Async/await**: Pool de conexiones asyncpg
- ✅ **Type-safe**: Pydantic V2 en todo el proyecto

## 🐳 Docker (Opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📝 Notas Técnicas

- **LangGraph**: StateGraph con 10 nodos + 3 routers condicionales
- **Pydantic V2**: BaseModel y BaseSettings (no TypedDict)
- **SessionManager**: En memoria con timeout automático (1 hora)
- **Tools**: Decorador `@tool` de LangChain
- **CORS**: Habilitado para desarrollo local

## 🔧 Troubleshooting

**Error: 'dict' object has no attribute 'last_updated'**
- LangGraph retorna dict, se convierte a AgentState en `process_user_message`

**Error: SQL injection detected**
- Validación bloqueando query legítimo → revisar `validate_sql_node`

**Error: No properties found**
- Verificar datos en PostgreSQL schema `property_infrastructure`
- Revisar filtros generados en logs

**Frontend no conecta**
- Verificar CORS en main.py
- Cambiar `API_URL` en script.js si backend no está en localhost:8000