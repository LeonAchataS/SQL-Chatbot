"""
Nodo: ask_additional_filters
Pregunta al usuario si desea agregar filtros opcionales (cuando los 5 esenciales están completos)
"""
from models.state import AgentState
from tools.property_tools import ask_for_additional_filters
import json


def ask_additional_filters_node(state: AgentState) -> AgentState:
    """
    Genera un mensaje preguntando si el usuario quiere agregar filtros opcionales.
    Activa el flag awaiting_additional_filters_confirmation.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con pregunta y flag activado
    """
    print(f"\n{'='*60}")
    print(f"💬 ASK ADDITIONAL FILTERS NODE")
    print(f"{'='*60}")
    
    # Verificar que los filtros esenciales estén completos
    if not state.essential_filters_complete:
        print("⚠️ Los filtros esenciales no están completos (esto no debería ocurrir)")
        state.current_node = "ask_additional_filters"
        return state
    
    print("✅ Filtros esenciales completos. Preguntando por opcionales...")
    
    # Preparar filtros actuales
    current_filters = state.filters.model_dump(exclude_none=True)
    current_filters_json = json.dumps(current_filters, ensure_ascii=False)
    
    try:
        # Generar pregunta usando el tool
        message = ask_for_additional_filters.invoke({
            "current_filters_json": current_filters_json
        })
        
        print(f"✅ Mensaje generado: {message}")
        
        # Agregar mensaje al historial
        state.add_message("assistant", message)
        
    except Exception as e:
        print(f"❌ Error generando mensaje: {e}")
        
        # Fallback message
        message = "Perfecto, tengo toda la información básica. ¿Te gustaría agregar algún filtro adicional (como pet-friendly, balcón, terraza) o buscamos con estos criterios?"
        state.add_message("assistant", message)
        state.error_message = f"Error generando mensaje: {e}"
    
    # Activar flag de espera de confirmación
    state.awaiting_additional_filters_confirmation = True
    
    # Actualizar metadata
    state.current_node = "ask_additional_filters"
    
    print(f"🔔 Flag activado: awaiting_additional_filters_confirmation = True")
    
    return state