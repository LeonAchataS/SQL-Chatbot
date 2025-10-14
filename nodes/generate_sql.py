"""
Nodo: generate_sql
Genera la consulta SQL basada en los filtros recopilados
"""
from models.state import AgentState
from tools.sql_tools import generate_property_sql
import json


def generate_sql_node(state: AgentState) -> AgentState:
    """
    Genera la consulta SQL SELECT para buscar propiedades.
    Usa el tool generate_property_sql que emplea LLM.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con SQL generado
    """
    print(f"\n{'='*60}")
    print(f"🔧 GENERATE SQL NODE")
    print(f"{'='*60}")
    
    # Obtener todos los filtros (esenciales + opcionales)
    all_filters = state.filters.model_dump(exclude_none=True)
    
    print(f"📋 Generando SQL con filtros:")
    for key, value in all_filters.items():
        print(f"  - {key}: {value}")
    
    # Convertir filtros a JSON
    filters_json = json.dumps(all_filters, ensure_ascii=False)
    
    try:
        # Generar SQL usando el tool
        sql_query = generate_property_sql.invoke({
            "filters_json": filters_json
        })
        
        print(f"\n✅ SQL Generado:")
        print(f"{'-'*60}")
        print(sql_query)
        print(f"{'-'*60}\n")
        
        # Guardar SQL en el state
        state.generated_sql = sql_query
        
    except Exception as e:
        print(f"❌ Error generando SQL: {e}")
        state.error_message = f"Error generando SQL: {e}"
        state.generated_sql = None
    
    # Actualizar metadata
    state.current_node = "generate_sql"
    
    return state