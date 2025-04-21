'use client';
import React, { useEffect, useRef, useState } from 'react';
import styles from './ChatBot.module.css';
import DOMPurify from 'dompurify';

type Message = { text: string; isUser: boolean };

export const ChatBot = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  /* -------------  WebSocket ------------- */
  useEffect(() => {
    const ws = new WebSocket('wss://nutriplanner.up.railway.app/chatbot');
    ws.onopen = () => setSocket(ws);
    ws.onerror = () =>
      setMessages(m => [
        ...m,
        { text: '⚠️ Error de conexión', isUser: false },
      ]);
    ws.onmessage = e => {
      const res = JSON.parse(e.data);
      if (res.status === 'success') {
        setIsTyping(false);
        setMessages(m => [...m, { text: res.message, isUser: false }]);
      }
    };
      return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  /* -------------  Auto‑scroll ------------- */
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  /* -------------  Handlers ------------- */
  const send = () => {
    if (!socket || !input.trim()) return;
    socket.send(JSON.stringify({ message: input.trim() }));
    setMessages(m => [...m, { text: input.trim(), isUser: true }]);
    setInput('');
    setIsTyping(true);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  /* -------------  Render helpers ------------- */
  const renderMessage = (msg: string, isUser: boolean) => {
    if (isUser) return <div className={styles.userText}>{msg}</div>;

    const safe = DOMPurify.sanitize(msg, {
      ALLOWED_TAGS: [
        'p', 'br', 'a', 'strong', 'em', 'ul', 'ol', 'li', 'span'
      ],
      ALLOWED_ATTR: ['href', 'class', 'target', 'rel']
    });
    return (
      <div
        className={styles.botText}
        dangerouslySetInnerHTML={{ __html: safe }}
      />
    );
  };

  /* -------------  JSX ------------- */
  return (
    <div className={styles.chatbot}>
      <h2 className={styles.title}>Asistente&nbsp;Virtual</h2>

      <div className={styles.messages}>
        {messages.map((m, i) => (
          <div
            key={i}
            className={`${styles.message} ${
              m.isUser ? styles.userMsg : styles.botMsg
            }`}
          >
            {renderMessage(m.text, m.isUser)}
          </div>
        ))}

        {isTyping && (
          <p className={`${styles.message} ${styles.botMsg}`}>
            El bot está escribiendo…
          </p>
        )}
        <div ref={endRef} />
      </div>

      <div className={styles.inputBox}>
        <input
          className={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Escribe tu mensaje…"
        />
        <button
          className={styles.send}
          disabled={!input.trim() || !socket}
          onClick={send}
        >
          Enviar
        </button>
      </div>
    </div>
  );
};
