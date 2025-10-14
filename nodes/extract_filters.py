"""
Nodo: extract_filters
Extrae filtros de búsqueda del mensaje del usuario usando LLM
"""
from models.state import AgentState
from tools.property_tools import extract_property_filters
import json


def extract_filters_node(state: AgentState) -> AgentState:
    """
    Extrae filtros del último mensaje del usuario.
    Usa el tool extract_property_filters que emplea LLM para entender el mensaje.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con nuevos filtros extraídos
    """
    print(f"\n{'='*60}")
    print(f"🔍 EXTRACT FILTERS NODE")
    print(f"{'='*60}")
    
    # Obtener último mensaje del usuario
    last_message = None
    for msg in reversed(state.messages):
        if msg.get("role") == "user":
            last_message = msg.get("content", "")
            break
    
    if not last_message:
        print("⚠️ No se encontró mensaje del usuario")
        state.current_node = "extract_filters"
        return state
    
    print(f"Mensaje a analizar: '{last_message[:100]}...'")
    
    # Preparar filtros actuales como JSON
    current_filters = state.filters.model_dump(exclude_none=True)
    current_filters_json = json.dumps(current_filters, ensure_ascii=False)
    
    print(f"Filtros actuales: {current_filters}")
    
    # Llamar al tool para extraer filtros
    try:
        new_filters_json = extract_property_filters.invoke({
            "user_message": last_message,
            "current_filters_json": current_filters_json
        })
        
        # Parse respuesta
        new_filters = json.loads(new_filters_json)
        
        if new_filters:
            print(f"✅ Filtros extraídos: {new_filters}")
            
            # Actualizar state con nuevos filtros
            state.update_filters(**new_filters)
            
            # Log del estado actual
            print(f"📊 Estado de filtros esenciales: {state.filters.count_essential_filters()}/5")
            print(f"📊 Filtros opcionales: {state.filters.count_optional_filters()}")
        else:
            print("ℹ️ No se extrajeron filtros nuevos del mensaje")
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando respuesta del tool: {e}")
        state.error_message = f"Error extrayendo filtros: {e}"
    except Exception as e:
        print(f"❌ Error en extracción de filtros: {e}")
        state.error_message = f"Error: {e}"
    
    # Actualizar metadata
    state.current_node = "extract_filters"
    
    return state