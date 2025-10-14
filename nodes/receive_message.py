"""
Nodo: receive_message
Punto de entrada - Recibe el mensaje del usuario y lo agrega al state
"""
from models.state import AgentState


def receive_message_node(state: AgentState) -> AgentState:
    """
    Recibe el mensaje del usuario y lo procesa.
    Este es el primer nodo del grafo.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con el mensaje agregado
    """
    print(f"\n{'='*60}")
    print(f"📨 RECEIVE MESSAGE NODE")
    print(f"{'='*60}")
    
    # El mensaje ya debería estar en state.messages (agregado por la API)
    if state.messages:
        last_message = state.messages[-1]
        print(f"User: {last_message.get('content', '')[:100]}...")
    
    # Actualizar metadata
    state.current_node = "receive_message"
    
    print(f"✅ Mensaje recibido y procesado")
    print(f"Total mensajes en conversación: {len(state.messages)}")
    
    return state