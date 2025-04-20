'use client';

import React, { useEffect, useRef, useState } from 'react';
import parse, { Element } from 'html-react-parser';
import DOMPurify from 'dompurify';
import styles from './ChatBot.module.css';

type Message = {
  text: string;
  isUser: boolean;
};

export const ChatBot: React.FC = () => {
  // Mensaje inicial fijo
// start with an empty chat; server will send the greeting
const [messages, setMessages] = useState<Message[]>([]);

  const [input, setInput] = useState<string>('');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = new WebSocket(
      'wss://nutriplanner.up.railway.app/chatbot'
    ); 

    ws.onerror = () => {
      setMessages((prev) => [
        ...prev,
        { text: '⚠️ Error de conexión con el servidor', isUser: false },
      ]);
    };

    ws.onopen = () => {
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.status === 'error') {
          setMessages((prev) => [
            ...prev,
            {
              text: `⚠️ Error: ${
                response.error ?? 'Error desconocido'
              }`,
              isUser: false,
            },
          ]);
        } else {
          setIsTyping(false);
          setMessages((prev) => [
            ...prev,
            { text: response.message, isUser: false },
          ]);
        }
      } catch {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          { text: '⚠️ Respuesta no válida', isUser: false },
        ]);
      }
    };

    ws.onclose = (event) => {
      if (event.code !== 1000) {
        setMessages((prev) => [
          ...prev,
          {
            text: '⚠️ Conexión perdida, recarga la página para reconectar',
            isUser: false,
          },
        ]);
      }
    };

    const cleanup = () => {
      if (ws.readyState === WebSocket.OPEN) ws.close(1000, 'Unload');
    };
    window.addEventListener('beforeunload', cleanup);
    return () => {
      window.removeEventListener('beforeunload', cleanup);
      cleanup();
    };
  }, []);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = () => {
    if (socket && input.trim()) {
      setIsTyping(true);
      socket.send(JSON.stringify({ message: input.trim() }));
      setMessages((prev) => [
        ...prev,
        { text: input.trim(), isUser: true },
      ]);
      setInput('');
    }
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (text: string, isUser: boolean) => {
    if (isUser) {
      return <div className={styles.userMessageContent}>{text}</div>;
    }
  
    // only sanitize if DOMPurify.sanitize is available (i.e. on the client)
    const sanitized = typeof DOMPurify.sanitize === 'function'
      ? DOMPurify.sanitize(text, {
          ALLOWED_TAGS: ['p','br','a','strong','em','ul','ol','li'],
          ALLOWED_ATTR: ['href','class']
        })
      : text;
  
    return (
      <div className={styles.messageContent}>
        {parse(sanitized, {
          replace: (node) => {
            if (
              node instanceof Element &&
              node.name === 'a' &&
              node.attribs.href
            ) {
              return (
                <a
                  href={node.attribs.href}
                  className={styles.recommendationLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {node.children.map((child, i) =>
                    'data' in child ? child.data : null
                  )}
                </a>
              );
            }
            return undefined;
          },
        })}
      </div>
    );
  };
  

  return (
    <div className={styles.chatbotContainer}>
      <h2 className={styles.title}>Asistente Virtual</h2>

      <div className={styles.chatMessages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.message} ${
              msg.isUser
                ? styles.userMessage
                : styles.botMessage
            }`}
          >
            {renderMessage(msg.text, msg.isUser)}
          </div>
        ))}
        {isTyping && (
          <p className={styles.typing}>El bot está escribiendo...</p>
        )}
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
