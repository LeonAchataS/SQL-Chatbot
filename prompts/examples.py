"""
Few-shot examples para mejorar la extracción de filtros y generación de SQL
"""

# ============================================================================
# EXAMPLES DE EXTRACCIÓN DE FILTROS
# ============================================================================

FILTER_EXTRACTION_EXAMPLES = [
    {
        "user_message": "Busco en San Isidro de 2 dormitorios",
        "current_filters": {},
        "output": {
            "distrito": "San Isidro",
            "dormitorios": 2
        }
    },
    {
        "user_message": "Máximo 500 mil soles",
        "current_filters": {"distrito": "Miraflores"},
        "output": {
            "monto_maximo": 500000.0
        }
    },
    {
        "user_message": "Que acepte mascotas y tenga balcón",
        "current_filters": {"distrito": "Surco", "dormitorios": 3},
        "output": {
            "permite_mascotas": True,
            "balcon": True
        }
    },
    {
        "user_message": "80 metros cuadrados mínimo",
        "current_filters": {},
        "output": {
            "area_min": 80.0
        }
    },
    {
        "user_message": "Disponible y terminado",
        "current_filters": {"distrito": "San Isidro"},
        "output": {
            "estado_propiedad": "DISPONIBLE"
        }
    },
    {
        "user_message": "pet friendly con terraza",
        "current_filters": {},
        "output": {
            "permite_mascotas": True,
            "terraza": True
        }
    },
    {
        "user_message": "3 habitaciones y 2 baños",
        "current_filters": {},
        "output": {
            "dormitorios": 3,
            "banios": 2
        }
    }
]

# ============================================================================
# EXAMPLES DE CONVERSACIONES COMPLETAS
# ============================================================================

CONVERSATION_EXAMPLES = [
    {
        "title": "Conversación típica - Filtros completos",
        "messages": [
            {"role": "user", "content": "Hola, busco departamento"},
            {"role": "assistant", "content": "¡Hola! Encantado de ayudarte. ¿En qué distrito de Lima te gustaría buscar?"},
            {"role": "user", "content": "San Isidro"},
            {"role": "assistant", "content": "Perfecto. ¿Cuál es el área mínima que necesitas en m²?"},
            {"role": "user", "content": "80 metros"},
            {"role": "assistant", "content": "Entendido. ¿Qué estado prefieres? ¿Disponible, en construcción o con planos?"},
            {"role": "user", "content": "Disponible"},
            {"role": "assistant", "content": "¿Cuál es tu presupuesto máximo?"},
            {"role": "user", "content": "500 mil"},
            {"role": "assistant", "content": "¿Cuántos dormitorios necesitas?"},
            {"role": "user", "content": "2"},
            {"role": "assistant", "content": "Perfecto, tengo toda la información básica. ¿Te gustaría agregar algún filtro adicional como pet-friendly, balcón o terraza?"},
            {"role": "user", "content": "Sí, que acepte mascotas"},
            {"role": "assistant", "content": "Listo. ¿Algo más o busco con estos criterios?"},
            {"role": "user", "content": "Búscalo así"},
            {"role": "assistant", "content": "¡Encontré 3 departamentos que cumplen con tus criterios! Puedes ver los detalles a continuación."}
        ]
    },
    {
        "title": "Conversación - Usuario da varios datos a la vez",
        "messages": [
            {"role": "user", "content": "Busco en Miraflores, 3 dormitorios, máximo 700k"},
            {"role": "assistant", "content": "¡Excelente! Ya tengo distrito, dormitorios y presupuesto. ¿Cuál es el área mínima que buscas?"},
            {"role": "user", "content": "100 metros mínimo"},
            {"role": "assistant", "content": "Perfecto. ¿Qué estado prefieres para el inmueble?"},
            {"role": "user", "content": "Disponible"},
            {"role": "assistant", "content": "Genial, tengo todos los datos básicos. ¿Quieres agregar filtros opcionales o buscamos así?"},
            {"role": "user", "content": "Así está bien"},
            {"role": "assistant", "content": "¡Perfecto! Encontré 5 propiedades que coinciden con tu búsqueda."}
        ]
    },
    {
        "title": "Conversación - Sin resultados",
        "messages": [
            {"role": "user", "content": "Busco en Barranco, 4 dormitorios, 50m2, máximo 200k"},
            {"role": "assistant", "content": "Entiendo. ¿Qué estado buscas?"},
            {"role": "user", "content": "Disponible"},
            {"role": "assistant", "content": "Tengo todos los datos. ¿Algún filtro adicional?"},
            {"role": "user", "content": "No, búscalo"},
            {"role": "assistant", "content": "Lo siento, no encontré propiedades con esos criterios. ¿Quieres ajustar el área o el presupuesto?"}
        ]
    }
]

# ============================================================================
# EXAMPLES DE SQL GENERADO
# ============================================================================

SQL_GENERATION_EXAMPLES = [
    {
        "filters": {
            "distrito": "San Isidro",
            "area_min": 80.0,
            "estado_propiedad": "DISPONIBLE",
            "monto_maximo": 500000.0,
            "dormitorios": 2
        },
        "sql": """SELECT 
    p.*,
    e.nombre as edificio_nombre,
    e.direccion as edificio_direccion,
    e.distrito as edificio_distrito
FROM property_infrastructure.propiedad p
JOIN property_infrastructure.edificio e ON p.edificio_id = e.id
WHERE 
    e.distrito = 'San Isidro'
    AND p.area >= 80
    AND p.estado = 'DISPONIBLE'
    AND p.valor_comercial <= 500000
    AND p.dormitorios = 2
LIMIT 5;"""
    },
    {
        "filters": {
            "distrito": "Miraflores",
            "area_min": 100.0,
            "estado_propiedad": "DISPONIBLE",
            "monto_maximo": 700000.0,
            "dormitorios": 3,
            "permite_mascotas": True,
            "balcon": True
        },
        "sql": """SELECT 
    p.*,
    e.nombre as edificio_nombre,
    e.direccion as edificio_direccion,
    e.distrito as edificio_distrito
FROM property_infrastructure.propiedad p
JOIN property_infrastructure.edificio e ON p.edificio_id = e.id
WHERE 
    e.distrito = 'Miraflores'
    AND p.area >= 100
    AND p.estado = 'DISPONIBLE'
    AND p.valor_comercial <= 700000
    AND p.dormitorios = 3
    AND p.permite_mascotas = true
    AND p.balcon = true
LIMIT 5;"""
    }
]

# ============================================================================
# HELPER FUNCTION PARA FORMATEAR EXAMPLES
# ============================================================================

def format_extraction_examples() -> str:
    """Formatea los examples de extracción para incluir en prompts."""
    formatted = "\n\nEXAMPLES:\n"
    for i, example in enumerate(FILTER_EXTRACTION_EXAMPLES[:3], 1):  # Solo primeros 3
        formatted += f"\nExample {i}:\n"
        formatted += f"User: \"{example['user_message']}\"\n"
        formatted += f"Current filters: {example['current_filters']}\n"
        formatted += f"Output: {example['output']}\n"
    return formatted


def format_sql_examples() -> str:
    """Formatea los examples de SQL para incluir en prompts."""
    formatted = "\n\nEXAMPLES:\n"
    for i, example in enumerate(SQL_GENERATION_EXAMPLES, 1):
        formatted += f"\nExample {i}:\n"
        formatted += f"Filters: {example['filters']}\n"
        formatted += f"SQL:\n{example['sql']}\n"
    return formatted