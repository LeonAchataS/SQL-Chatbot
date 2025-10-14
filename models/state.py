"""
Estado del agente - Mantiene contexto entre mensajes
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PropertyFilters(BaseModel):
    """Filtros de búsqueda de propiedades que el usuario va completando."""
    
    # === FILTROS ESENCIALES (5 requeridos) ===
    distrito: Optional[str] = Field(None, description="Distrito del edificio")
    area_min: Optional[float] = Field(None, description="Área mínima en m2")
    estado_propiedad: Optional[str] = Field(None, description="Estado: DISPONIBLE, OCUPADA, MANTENIMIENTO, VENDIDA")
    monto_maximo: Optional[float] = Field(None, description="Presupuesto máximo")
    dormitorios: Optional[int] = Field(None, description="Número de dormitorios")
    
    # === FILTROS OPCIONALES (máximo 3) ===
    permite_mascotas: Optional[bool] = Field(None, description="Pet-friendly")
    balcon: Optional[bool] = Field(None, description="Tiene balcón")
    terraza: Optional[bool] = Field(None, description="Tiene terraza")
    amoblado: Optional[bool] = Field(None, description="Está amoblado")
    banios: Optional[int] = Field(None, description="Número de baños")
    
    def count_essential_filters(self) -> int:
        """Cuenta cuántos filtros esenciales están completos."""
        essential = [
            self.distrito,
            self.area_min,
            self.estado_propiedad,
            self.monto_maximo,
            self.dormitorios
        ]
        return sum(1 for f in essential if f is not None)
    
    def count_optional_filters(self) -> int:
        """Cuenta cuántos filtros opcionales están activos."""
        optional = [
            self.permite_mascotas,
            self.balcon,
            self.terraza,
            self.amoblado,
            self.banios
        ]
        return sum(1 for f in optional if f is not None)
    
    def get_missing_essential_filters(self) -> List[str]:
        """Retorna lista de filtros esenciales que faltan."""
        missing = []
        if self.distrito is None:
            missing.append("distrito")
        if self.area_min is None:
            missing.append("area_min")
        if self.estado_propiedad is None:
            missing.append("estado_propiedad")
        if self.monto_maximo is None:
            missing.append("monto_maximo")
        if self.dormitorios is None:
            missing.append("dormitorios")
        return missing
    
    def is_complete(self) -> bool:
        """Verifica si todos los filtros esenciales están completos."""
        return self.count_essential_filters() == 5


class AgentState(BaseModel):
    """Estado completo del agente - Se mantiene entre mensajes."""
    
    # === Identificación ===
    session_id: str = Field(..., description="ID único de la sesión")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # === Historial Conversacional ===
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Historial de mensajes: [{'role': 'user/assistant', 'content': '...'}]"
    )
    
    # === Filtros del Usuario ===
    filters: PropertyFilters = Field(
        default_factory=PropertyFilters,
        description="Filtros de búsqueda acumulados"
    )
    
    # === Control de Flujo ===
    essential_filters_complete: bool = Field(
        default=False,
        description="Flag: ¿Se completaron los 5 filtros esenciales?"
    )
    awaiting_additional_filters_confirmation: bool = Field(
        default=False,
        description="Flag: ¿Esperando respuesta sobre agregar filtros opcionales?"
    )
    collecting_optional_filters: bool = Field(
        default=False,
        description="Flag: ¿Estamos recolectando filtros opcionales?"
    )
    ready_to_search: bool = Field(
        default=False,
        description="Flag: ¿Listo para ejecutar búsqueda?"
    )
    
    # === SQL y Resultados ===
    generated_sql: Optional[str] = Field(None, description="SQL generado")
    sql_validated: bool = Field(default=False, description="¿SQL validado?")
    query_executed: bool = Field(default=False, description="¿Query ejecutado?")
    query_results: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Resultados de la búsqueda (limit 5)"
    )
    
    # === Metadata ===
    current_node: Optional[str] = Field(None, description="Nodo actual del grafo")
    error_message: Optional[str] = Field(None, description="Mensaje de error si ocurre")
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_message(self, role: str, content: str):
        """Agrega un mensaje al historial."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now()
    
    def update_filters(self, **kwargs):
        """Actualiza filtros y recalcula flags."""
        for key, value in kwargs.items():
            if hasattr(self.filters, key) and value is not None:
                setattr(self.filters, key, value)
        
        # Recalcular flag de completitud
        self.essential_filters_complete = self.filters.is_complete()
        self.last_updated = datetime.now()
    
    def get_next_missing_filter(self) -> Optional[str]:
        """Retorna el siguiente filtro esencial que falta."""
        missing = self.filters.get_missing_essential_filters()
        return missing[0] if missing else None