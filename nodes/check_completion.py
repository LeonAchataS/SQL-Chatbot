"""
Nodo: check_completion
Router node - Decide el siguiente paso basado en completitud de filtros esenciales
"""
from models.state import AgentState
from typing import Literal


def check_completion_node(state: AgentState) -> AgentState:
    """
    Verifica si los 5 filtros esenciales están completos.
    Actualiza el flag essential_filters_complete.
    
    Este es un nodo que NO toma decisiones de routing aquí,
    solo actualiza el estado. El routing lo hace el conditional edge en el grafo.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con flag de completitud
    """
    print(f"\n{'='*60}")
    print(f"✔️ CHECK COMPLETION NODE")
    print(f"{'='*60}")
    
    # Contar filtros esenciales
    essential_count = state.filters.count_essential_filters()
    missing_filters = state.filters.get_missing_essential_filters()
    
    print(f"📊 Filtros esenciales completados: {essential_count}/5")
    
    if missing_filters:
        print(f"⚠️ Filtros faltantes: {', '.join(missing_filters)}")
        state.essential_filters_complete = False
    else:
        print(f"✅ ¡Todos los filtros esenciales están completos!")
        state.essential_filters_complete = True
    
    # Actualizar metadata
    state.current_node = "check_completion"
    
    return state


def route_after_check_completion(state: AgentState) -> Literal["ask_missing_filter", "ask_additional_filters"]:
    """
    Función de routing para decidir el siguiente nodo después de check_completion.
    Esta función se usa en el conditional edge del grafo.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Nombre del siguiente nodo
    """
    if state.essential_filters_complete:
        # Si YA preguntamos por opcionales, ir directo a collect
        if state.awaiting_additional_filters_confirmation:
            print("➡️ Routing: Ya preguntamos por opcionales → collect_optional_filters")
            return "collect_optional_filters"
        else:
            print("➡️ Routing: Filtros completos → ask_additional_filters")
            return "ask_additional_filters"
    else:
        print("➡️ Routing: Filtros incompletos → ask_missing_filter")
        return "ask_missing_filter"