"""
FastAPI Application - Real Estate Chatbot
Ejecutar con: python main.py
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from models.settings import settings
from models.schemas import (
    ChatRequest,
    ChatResponse,
    PropertiesListResponse,
    PropertyResponse,
    PropertyFiltersResponse,
    ErrorResponse
)
from pipeline import (
    process_user_message,
    get_session_state,
    reset_session,
    session_manager
)
from db import db
import uuid


# ============================================================================
# LIFESPAN - Manejo de startup/shutdown
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja eventos de startup y shutdown de la aplicación.
    """
    # STARTUP
    print("\n" + "="*70)
    print("🚀 INICIANDO APLICACIÓN")
    print("="*70)
    
    # Conectar a la base de datos
    try:
        await db.connect()
        await db.test_connection()
        print("✅ Base de datos conectada")
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        raise
    
    print("✅ Pipeline inicializado")
    print("✅ SessionManager listo")
    print(f"🌐 API escuchando en http://{settings.api_host}:{settings.api_port}")
    print("="*70 + "\n")
    
    yield
    
    # SHUTDOWN
    print("\n" + "="*70)
    print("🛑 APAGANDO APLICACIÓN")
    print("="*70)
    
    # Desconectar base de datos
    await db.disconnect()
    print("✅ Base de datos desconectada")
    print("="*70 + "\n")


# ============================================================================
# CREAR APP
# ============================================================================

app = FastAPI(
    title="Real Estate Chatbot API",
    description="API para chatbot de búsqueda de propiedades inmobiliarias",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS - Para permitir requests desde frontend local
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raíz - Health check básico.
    """
    return {
        "message": "Real Estate Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check para Railway y monitoring.
    """
    try:
        # Verificar conexión a DB
        version = await db.fetch_val("SELECT version()")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        version = None
    
    return {
        "status": "healthy",
        "database": db_status,
        "active_sessions": session_manager.get_active_sessions_count(),
        "postgres_version": version[:50] if version else None
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Endpoint principal del chat.
    Recibe mensaje del usuario y retorna respuesta del agente.
    
    Request:
        - session_id (opcional): ID de sesión. Si no se provee, se crea uno nuevo
        - message: Mensaje del usuario
    
    Response:
        - session_id: ID de la sesión
        - response: Respuesta del agente
        - filters: Estado actual de filtros
        - ready_to_search: Si está listo para buscar propiedades
        - properties_found: Número de propiedades encontradas (si ya buscó)
    """
    try:
        # Generar session_id si no viene
        session_id = request.session_id or str(uuid.uuid4())
        
        print(f"\n{'='*70}")
        print(f"💬 CHAT REQUEST - Session: {session_id[:8]}...")
        print(f"📝 Message: {request.message[:100]}...")
        print(f"{'='*70}")
        
        # Procesar mensaje
        state = await process_user_message(session_id, request.message)
        
        # Obtener última respuesta del asistente
        assistant_response = None
        for msg in reversed(state.messages):
            if msg.get("role") == "assistant":
                assistant_response = msg.get("content")
                break
        
        if not assistant_response:
            assistant_response = "Lo siento, no pude procesar tu mensaje. ¿Puedes intentar de nuevo?"
        
        # Construir response con filtros
        filters_response = PropertyFiltersResponse(
            distrito=state.filters.distrito,
            area_min=state.filters.area_min,
            estado_propiedad=state.filters.estado_propiedad,
            monto_maximo=state.filters.monto_maximo,
            dormitorios=state.filters.dormitorios,
            permite_mascotas=state.filters.permite_mascotas,
            balcon=state.filters.balcon,
            terraza=state.filters.terraza,
            amoblado=state.filters.amoblado,
            banios=state.filters.banios,
            essential_count=state.filters.count_essential_filters(),
            optional_count=state.filters.count_optional_filters(),
            is_complete=state.filters.is_complete()
        )
        
        # Contar propiedades si ya se ejecutó la búsqueda
        properties_count = None
        if state.query_results is not None:
            properties_count = len(state.query_results)
        
        response = ChatResponse(
            session_id=session_id,
            response=assistant_response,
            filters=filters_response,
            ready_to_search=state.ready_to_search,
            properties_found=properties_count
        )
        
        print(f"✅ Response generado - {len(assistant_response)} chars")
        print(f"📊 Filtros: {filters_response.essential_count}/5 esenciales")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en /chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@app.get("/properties/{session_id}", response_model=PropertiesListResponse, tags=["Properties"])
async def get_properties(session_id: str):
    """
    Obtiene las propiedades encontradas para una sesión.
    Solo retorna datos si ya se ejecutó la búsqueda.
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Lista de propiedades encontradas con sus detalles
    """
    try:
        print(f"\n{'='*70}")
        print(f"🏠 GET PROPERTIES - Session: {session_id[:8]}...")
        print(f"{'='*70}")
        
        # Obtener estado de la sesión
        state = get_session_state(session_id)
        
        # Verificar que se haya ejecutado la búsqueda
        if not state.query_executed:
            raise HTTPException(
                status_code=400,
                detail="No se ha ejecutado ninguna búsqueda en esta sesión. Completa la conversación primero."
            )
        
        if state.query_results is None:
            raise HTTPException(
                status_code=404,
                detail="No hay resultados disponibles."
            )
        
        # Convertir resultados a PropertyResponse
        properties = []
        for prop in state.query_results:
            property_response = PropertyResponse(
                id=str(prop.get("id")),
                numero=prop.get("numero"),
                piso=prop.get("piso"),
                tipo=prop.get("tipo"),
                area=prop.get("area"),
                dormitorios=prop.get("dormitorios"),
                banios=prop.get("banios"),
                balcon=prop.get("balcon", False),
                terraza=prop.get("terraza", False),
                amoblado=prop.get("amoblado", False),
                permite_mascotas=prop.get("permite_mascotas", False),
                valor_comercial=prop.get("valor_comercial"),
                mantenimiento_mensual=prop.get("mantenimiento_mensual"),
                estado=prop.get("estado"),
                edificio_nombre=prop.get("edificio_nombre"),
                edificio_direccion=prop.get("edificio_direccion"),
                edificio_distrito=prop.get("edificio_distrito")
            )
            properties.append(property_response)
        
        # Construir filtros usados
        filters_response = PropertyFiltersResponse(
            distrito=state.filters.distrito,
            area_min=state.filters.area_min,
            estado_propiedad=state.filters.estado_propiedad,
            monto_maximo=state.filters.monto_maximo,
            dormitorios=state.filters.dormitorios,
            permite_mascotas=state.filters.permite_mascotas,
            balcon=state.filters.balcon,
            terraza=state.filters.terraza,
            amoblado=state.filters.amoblado,
            banios=state.filters.banios,
            essential_count=state.filters.count_essential_filters(),
            optional_count=state.filters.count_optional_filters(),
            is_complete=state.filters.is_complete()
        )
        
        response = PropertiesListResponse(
            session_id=session_id,
            count=len(properties),
            properties=properties,
            filters_used=filters_response,
            sql_query=state.generated_sql  # Para debug
        )
        
        print(f"✅ Retornando {len(properties)} propiedades")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en /properties: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo propiedades: {str(e)}"
        )


@app.get("/session/{session_id}", tags=["Session"])
async def get_session_info(session_id: str):
    """
    Obtiene información de una sesión (útil para debugging).
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Información del estado de la sesión
    """
    try:
        info = session_manager.get_session_info(session_id)
        
        if info is None:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada"
            )
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo info de sesión: {str(e)}"
        )


@app.post("/session/{session_id}/reset", tags=["Session"])
async def reset_session_endpoint(session_id: str):
    """
    Reinicia una sesión (borra todo el historial y filtros).
    
    Args:
        session_id: ID de la sesión a reiniciar
        
    Returns:
        Mensaje de confirmación
    """
    try:
        reset_session(session_id)
        
        return {
            "message": "Sesión reiniciada exitosamente",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reiniciando sesión: {str(e)}"
        )


@app.get("/sessions/active", tags=["Session"])
async def get_active_sessions():
    """
    Obtiene el número de sesiones activas (para monitoring).
    """
    return {
        "active_sessions": session_manager.get_active_sessions_count()
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para excepciones no manejadas.
    """
    print(f"❌ Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc)
        }
    )


# ============================================================================
# MAIN - Para ejecutar con python main.py
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR")
    print("="*70)
    print(f"Host: {settings.api_host}")
    print(f"Port: {settings.api_port}")
    print(f"Reload: {settings.api_reload}")
    print(f"Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )