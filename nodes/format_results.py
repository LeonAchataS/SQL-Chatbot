"""
Nodo: format_results
Formatea los resultados de la búsqueda en un mensaje natural para el usuario
"""
from models.state import AgentState
from tools.property_tools import format_search_results_message
import json


def format_results_node(state: AgentState) -> AgentState:
    """
    Genera un mensaje final con los resultados de la búsqueda.
    Maneja tanto casos exitosos como errores.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con mensaje final
    """
    print(f"\n{'='*60}")
    print(f"📊 FORMAT RESULTS NODE")
    print(f"{'='*60}")
    
    # Caso 1: Si hubo error en validación o ejecución
    if state.error_message:
        print(f"⚠️ Hubo un error: {state.error_message}")
        
        error_messages = {
            "SQL inválido": "Lo siento, hubo un problema generando la búsqueda. ¿Podrías reformular tus criterios?",
            "Error ejecutando SQL": "Hubo un problema al buscar en la base de datos. Por favor, intenta de nuevo.",
            "No se generó SQL": "No pude generar la búsqueda. ¿Podrías proporcionar más detalles?"
        }
        
        # Buscar mensaje apropiado
        message = None
        for key, msg in error_messages.items():
            if key in state.error_message:
                message = msg
                break
        
        if not message:
            message = "Lo siento, hubo un problema con tu búsqueda. Por favor, intenta nuevamente."
        
        state.add_message("assistant", message)
        state.current_node = "format_results"
        return state
    
    # Caso 2: Búsqueda exitosa
    if state.query_executed and state.query_results is not None:
        properties_count = len(state.query_results)
        
        print(f"✅ Formateando resultados: {properties_count} propiedades")
        
        # Obtener filtros usados
        all_filters = state.filters.model_dump(exclude_none=True)
        filters_json = json.dumps(all_filters, ensure_ascii=False)
        
        try:
            # Generar mensaje usando el tool
            message = format_search_results_message.invoke({
                "filters_json": filters_json,
                "properties_count": properties_count
            })
            
            print(f"✅ Mensaje generado: {message}")
            
            # Agregar mensaje al historial
            state.add_message("assistant", message)
            
        except Exception as e:
            print(f"❌ Error formateando mensaje: {e}")
            
            # Fallback messages
            if properties_count == 0:
                message = "Lo siento, no encontré propiedades con esos criterios. ¿Quieres ajustar algún filtro?"
            elif properties_count == 1:
                message = "¡Encontré 1 departamento que cumple con tus criterios!"
            else:
                message = f"¡Encontré {properties_count} departamentos que cumplen con tus criterios! Puedes ver los detalles a continuación."
            
            state.add_message("assistant", message)
            state.error_message = f"Error formateando mensaje: {e}"
    
    else:
        print("⚠️ No hay resultados para formatear")
        state.add_message("assistant", "Hubo un problema procesando tu búsqueda. Por favor, intenta nuevamente.")
    
    # Actualizar metadata
    state.current_node = "format_results"
    
    print(f"\n{'='*60}")
    print(f"✅ FLUJO COMPLETADO")
    print(f"{'='*60}\n")
    
    return state