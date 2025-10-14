"""
Nodo: collect_optional_filters
Maneja la recolección de filtros opcionales (máximo 3) y detecta cuando el usuario está listo
"""
from models.state import AgentState
from typing import Literal
import re


def collect_optional_filters_node(state: AgentState) -> AgentState:
    """
    Analiza la respuesta del usuario cuando está en modo de recolección de opcionales.
    Detecta si dice "suficiente/no/búscalo" o si agrega un filtro opcional.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado
    """
    print(f"\n{'='*60}")
    print(f"📥 COLLECT OPTIONAL FILTERS NODE")
    print(f"{'='*60}")
    
    # Obtener último mensaje del usuario
    last_message = None
    for msg in reversed(state.messages):
        if msg.get("role") == "user":
            last_message = msg.get("content", "").lower()
            break
    
    if not last_message:
        print("⚠️ No se encontró mensaje del usuario")
        state.current_node = "collect_optional_filters"
        return state
    
    print(f"Analizando respuesta: '{last_message[:100]}...'")
    
    # Detectar si el usuario quiere proceder a la búsqueda
    proceed_keywords = [
        "no", "suficiente", "búscalo", "buscalo", "busca", 
        "así está bien", "asi esta bien", "perfecto", "listo",
        "ya", "eso es todo", "nada más", "nada mas"
    ]
    
    wants_to_proceed = any(keyword in last_message for keyword in proceed_keywords)
    
    if wants_to_proceed:
        print("✅ Usuario quiere proceder a la búsqueda")
        state.ready_to_search = True
        state.awaiting_additional_filters_confirmation = False
        state.collecting_optional_filters = False
        state.current_node = "collect_optional_filters"
        return state
    
    # Si no quiere proceder, verificar cuántos opcionales tiene
    optional_count = state.filters.count_optional_filters()
    print(f"📊 Filtros opcionales actuales: {optional_count}/3")
    
    if optional_count >= 3:
        print("⚠️ Ya tiene 3 filtros opcionales (máximo alcanzado)")
        state.ready_to_search = True
        state.awaiting_additional_filters_confirmation = False
        state.collecting_optional_filters = False
        
        # Agregar mensaje informando que procederá
        state.add_message(
            "assistant", 
            "Entendido. Ya tienes 3 filtros adicionales, procederé con la búsqueda."
        )
    else:
        print(f"ℹ️ Puede agregar {3 - optional_count} filtros opcionales más")
        state.collecting_optional_filters = True
        state.awaiting_additional_filters_confirmation = False
    
    # Actualizar metadata
    state.current_node = "collect_optional_filters"
    
    return state


def route_after_collect_optional(state: AgentState) -> Literal["extract_filters", "generate_sql"]:
    """
    Función de routing después de collect_optional_filters.
    Decide si debe extraer más filtros o proceder a generar SQL.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Nombre del siguiente nodo
    """
    if state.ready_to_search:
        print("➡️ Routing: Listo para búsqueda → generate_sql")
        return "generate_sql"
    else:
        print("➡️ Routing: Recolectando más filtros → extract_filters")
        return "extract_filters"