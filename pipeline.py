"""
Pipeline del agente de búsqueda de propiedades
Define el StateGraph con todos los nodos y maneja sesiones en memoria
"""
from langgraph.graph import StateGraph, END
from models.state import AgentState
from nodes import (
    receive_message_node,
    extract_filters_node,
    check_completion_node,
    route_after_check_completion,
    ask_missing_filter_node,
    ask_additional_filters_node,
    collect_optional_filters_node,
    route_after_collect_optional,
    generate_sql_node,
    validate_sql_node,
    route_after_validate_sql,
    execute_sql_node,
    format_results_node,
)
from typing import Dict
from datetime import datetime, timedelta
import uuid


# ============================================================================
# DEFINICIÓN DEL GRAFO
# ============================================================================

def create_property_search_graph():
    """
    Crea y compila el StateGraph para búsqueda de propiedades.
    
    Returns:
        Grafo compilado listo para ejecutar
    """
    print("🔨 Creando StateGraph...")
    
    # Crear grafo con AgentState
    workflow = StateGraph(AgentState)
    
    # ========== AGREGAR NODOS ==========
    workflow.add_node("receive_message", receive_message_node)
    workflow.add_node("extract_filters", extract_filters_node)
    workflow.add_node("check_completion", check_completion_node)
    workflow.add_node("ask_missing_filter", ask_missing_filter_node)
    workflow.add_node("ask_additional_filters", ask_additional_filters_node)
    workflow.add_node("collect_optional_filters", collect_optional_filters_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("format_results", format_results_node)
    
    # ========== DEFINIR ENTRY POINT ==========
    workflow.set_entry_point("receive_message")
    
    # ========== EDGES NORMALES (secuenciales) ==========
    workflow.add_edge("receive_message", "extract_filters")
    workflow.add_edge("extract_filters", "check_completion")
    
    # ask_missing_filter termina esperando respuesta del usuario
    workflow.add_edge("ask_missing_filter", END)
    
    # ask_additional_filters termina esperando confirmación
    workflow.add_edge("ask_additional_filters", END)
    
    workflow.add_edge("generate_sql", "validate_sql")
    workflow.add_edge("execute_sql", "format_results")
    
    # format_results siempre es el final
    workflow.add_edge("format_results", END)
    
    # ========== CONDITIONAL EDGES (routers) ==========
    
    # Router 1: Después de check_completion
    # Decide si pregunta por filtro faltante o por filtros adicionales
    workflow.add_conditional_edges(
        "check_completion",
        route_after_check_completion,
        {
            "ask_missing_filter": "ask_missing_filter",
            "ask_additional_filters": "ask_additional_filters"
        }
    )
    
    # Router 2: Después de collect_optional_filters
    # Decide si extrae más filtros o genera SQL
    workflow.add_conditional_edges(
        "collect_optional_filters",
        route_after_collect_optional,
        {
            "extract_filters": "extract_filters",
            "generate_sql": "generate_sql"
        }
    )
    
    # Router 3: Después de validate_sql
    # Decide si ejecuta SQL o va directo a format_results con error
    workflow.add_conditional_edges(
        "validate_sql",
        route_after_validate_sql,
        {
            "execute_sql": "execute_sql",
            "format_results": "format_results"
        }
    )
    
    # ========== COMPILAR GRAFO ==========
    compiled_graph = workflow.compile()
    
    print("✅ StateGraph creado y compilado exitosamente")
    print(f"📊 Nodos: {len(workflow.nodes)}")
    print(f"🔗 Edges: normales + 3 condicionales")
    
    return compiled_graph


# ============================================================================
# MANEJO DE SESIONES EN MEMORIA
# ============================================================================

class SessionManager:
    """
    Gestor de sesiones en memoria.
    Mantiene el estado de cada conversación independiente por session_id.
    """
    
    def __init__(self, timeout_seconds: int = 3600):
        """
        Args:
            timeout_seconds: Tiempo de vida de una sesión en segundos (default: 1 hora)
        """
        self.sessions: Dict[str, AgentState] = {}
        self.timeout = timedelta(seconds=timeout_seconds)
        print(f"📦 SessionManager inicializado (timeout: {timeout_seconds}s)")
    
    def create_session(self, session_id: str = None) -> AgentState:
        """
        Crea una nueva sesión.
        
        Args:
            session_id: ID de sesión (si None, genera uno nuevo)
            
        Returns:
            Nuevo AgentState inicializado
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Crear nuevo estado
        state = AgentState(session_id=session_id)
        
        # Guardar en memoria
        self.sessions[session_id] = state
        
        print(f"✅ Nueva sesión creada: {session_id}")
        return state
    
    def get_session(self, session_id: str) -> AgentState:
        """
        Obtiene una sesión existente o crea una nueva si no existe.
        Limpia sesiones expiradas automáticamente.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            AgentState de la sesión
        """
        # Limpiar sesiones expiradas primero
        self._cleanup_expired_sessions()
        
        # Si la sesión existe, retornarla
        if session_id in self.sessions:
            state = self.sessions[session_id]
            
            # Verificar si expiró
            if datetime.now() - state.last_updated > self.timeout:
                print(f"⏰ Sesión {session_id} expiró, creando nueva")
                return self.create_session(session_id)
            
            print(f"📖 Sesión recuperada: {session_id}")
            return state
        
        # Si no existe, crear nueva
        print(f"🆕 Sesión no existe, creando nueva: {session_id}")
        return self.create_session(session_id)
    
    def update_session(self, session_id: str, state: AgentState):
        """
        Actualiza el estado de una sesión.
        
        Args:
            session_id: ID de la sesión
            state: Estado actualizado
        """
        state.last_updated = datetime.now()
        self.sessions[session_id] = state
        print(f"💾 Sesión actualizada: {session_id}")
    
    def delete_session(self, session_id: str):
        """
        Elimina una sesión.
        
        Args:
            session_id: ID de la sesión a eliminar
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"🗑️ Sesión eliminada: {session_id}")
    
    def _cleanup_expired_sessions(self):
        """Limpia sesiones expiradas."""
        now = datetime.now()
        expired = [
            sid for sid, state in self.sessions.items()
            if now - state.last_updated > self.timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
            
        if expired:
            print(f"🧹 Limpieza: {len(expired)} sesiones expiradas eliminadas")
    
    def get_active_sessions_count(self) -> int:
        """Retorna el número de sesiones activas."""
        return len(self.sessions)
    
    def get_session_info(self, session_id: str) -> dict:
        """
        Obtiene información de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con info de la sesión o None si no existe
        """
        if session_id not in self.sessions:
            return None
        
        state = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": state.created_at.isoformat(),
            "last_updated": state.last_updated.isoformat(),
            "messages_count": len(state.messages),
            "essential_filters_complete": state.essential_filters_complete,
            "filters_count": state.filters.count_essential_filters(),
            "ready_to_search": state.ready_to_search,
            "query_executed": state.query_executed,
        }


# ============================================================================
# INSTANCIAS GLOBALES
# ============================================================================

# Crear el grafo compilado (solo una vez al iniciar)
property_search_graph = create_property_search_graph()

# Crear el gestor de sesiones
session_manager = SessionManager(timeout_seconds=3600)  # 1 hora

print("✅ Pipeline inicializado y listo")
print(f"🌐 Grafo: property_search_graph")
print(f"📦 Sesiones: session_manager")


# ============================================================================
# FUNCIONES HELPER PARA USO EN LA API
# ============================================================================

async def process_user_message(session_id: str, user_message: str) -> AgentState:
    """
    Procesa un mensaje del usuario manteniendo el contexto de la sesión.
    
    Args:
        session_id: ID de la sesión
        user_message: Mensaje del usuario
        
    Returns:
        Estado actualizado después de procesar el mensaje
    """
    print(f"\n{'='*70}")
    print(f"🔄 PROCESANDO MENSAJE - Sesión: {session_id[:8]}...")
    print(f"{'='*70}")
    
    # Obtener o crear sesión
    state = session_manager.get_session(session_id)
    
    # Agregar mensaje del usuario al historial
    state.add_message("user", user_message)
    
    # Ejecutar el grafo
    try:
        result = await property_search_graph.ainvoke(state)
        
        # Actualizar sesión con el resultado
        session_manager.update_session(session_id, result)
        
        print(f"✅ Mensaje procesado exitosamente")
        return result
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        state.error_message = str(e)
        session_manager.update_session(session_id, state)
        raise


def get_session_state(session_id: str) -> AgentState:
    """
    Obtiene el estado actual de una sesión.
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Estado actual de la sesión
    """
    return session_manager.get_session(session_id)


def reset_session(session_id: str) -> AgentState:
    """
    Reinicia una sesión (crea una nueva con el mismo ID).
    
    Args:
        session_id: ID de la sesión a reiniciar
        
    Returns:
        Nuevo estado limpio
    """
    session_manager.delete_session(session_id)
    return session_manager.create_session(session_id)