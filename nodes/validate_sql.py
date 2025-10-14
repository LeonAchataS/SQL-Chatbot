"""
Nodo: validate_sql
Valida la seguridad del SQL generado y lo corrige si falla
"""
from models.state import AgentState
from tools.sql_tools import validate_sql_query, fix_sql_error
from typing import Literal
import json


def validate_sql_node(state: AgentState) -> AgentState:
    """
    Valida el SQL generado por seguridad y sintaxis.
    Si falla, intenta corregirlo (máximo 3 intentos).
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con SQL validado o error
    """
    print(f"\n{'='*60}")
    print(f"🔍 VALIDATE SQL NODE")
    print(f"{'='*60}")
    
    if not state.generated_sql:
        print("❌ No hay SQL para validar")
        state.error_message = "No se generó SQL"
        state.sql_validated = False
        state.current_node = "validate_sql"
        return state
    
    # Intentar validar (con reintentos si falla)
    max_attempts = 3
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"\n🔄 Intento de validación #{attempt}")
        
        try:
            # Validar SQL
            validation_result_json = validate_sql_query.invoke({
                "query": state.generated_sql
            })
            
            validation_result = json.loads(validation_result_json)
            
            if validation_result.get("valid"):
                print("✅ SQL validado exitosamente")
                
                # Usar el query limpio
                clean_query = validation_result.get("clean_query", state.generated_sql)
                state.generated_sql = clean_query
                state.sql_validated = True
                
                print(f"SQL limpio y validado:")
                print(f"{'-'*60}")
                print(clean_query)
                print(f"{'-'*60}")
                
                break
            else:
                error_msg = validation_result.get("error", "Error desconocido")
                print(f"❌ Validación falló: {error_msg}")
                
                if attempt < max_attempts:
                    print(f"🔧 Intentando corregir SQL...")
                    
                    # Obtener filtros para regenerar
                    all_filters = state.filters.model_dump(exclude_none=True)
                    filters_json = json.dumps(all_filters, ensure_ascii=False)
                    
                    # Intentar corregir
                    fixed_sql = fix_sql_error.invoke({
                        "original_query": state.generated_sql,
                        "error_message": error_msg,
                        "filters_json": filters_json
                    })
                    
                    print(f"SQL corregido generado")
                    state.generated_sql = fixed_sql
                    attempt += 1
                else:
                    print(f"❌ No se pudo validar después de {max_attempts} intentos")
                    state.sql_validated = False
                    state.error_message = f"SQL inválido: {error_msg}"
                    break
                    
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando resultado de validación: {e}")
            state.sql_validated = False
            state.error_message = f"Error en validación: {e}"
            break
        except Exception as e:
            print(f"❌ Error en validación: {e}")
            state.sql_validated = False
            state.error_message = f"Error: {e}"
            break
    
    # Actualizar metadata
    state.current_node = "validate_sql"
    
    return state


def route_after_validate_sql(state: AgentState) -> Literal["execute_sql", "format_results"]:
    """
    Función de routing después de validate_sql.
    Si validó correctamente, ejecuta. Si falló, va directo a format_results con error.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Nombre del siguiente nodo
    """
    if state.sql_validated:
        print("➡️ Routing: SQL válido → execute_sql")
        return "execute_sql"
    else:
        print("➡️ Routing: SQL inválido → format_results (con error)")
        return "format_results"