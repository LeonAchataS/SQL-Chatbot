"""
Tools para generar, validar y ejecutar SQL queries
"""
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import re
import json
from typing import List, Dict, Any
from models.settings import settings
from prompts.system_prompts import GENERATE_SQL_PROMPT
from db import db


# Inicializar LLM
llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=settings.openai_temperature,
    api_key=settings.openai_api_key
)


@tool
async def get_database_schema() -> str:
    """
    Obtiene el schema de las tablas propiedad y edificio desde la base de datos.
    
    Returns:
        String con la información del schema
    """
    print("📊 Obteniendo schema de la base de datos...")
    
    try:
        schema_info = await db.get_schema_info()
        print("✅ Schema obtenido exitosamente")
        return schema_info
    except Exception as e:
        print(f"❌ Error obteniendo schema: {e}")
        return f"Error obteniendo schema: {e}"


@tool
def generate_property_sql(filters_json: str) -> str:
    """
    Genera una consulta SQL SELECT para buscar propiedades basado en filtros.
    
    Args:
        filters_json: JSON string con los filtros de búsqueda
        
    Returns:
        Query SQL generado
    """
    print(f"🔧 Generando SQL con filtros: {filters_json[:100]}...")
    
    try:
        filters = json.loads(filters_json) if filters_json else {}
        
        # Construir prompt
        prompt = GENERATE_SQL_PROMPT.format(
            filters_json=json.dumps(filters, indent=2, ensure_ascii=False)
        )
        
        # Llamar al LLM
        response = llm.invoke(prompt)
        sql = response.content.strip()
        
        # Limpiar SQL (remover markdown)
        if sql.startswith("```sql"):
            sql = sql.replace("```sql", "").replace("```", "").strip()
        elif sql.startswith("```"):
            sql = sql.replace("```", "").strip()
        
        print(f"✅ SQL generado:\n{sql[:200]}...")
        return sql
        
    except Exception as e:
        print(f"❌ Error generando SQL: {e}")
        return f"Error: {e}"


@tool
def validate_sql_query(query: str) -> str:
    """
    Valida la seguridad y sintaxis de una consulta SQL.
    
    Args:
        query: Query SQL a validar
        
    Returns:
        JSON con {"valid": true/false, "error": mensaje, "clean_query": query limpio}
    """
    print(f"🔍 Validando SQL: {query[:100]}...")
    
    result = {"valid": False, "error": None, "clean_query": None}
    
    try:
        # Limpiar query
        clean_query = query.strip()
        
        # Remover markdown si existe
        clean_query = re.sub(r'```sql\s*', '', clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r'```\s*', '', clean_query)
        clean_query = clean_query.strip()
        
        # Remover punto y coma final si existe
        if clean_query.endswith(";"):
            clean_query = clean_query[:-1].strip()
        
        # Validación 1: Debe ser SELECT
        if not clean_query.upper().startswith("SELECT"):
            result["error"] = "Solo se permiten queries SELECT"
            print(f"❌ {result['error']}")
            return json.dumps(result, ensure_ascii=False)
        
        # Validación 2: No múltiples statements
        if clean_query.count(";") > 0:
            result["error"] = "No se permiten múltiples statements"
            print(f"❌ {result['error']}")
            return json.dumps(result, ensure_ascii=False)
        
        # Validación 3: Bloquear operaciones peligrosas
        dangerous_patterns = [
            r'\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|REPLACE|TRUNCATE)\b',
            r'\b(EXEC|EXECUTE)\b',
            r'--',  # SQL comments
            r'/\*',  # Block comments
            r'\bINTO\s+OUTFILE\b',
            r'\bLOAD_FILE\b'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, clean_query, re.IGNORECASE):
                result["error"] = "Query contiene operaciones no permitidas"
                print(f"❌ {result['error']}: patrón {pattern}")
                return json.dumps(result, ensure_ascii=False)
        
        # Validación 4: Debe tener FROM
        if not re.search(r'\bFROM\b', clean_query, re.IGNORECASE):
            result["error"] = "Query debe tener cláusula FROM"
            print(f"❌ {result['error']}")
            return json.dumps(result, ensure_ascii=False)
        
        # Validación 5: Solo un SELECT
        select_count = len(re.findall(r'\bSELECT\b', clean_query, re.IGNORECASE))
        if select_count > 1:
            # Permitir subqueries, pero validar que no sean maliciosos
            pass
        
        # Validación 6: Verificar paréntesis balanceados
        if clean_query.count('(') != clean_query.count(')'):
            result["error"] = "Paréntesis desbalanceados"
            print(f"❌ {result['error']}")
            return json.dumps(result, ensure_ascii=False)
        
        # Validación 7: Debe tener LIMIT
        if not re.search(r'\bLIMIT\b', clean_query, re.IGNORECASE):
            # Agregar LIMIT automáticamente
            clean_query += f"\nLIMIT {settings.properties_limit}"
            print(f"⚠️ LIMIT agregado automáticamente: {settings.properties_limit}")
        
        # Si pasó todas las validaciones
        result["valid"] = True
        result["clean_query"] = clean_query
        print("✅ Query validado exitosamente")
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        result["error"] = f"Error en validación: {str(e)}"
        print(f"❌ {result['error']}")
        return json.dumps(result, ensure_ascii=False)


@tool
async def execute_property_sql(query: str) -> str:
    """
    Ejecuta una consulta SQL validada y retorna los resultados.
    
    Args:
        query: Query SQL validado para ejecutar
        
    Returns:
        JSON string con los resultados o error
    """
    print(f"🚀 Ejecutando SQL: {query[:100]}...")
    
    try:
        # Ejecutar query
        results = await db.fetch_all(query)
        
        # Convertir resultados a JSON serializable
        # asyncpg retorna objetos Record, necesitamos convertir a dict
        serializable_results = []
        for row in results:
            row_dict = {}
            for key, value in row.items():
                # Convertir tipos especiales a strings serializables
                if hasattr(value, 'isoformat'):  # datetime, date
                    row_dict[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    row_dict[key] = value
                else:
                    row_dict[key] = str(value)
            serializable_results.append(row_dict)
        
        result = {
            "success": True,
            "count": len(serializable_results),
            "data": serializable_results
        }
        
        print(f"✅ Query ejecutado: {len(serializable_results)} resultados")
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "count": 0,
            "data": []
        }
        print(f"❌ Error ejecutando query: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def fix_sql_error(original_query: str, error_message: str, filters_json: str) -> str:
    """
    Intenta corregir un query SQL que falló.
    
    Args:
        original_query: Query original que falló
        error_message: Mensaje de error recibido
        filters_json: Filtros originales para regenerar
        
    Returns:
        Nuevo query SQL corregido
    """
    print(f"🔧 Intentando corregir SQL. Error: {error_message[:100]}...")
    
    try:
        filters = json.loads(filters_json) if filters_json else {}
        
        fix_prompt = f"""El siguiente SQL falló con error:

Query original:
{original_query}

Error:
{error_message}

Filtros de búsqueda:
{json.dumps(filters, indent=2, ensure_ascii=False)}

Schema:
- Tabla: property_infrastructure.propiedad
- Tabla relacionada: property_infrastructure.edificio
- JOIN necesario: propiedad.edificio_id = edificio.id

Analiza el error y genera un SQL corregido que:
1. Solucione el problema específico del error
2. Use los filtros correctamente
3. Mantenga la estructura básica: SELECT con JOIN
4. Incluya LIMIT 5

Genera SOLO el SQL corregido, sin explicaciones.
"""
        
        response = llm.invoke(fix_prompt)
        fixed_sql = response.content.strip()
        
        # Limpiar SQL
        if fixed_sql.startswith("```sql"):
            fixed_sql = fixed_sql.replace("```sql", "").replace("```", "").strip()
        elif fixed_sql.startswith("```"):
            fixed_sql = fixed_sql.replace("```", "").strip()
        
        print(f"✅ SQL corregido generado")
        return fixed_sql
        
    except Exception as e:
        print(f"❌ Error corrigiendo SQL: {e}")
        return original_query  # Retornar original si falla la corrección