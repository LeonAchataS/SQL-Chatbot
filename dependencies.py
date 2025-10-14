"""
Dependencias de FastAPI
"""
from fastapi import Header, HTTPException
from typing import Optional


async def verify_session_id(session_id: Optional[str] = None) -> str:
    """
    Verifica que el session_id sea válido (básico por ahora).
    Puede expandirse para validaciones más complejas.
    
    Args:
        session_id: ID de sesión desde el request
        
    Returns:
        session_id validado
        
    Raises:
        HTTPException si es inválido
    """
    if session_id and len(session_id) > 200:
        raise HTTPException(
            status_code=400,
            detail="session_id demasiado largo"
        )
    
    return session_id


async def get_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """
    Dependency opcional para validar API key en headers.
    Por ahora no se usa, pero está lista para producción.
    
    Args:
        x_api_key: API key desde headers
        
    Returns:
        API key si es válida
    """
    # TODO: Implementar validación de API key si se requiere
    # if x_api_key != "tu_api_key_secreta":
    #     raise HTTPException(status_code=401, detail="API key inválida")
    
    return x_api_key