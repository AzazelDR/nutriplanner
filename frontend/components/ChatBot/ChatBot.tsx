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
  
    // Función de limpieza que siempre devuelve void
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const send = () => {
    if (!socket || !input.trim()) return;
    setIsTyping(true);
    socket.send(JSON.stringify({ message: input.trim() }));
    setMessages(m => [...m, { text: input, isUser: true }]);
    setInput('');
  };

  const renderMessage = (msg: string, me: boolean) => {
    if (me) return <div className={styles.userMessageContent}>{msg}</div>;
    const safe = DOMPurify.sanitize(msg, {
      ALLOWED_TAGS: ['p','br','a','strong','em','ul','ol','li'],
      ALLOWED_ATTR: ['href','class','target','rel']
    });
    return <div className={styles.messageContent} dangerouslySetInnerHTML={{ __html: safe }} />;
  };

  return (
    <div className={styles.chatbotContainer}>
      <h2 className={styles.title}>Asistente Virtual</h2>
      <div className={styles.chatMessages}>
        {messages.map((m,i) =>
          <div key={i} className={`${styles.message} ${m.isUser?styles.userMessage:styles.botMessage}`}>
            {renderMessage(m.text, m.isUser)}
          </div>
        )}
        {isTyping && <p className={styles.typing}>El bot está escribiendo…</p>}
        <div ref={endRef}/>
      </div>
      <div className={styles.inputContainer}>
        <input
          className={styles.inputField}
          value={input}
          onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==='Enter'&&!e.shiftKey&&(e.preventDefault(),send())}
          placeholder="Escribe tu mensaje…"
        />
        <button disabled={!input.trim()||!socket} className={styles.sendButton} onClick={send}>
          Enviar
        </button>
      </div>
    </div>
  );
};
