"""
Nodo: ask_missing_filter
Genera pregunta para el siguiente filtro esencial faltante
"""
from models.state import AgentState
from tools.property_tools import generate_missing_filter_question
import json


def ask_missing_filter_node(state: AgentState) -> AgentState:
    """
    Genera una pregunta conversacional para solicitar el siguiente filtro faltante.
    Este nodo termina el flujo esperando respuesta del usuario.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con pregunta generada
    """
    print(state)
    print(f"\n{'='*60}")
    print(f"❓ ASK MISSING FILTER NODE")
    print(f"{'='*60}")
    
    # Obtener el siguiente filtro que falta
    next_missing = state.get_next_missing_filter()
    
    if not next_missing:
        print("⚠️ No hay filtros faltantes (esto no debería ocurrir)")
        state.add_message("assistant", "Parece que ya tenemos toda la información necesaria.")
        state.current_node = "ask_missing_filter"
        return state
    
    print(f"Filtro faltante: {next_missing}")
    
    # Preparar filtros actuales
    current_filters = state.filters.model_dump(exclude_none=True)
    current_filters_json = json.dumps(current_filters, ensure_ascii=False)
    
    try:
        # Generar pregunta usando el tool
        question = generate_missing_filter_question.invoke({
            "missing_filter": next_missing,
            "current_filters_json": current_filters_json
        })
        
        print(f"✅ Pregunta generada: {question}")
        
        # Agregar pregunta al historial
        state.add_message("assistant", question)
        
    except Exception as e:
        print(f"❌ Error generando pregunta: {e}")
        
        # Fallback a preguntas predefinidas
        fallback_questions = {
            "distrito": "¿En qué distrito te gustaría buscar?",
            "area_min": "¿Cuál es el área mínima que necesitas (en m²)?",
            "estado_propiedad": "¿Qué estado prefieres? ¿Disponible, en construcción o con planos?",
            "monto_maximo": "¿Cuál es tu presupuesto máximo?",
            "dormitorios": "¿Cuántos dormitorios necesitas?"
        }
        
        question = fallback_questions.get(next_missing, f"¿Podrías especificar {next_missing}?")
        state.add_message("assistant", question)
        state.error_message = f"Error generando pregunta: {e}"
    
    # Actualizar metadata
    state.current_node = "ask_missing_filter"
    
    return state