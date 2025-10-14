"""
Configuración del sistema usando Pydantic V2
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env explícitamente antes de crear Settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Settings(BaseSettings):
    """Configuración principal del sistema."""
    
    # === OpenAI API ===
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="Modelo de OpenAI a usar")
    openai_temperature: float = Field(default=0, description="Temperatura del modelo")
    
    # === PostgreSQL Database ===
    database_url: str = Field(
        ..., 
        description="PostgreSQL connection string (postgresql://user:pass@host:port/dbname)"
    )
    database_schema: str = Field(
        default="property_infrastructure",
        description="Schema de la base de datos"
    )
    
    # Pool de conexiones
    db_pool_min_size: int = Field(default=5, description="Tamaño mínimo del pool")
    db_pool_max_size: int = Field(default=20, description="Tamaño máximo del pool")
    db_command_timeout: int = Field(default=60, description="Timeout para comandos en segundos")
    
    # === Configuración del Agente ===
    max_optional_filters: int = Field(default=3, description="Máximo de filtros opcionales")
    properties_limit: int = Field(default=5, description="Límite de propiedades a retornar")
    
    # === Sesiones ===
    session_timeout: int = Field(default=3600, description="Timeout de sesión en segundos (1 hora)")
    
    # === API Configuration ===
    api_host: str = Field(default="0.0.0.0", description="Host de la API")
    api_port: int = Field(default=8000, description="Puerto de la API")
    api_reload: bool = Field(default=False, description="Auto-reload en desarrollo")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix=""  # Sin prefijo en las variables
    )


# Instancia global de configuración
settings = Settings()