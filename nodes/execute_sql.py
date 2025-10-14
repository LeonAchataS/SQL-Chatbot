"""
Nodo: execute_sql
Ejecuta el SQL validado contra la base de datos PostgreSQL
"""
from models.state import AgentState
from tools.sql_tools import execute_property_sql
import json


async def execute_sql_node(state: AgentState) -> AgentState:
    """
    Ejecuta la consulta SQL validada contra la base de datos.
    Guarda los resultados en state.query_results.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con resultados de la query
    """
    print(f"\n{'='*60}")
    print(f"🚀 EXECUTE SQL NODE")
    print(f"{'='*60}")
    
    if not state.generated_sql:
        print("❌ No hay SQL para ejecutar")
        state.error_message = "No hay SQL generado"
        state.query_executed = False
        state.current_node = "execute_sql"
        return state
    
    if not state.sql_validated:
        print("❌ SQL no fue validado")
        state.error_message = "SQL no validado"
        state.query_executed = False
        state.current_node = "execute_sql"
        return state
    
    print(f"Ejecutando SQL:")
    print(f"{'-'*60}")
    print(state.generated_sql)
    print(f"{'-'*60}\n")
    
    try:
        # Ejecutar SQL usando el tool (que es async)
        result_json = await execute_property_sql.ainvoke({
            "query": state.generated_sql
        })
        
        # Parse resultado
        result = json.loads(result_json)
        
        if result.get("success"):
            properties = result.get("data", [])
            count = result.get("count", 0)
            
            print(f"✅ Query ejecutado exitosamente")
            print(f"📊 Propiedades encontradas: {count}")
            
            # Guardar resultados en el state
            state.query_results = properties
            state.query_executed = True
            
            # Log de primeros resultados (para debug)
            if count > 0:
                print(f"\n📋 Primera propiedad encontrada:")
                first_prop = properties[0]
                print(f"  - ID: {first_prop.get('id', 'N/A')}")
                print(f"  - Número: {first_prop.get('numero', 'N/A')}")
                print(f"  - Área: {first_prop.get('area', 'N/A')} m²")
                print(f"  - Dormitorios: {first_prop.get('dormitorios', 'N/A')}")
                print(f"  - Distrito: {first_prop.get('edificio_distrito', 'N/A')}")
                
                if count > 1:
                    print(f"  ... y {count - 1} más")
            else:
                print("ℹ️ No se encontraron propiedades con esos criterios")
                
        else:
            error_msg = result.get("error", "Error desconocido")
            print(f"❌ Error ejecutando query: {error_msg}")
            state.error_message = error_msg
            state.query_executed = False
            state.query_results = []
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando resultado: {e}")
        state.error_message = f"Error parseando resultado: {e}"
        state.query_executed = False
        state.query_results = []
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        state.error_message = f"Error ejecutando SQL: {e}"
        state.query_executed = False
        state.query_results = []
    
    # Actualizar metadata
    state.current_node = "execute_sql"
    
    return state