// ============================================================================
// CONFIGURACIÓN
// ============================================================================

const API_URL = 'http://localhost:8000';
const SESSION_KEY = 'chatbot_session_id';

// ============================================================================
// ELEMENTOS DEL DOM
// ============================================================================

const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');
const sessionStatus = document.getElementById('session-status');
const loading = document.getElementById('loading');
const propertiesContainer = document.getElementById('properties-container');
const propertiesList = document.getElementById('properties-list');
const closePropertiesBtn = document.getElementById('close-properties-btn');

// ============================================================================
// ESTADO
// ============================================================================

let sessionId = localStorage.getItem(SESSION_KEY) || null;
let isProcessing = false;

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    updateSessionStatus();
    setupEventListeners();
    
    // Si hay sesión previa, mostrar mensaje de bienvenida
    if (sessionId) {
        addMessage('bot', '¡Hola de nuevo! ¿En qué puedo ayudarte?');
    }
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Enviar mensaje con botón
    sendBtn.addEventListener('click', handleSendMessage);
    
    // Enviar mensaje con Enter
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) {
            handleSendMessage();
        }
    });
    
    // Reset session
    resetBtn.addEventListener('click', handleResetSession);
    
    // Cerrar modal de propiedades
    closePropertiesBtn.addEventListener('click', closeProperties);
    
    // Cerrar modal al hacer click fuera
    propertiesContainer.addEventListener('click', (e) => {
        if (e.target === propertiesContainer) {
            closeProperties();
        }
    });
}

// ============================================================================
// MANEJO DE MENSAJES
// ============================================================================

async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) return;
    
    // Limpiar input
    messageInput.value = '';
    
    // Agregar mensaje del usuario
    addMessage('user', message);
    
    // Mostrar loading
    setProcessing(true);
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Actualizar session_id
        if (!sessionId) {
            sessionId = data.session_id;
            localStorage.setItem(SESSION_KEY, sessionId);
            updateSessionStatus();
        }
        
        // Agregar respuesta del bot
        addMessage('bot', data.response);
        
        // Si hay propiedades encontradas, mostrarlas automáticamente
        if (data.properties_found && data.properties_found > 0) {
            setTimeout(() => {
                loadProperties();
            }, 500);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', '❌ Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.');
    } finally {
        setProcessing(false);
    }
}

// ============================================================================
// UI - MENSAJES
// ============================================================================

function addMessage(type, content) {
    // Remover mensaje de bienvenida si existe
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'bot' ? '🤖' : '👤';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    contentDiv.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll al final
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ============================================================================
// PROPIEDADES
// ============================================================================

async function loadProperties() {
    if (!sessionId) return;
    
    setProcessing(true);
    
    try {
        const response = await fetch(`${API_URL}/properties/${sessionId}`);
        
        if (!response.ok) {
            if (response.status === 400) {
                // No hay búsqueda ejecutada aún
                return;
            }
            throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        displayProperties(data);
        
    } catch (error) {
        console.error('Error loading properties:', error);
        addMessage('bot', '❌ Hubo un error al cargar las propiedades.');
    } finally {
        setProcessing(false);
    }
}

function displayProperties(data) {
    propertiesList.innerHTML = '';
    
    if (!data.properties || data.properties.length === 0) {
        propertiesList.innerHTML = `
            <div class="no-properties">
                <p>No se encontraron propiedades con los criterios especificados.</p>
            </div>
        `;
    } else {
        data.properties.forEach(property => {
            const card = createPropertyCard(property);
            propertiesList.appendChild(card);
        });
    }
    
    propertiesContainer.style.display = 'flex';
}

function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'property-card';
    
    // Formatear precio
    const price = property.valor_comercial 
        ? `S/ ${property.valor_comercial.toLocaleString('es-PE')}` 
        : 'Precio no disponible';
    
    // Features activos
    const features = [];
    if (property.permite_mascotas) features.push('🐾 Pet-friendly');
    if (property.balcon) features.push('🌿 Balcón');
    if (property.terraza) features.push('🏖️ Terraza');
    if (property.amoblado) features.push('🛋️ Amoblado');
    
    card.innerHTML = `
        <div class="property-header">
            <div>
                <div class="property-title">${property.tipo} ${property.numero}</div>
                <small style="color: var(--text-light);">Piso ${property.piso || 'N/A'}</small>
            </div>
            <div class="property-price">${price}</div>
        </div>
        
        <div class="property-details">
            <div class="detail-item">
                📐 <strong>${property.area || 'N/A'} m²</strong>
            </div>
            <div class="detail-item">
                🛏️ <strong>${property.dormitorios || 0} dormitorios</strong>
            </div>
            <div class="detail-item">
                🚿 <strong>${property.banios || 0} baños</strong>
            </div>
            <div class="detail-item">
                📊 <strong>${property.estado}</strong>
            </div>
        </div>
        
        ${features.length > 0 ? `
            <div class="property-features">
                ${features.map(f => `<span class="feature-badge">${f}</span>`).join('')}
            </div>
        ` : ''}
        
        <div class="property-location">
            📍 <strong>${property.edificio_nombre || 'Edificio'}</strong><br>
            ${property.edificio_direccion || ''}, ${property.edificio_distrito || ''}
        </div>
    `;
    
    return card;
}

function closeProperties() {
    propertiesContainer.style.display = 'none';
}

// ============================================================================
// SESIONES
// ============================================================================

async function handleResetSession() {
    if (!confirm('¿Estás seguro de que quieres iniciar una nueva búsqueda? Se perderá la conversación actual.')) {
        return;
    }
    
    setProcessing(true);
    
    try {
        if (sessionId) {
            await fetch(`${API_URL}/session/${sessionId}/reset`, {
                method: 'POST'
            });
        }
        
        // Limpiar localStorage
        localStorage.removeItem(SESSION_KEY);
        sessionId = null;
        
        // Limpiar UI
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="bot-icon">🤖</div>
                <p>¡Hola! Soy tu asistente inmobiliario. Te ayudaré a encontrar el departamento perfecto.</p>
                <p>Solo dime qué buscas y empecemos.</p>
            </div>
        `;
        
        closeProperties();
        updateSessionStatus();
        
        addMessage('bot', '¡Nueva sesión iniciada! ¿En qué puedo ayudarte?');
        
    } catch (error) {
        console.error('Error resetting session:', error);
        alert('Hubo un error al reiniciar la sesión. Recarga la página.');
    } finally {
        setProcessing(false);
    }
}

function updateSessionStatus() {
    if (sessionId) {
        sessionStatus.textContent = `Sesión: ${sessionId.substring(0, 8)}...`;
    } else {
        sessionStatus.textContent = 'Sesión: Nueva';
    }
}

// ============================================================================
// UTILIDADES
// ============================================================================

function setProcessing(processing) {
    isProcessing = processing;
    sendBtn.disabled = processing;
    messageInput.disabled = processing;
    loading.style.display = processing ? 'block' : 'none';
    
    if (processing) {
        sendBtn.innerHTML = '<span>Enviando...</span>';
    } else {
        sendBtn.innerHTML = '<span>Enviar</span>';
        messageInput.focus();
    }
}

// ============================================================================
// MANEJO DE ERRORES GLOBAL
// ============================================================================

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    addMessage('bot', '❌ Ocurrió un error inesperado. Por favor, recarga la página.');
    setProcessing(false);
});