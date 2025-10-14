"""
Tools para extraer y manejar filtros de propiedades
"""
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional
import json
from models.settings import settings
from prompts.system_prompts import (
    EXTRACT_FILTERS_PROMPT,
    MISSING_FILTER_QUESTION_PROMPT,
    ASK_ADDITIONAL_FILTERS_PROMPT,
    FORMAT_RESULTS_PROMPT
)


# Inicializar LLM
llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=settings.openai_temperature,
    api_key=settings.openai_api_key
)


@tool
def extract_property_filters(user_message: str, current_filters_json: str) -> str:
    """
    Extrae filtros de búsqueda de propiedades del mensaje del usuario.
    
    Args:
        user_message: Mensaje del usuario
        current_filters_json: JSON string con filtros ya recopilados
        
    Returns:
        JSON string con los nuevos filtros extraídos
    """
    print(f"🔍 Extrayendo filtros de: '{user_message[:50]}...'")
    
    try:
        # Parse current filters
        current_filters = json.loads(current_filters_json) if current_filters_json else {}
        
        # Construir prompt
        prompt = EXTRACT_FILTERS_PROMPT.format(
            user_message=user_message,
            current_filters=json.dumps(current_filters, indent=2, ensure_ascii=False)
        )
        
        # Llamar al LLM
        response = llm.invoke(prompt)
        extracted = response.content.strip()
        
        # Limpiar respuesta (remover markdown si existe)
        if extracted.startswith("```json"):
            extracted = extracted.replace("```json", "").replace("```", "").strip()
        elif extracted.startswith("```"):
            extracted = extracted.replace("```", "").strip()
        
        # Validar que sea JSON válido
        parsed = json.loads(extracted)
        
        print(f"✅ Filtros extraídos: {parsed}")
        return json.dumps(parsed, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        print(f"Respuesta del LLM: {extracted}")
        return "{}"
    except Exception as e:
        print(f"❌ Error extrayendo filtros: {e}")
        return "{}"


@tool
def generate_missing_filter_question(missing_filter: str, current_filters_json: str) -> str:
    """
    Genera una pregunta conversacional para solicitar un filtro faltante.
    
    Args:
        missing_filter: Nombre del filtro que falta (ej: 'distrito', 'area_min')
        current_filters_json: JSON string con filtros ya recopilados
        
    Returns:
        Pregunta generada como string
    """
    print(f"❓ Generando pregunta para filtro faltante: {missing_filter}")
    
    try:
        current_filters = json.loads(current_filters_json) if current_filters_json else {}
        
        # Construir prompt
        prompt = MISSING_FILTER_QUESTION_PROMPT.format(
            missing_filter=missing_filter,
            current_filters=json.dumps(current_filters, indent=2, ensure_ascii=False)
        )
        
        # Llamar al LLM
        response = llm.invoke(prompt)
        question = response.content.strip()
        
        print(f"✅ Pregunta generada: {question}")
        return question
        
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
        return fallback_questions.get(missing_filter, f"¿Podrías especificar {missing_filter}?")


@tool
def ask_for_additional_filters(current_filters_json: str) -> str:
    """
    Genera un mensaje preguntando si el usuario quiere agregar filtros opcionales.
    
    Args:
        current_filters_json: JSON string con filtros esenciales ya completos
        
    Returns:
        Mensaje preguntando por filtros adicionales
    """
    print("💬 Generando pregunta por filtros adicionales")
    
    try:
        current_filters = json.loads(current_filters_json) if current_filters_json else {}
        
        # Construir prompt
        prompt = ASK_ADDITIONAL_FILTERS_PROMPT.format(
            current_filters=json.dumps(current_filters, indent=2, ensure_ascii=False)
        )
        
        # Llamar al LLM
        response = llm.invoke(prompt)
        message = response.content.strip()
        
        print(f"✅ Mensaje generado: {message}")
        return message
        
    except Exception as e:
        print(f"❌ Error generando mensaje: {e}")
        return "Perfecto, tengo toda la información básica. ¿Te gustaría agregar algún filtro adicional (como pet-friendly, balcón, terraza) o buscamos con estos criterios?"


@tool
def format_search_results_message(filters_json: str, properties_count: int) -> str:
    """
    Genera un mensaje informando sobre los resultados de la búsqueda.
    
    Args:
        filters_json: JSON string con los filtros usados
        properties_count: Número de propiedades encontradas
        
    Returns:
        Mensaje formateado sobre los resultados
    """
    print(f"📊 Formateando mensaje de resultados: {properties_count} propiedades")
    
    try:
        filters = json.loads(filters_json) if filters_json else {}
        
        # Construir prompt
        prompt = FORMAT_RESULTS_PROMPT.format(
            filters_json=json.dumps(filters, indent=2, ensure_ascii=False),
            count=properties_count
        )
        
        # Llamar al LLM
        response = llm.invoke(prompt)
        message = response.content.strip()
        
        print(f"✅ Mensaje generado: {message}")
        return message
        
    except Exception as e:
        print(f"❌ Error formateando mensaje: {e}")
        # Fallback messages
        if properties_count == 0:
            return "Lo siento, no encontré propiedades con esos criterios. ¿Quieres ajustar algún filtro?"
        elif properties_count == 1:
            return "¡Encontré 1 departamento que cumple con tus criterios!"
        else:
            return f"¡Encontré {properties_count} departamentos que cumplen con tus criterios! Puedes ver los detalles a continuación."


@tool
def validate_filter_value(filter_name: str, filter_value: str) -> str:
    """
    Valida y normaliza un valor de filtro específico.
    
    Args:
        filter_name: Nombre del filtro (ej: 'distrito', 'dormitorios')
        filter_value: Valor a validar
        
    Returns:
        JSON con {"valid": true/false, "normalized_value": valor, "error": mensaje}
    """
    print(f"✔️ Validando {filter_name} = {filter_value}")
    
    try:
        result = {"valid": True, "normalized_value": None, "error": None}
        
        # Validaciones específicas por tipo
        if filter_name == "distrito":
            # Capitalizar
            result["normalized_value"] = filter_value.title()
            
        elif filter_name == "area_min":
            # Convertir a float
            try:
                value = float(str(filter_value).replace("m2", "").replace("m²", "").strip())
                if value <= 0:
                    result["valid"] = False
                    result["error"] = "El área debe ser mayor a 0"
                else:
                    result["normalized_value"] = value
            except ValueError:
                result["valid"] = False
                result["error"] = "El área debe ser un número válido"
                
        elif filter_name == "estado_propiedad":
            # Validar estados válidos
            valid_states = ["DISPONIBLE", "OCUPADA", "MANTENIMIENTO", "VENDIDA"]
            normalized = filter_value.upper()
            if normalized in valid_states:
                result["normalized_value"] = normalized
            else:
                result["valid"] = False
                result["error"] = f"Estado debe ser uno de: {', '.join(valid_states)}"
                
        elif filter_name == "monto_maximo":
            # Convertir a float
            try:
                # Remover símbolos y convertir abreviaciones
                value_str = str(filter_value).replace("$", "").replace(",", "").strip()
                if "k" in value_str.lower():
                    value = float(value_str.lower().replace("k", "")) * 1000
                elif "mil" in value_str.lower():
                    value = float(value_str.lower().replace("mil", "").strip()) * 1000
                else:
                    value = float(value_str)
                    
                if value <= 0:
                    result["valid"] = False
                    result["error"] = "El monto debe ser mayor a 0"
                else:
                    result["normalized_value"] = value
            except ValueError:
                result["valid"] = False
                result["error"] = "El monto debe ser un número válido"
                
        elif filter_name in ["dormitorios", "banios"]:
            # Convertir a int
            try:
                value = int(filter_value)
                if value <= 0:
                    result["valid"] = False
                    result["error"] = "Debe ser mayor a 0"
                else:
                    result["normalized_value"] = value
            except ValueError:
                result["valid"] = False
                result["error"] = "Debe ser un número entero válido"
                
        elif filter_name in ["permite_mascotas", "balcon", "terraza", "amoblado"]:
            # Convertir a boolean
            value_lower = str(filter_value).lower()
            if value_lower in ["true", "sí", "si", "yes", "1"]:
                result["normalized_value"] = True
            elif value_lower in ["false", "no", "0"]:
                result["normalized_value"] = False
            else:
                result["valid"] = False
                result["error"] = "Debe ser sí/no"
        else:
            result["normalized_value"] = filter_value
            
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        print(f"❌ Error validando filtro: {e}")
        return json.dumps({"valid": False, "error": str(e)}, ensure_ascii=False)