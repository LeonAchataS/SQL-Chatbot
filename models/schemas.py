"""
Schemas de Pydantic V2 para requests/responses de la API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# === REQUEST SCHEMAS ===

class ChatRequest(BaseModel):
    """Request para el endpoint /chat"""
    session_id: Optional[str] = Field(
        None,
        description="ID de sesión (si es None, se crea una nueva)"
    )
    message: str = Field(..., description="Mensaje del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Busco departamento en San Isidro"
            }
        }


# === RESPONSE SCHEMAS ===

class PropertyFiltersResponse(BaseModel):
    """Representación de filtros para responses"""
    # Esenciales
    distrito: Optional[str] = None
    area_min: Optional[float] = None
    estado_propiedad: Optional[str] = None
    monto_maximo: Optional[float] = None
    dormitorios: Optional[int] = None
    
    # Opcionales
    permite_mascotas: Optional[bool] = None
    balcon: Optional[bool] = None
    terraza: Optional[bool] = None
    amoblado: Optional[bool] = None
    banios: Optional[int] = None
    
    # Metadata
    essential_count: int = Field(..., description="Filtros esenciales completados")
    optional_count: int = Field(..., description="Filtros opcionales activos")
    is_complete: bool = Field(..., description="¿Filtros esenciales completos?")


class ChatResponse(BaseModel):
    """Response del endpoint /chat"""
    session_id: str = Field(..., description="ID de la sesión")
    response: str = Field(..., description="Respuesta del agente")
    filters: PropertyFiltersResponse = Field(..., description="Estado actual de filtros")
    ready_to_search: bool = Field(..., description="¿Listo para buscar propiedades?")
    properties_found: Optional[int] = Field(None, description="Número de propiedades encontradas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "¡Perfecto! ¿Cuál es el área mínima que buscas?",
                "filters": {
                    "distrito": "San Isidro",
                    "area_min": None,
                    "estado_propiedad": None,
                    "monto_maximo": None,
                    "dormitorios": None,
                    "permite_mascotas": None,
                    "balcon": None,
                    "terraza": None,
                    "amoblado": None,
                    "banios": None,
                    "essential_count": 1,
                    "optional_count": 0,
                    "is_complete": False
                },
                "ready_to_search": False,
                "properties_found": None
            }
        }


class PropertyResponse(BaseModel):
    """Schema para una propiedad individual"""
    id: str
    numero: str
    piso: Optional[int]
    tipo: str
    area: Optional[float]
    dormitorios: Optional[int]
    banios: Optional[int]
    balcon: bool
    terraza: bool
    amoblado: bool
    permite_mascotas: bool
    valor_comercial: Optional[float]
    mantenimiento_mensual: Optional[float]
    estado: str
    
    # Info del edificio (JOIN)
    edificio_nombre: Optional[str] = None
    edificio_direccion: Optional[str] = None
    edificio_distrito: Optional[str] = None


class PropertiesListResponse(BaseModel):
    """Response del endpoint /properties/{session_id}"""
    session_id: str
    count: int = Field(..., description="Número de propiedades encontradas")
    properties: List[PropertyResponse] = Field(..., description="Lista de propiedades")
    filters_used: PropertyFiltersResponse = Field(..., description="Filtros usados en la búsqueda")
    sql_query: Optional[str] = Field(None, description="SQL generado (solo para debug)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "count": 3,
                "properties": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "numero": "301",
                        "piso": 3,
                        "tipo": "DEPARTAMENTO",
                        "area": 85.5,
                        "dormitorios": 2,
                        "banios": 2,
                        "balcon": True,
                        "terraza": False,
                        "amoblado": False,
                        "permite_mascotas": True,
                        "valor_comercial": 450000.00,
                        "mantenimiento_mensual": 350.00,
                        "estado": "DISPONIBLE",
                        "edificio_nombre": "Torre San Isidro",
                        "edificio_direccion": "Av. República de Panamá 123",
                        "edificio_distrito": "San Isidro"
                    }
                ],
                "filters_used": {
                    "distrito": "San Isidro",
                    "area_min": 80.0,
                    "estado_propiedad": "DISPONIBLE",
                    "monto_maximo": 500000.0,
                    "dormitorios": 2,
                    "permite_mascotas": True,
                    "balcon": None,
                    "terraza": None,
                    "amoblado": None,
                    "banios": None,
                    "essential_count": 5,
                    "optional_count": 1,
                    "is_complete": True
                },
                "sql_query": "SELECT p.*, e.nombre as edificio_nombre..."
            }
        }


class ErrorResponse(BaseModel):
    """Response para errores"""
    error: str = Field(..., description="Mensaje de error")
    detail: Optional[str] = Field(None, description="Detalle del error")
    session_id: Optional[str] = Field(None, description="ID de sesión si aplica")