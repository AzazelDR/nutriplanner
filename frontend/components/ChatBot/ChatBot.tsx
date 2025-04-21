'use client';

import React, { useEffect, useRef, useState } from 'react';
import styles from './ChatBot.module.css';
import DOMPurify from 'dompurify';

type Message = {
  text: string;
  isUser: boolean;
};

export const ChatBot = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Limpiar mensajes al iniciar (esto se ejecuta al montar el componente)
    setMessages([]);
    
    const ws = new WebSocket('wss://nutriplanner.up.railway.app/chatbot');

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setMessages(prev => [...prev, { 
        text: "⚠️ Error de conexión con el servidor", 
        isUser: false 
      }]);
    };

    ws.onopen = () => {
      console.log('WebSocket connection opened');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      console.log('Mensaje recibido:', event.data);
      try {
        const response = JSON.parse(event.data);
        
        if (response.status === "error") {
          console.error('Error del backend:', response.error);
          setMessages(prev => [...prev, { 
            text: `⚠️ Error: ${response.error || "Error desconocido"}`, 
            isUser: false 
          }]);
        } else {
          setIsTyping(false);
          setMessages(prev => [...prev, { 
            text: response.message, 
            isUser: false 
          }]);
        }
      } catch (error) {
        console.error('Error al parsear el mensaje:', error);
        setIsTyping(false);
        setMessages(prev => [...prev, { 
          text: "⚠️ Respuesta del servidor no válida", 
          isUser: false 
        }]);
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket connection closed', event.code, event.reason);
      if (event.code !== 1000) {
        setMessages(prev => [...prev, { 
          text: "⚠️ Conexión perdida, recarga la página para reconectar", 
          isUser: false 
        }]);
      }
    };

    // Limpiar al desmontar el componente o recargar la página
    const handleBeforeUnload = () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Page reload");
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Component unmounted");
      }
    };
  }, []); // <-- Array de dependencias vacío para que solo se ejecute al montar/desmontar

  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const sendMessage = () => {
    if (socket && input.trim()) {
      const messageObject = { message: input.trim() };
      setIsTyping(true);
      socket.send(JSON.stringify(messageObject));
      setMessages(prev => [...prev, { text: input, isUser: true }]);
      setInput('');
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (message: string, isUser: boolean) => {
    if (isUser) {
      return <div className={styles.userMessageContent}>{message}</div>;
    }
  
    // Sanitizar el HTML y permitir etiquetas básicas
    const sanitized = DOMPurify.sanitize(message, {
      ALLOWED_TAGS: ['p', 'br', 'a', 'strong', 'em', 'ul', 'ol', 'li'],
      ALLOWED_ATTR: ['href', 'class']
    });
  
    return (
      <div 
        className={styles.messageContent}
        dangerouslySetInnerHTML={{ __html: sanitized }}
      />
    );
  };

  return (
    <div className={styles.chatbotContainer}>
      <h2 className={styles.title}>Asistente Virtual</h2>

      <div className={styles.chatMessages}>
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`${styles.message} ${message.isUser ? styles.userMessage : styles.botMessage}`}
          >
            {renderMessage(message.text, message.isUser)}
          </div>
        ))}
        {isTyping && <p className={styles.typing}>El bot está escribiendo...</p>}
        <div ref={messageEndRef} />
      </div>

      <div className={styles.inputContainer}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje..."
          className={styles.inputField}
        />
        <button 
          onClick={sendMessage}
          className={styles.sendButton}
          disabled={!input.trim() || !socket}
        >
          Enviar
        </button>
      </div>
    </div>
  );
};