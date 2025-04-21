'use client';

import React, { useEffect, useState } from 'react';
import AnimatedList from '../desing/AnimatedList/AnimatedList';
import styles from './AccommodationsSupport.module.css';

export interface Doctor {
  Name: string;
  Especialidad: string;
  Telefono: string;
  Descripcion: string;
  Link: string;
}

export const AccommodationsSupport: React.FC = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [topOpacity, setTopOpacity] = useState(0);
  const [bottomOpacity, setBottomOpacity] = useState(1);

  useEffect(() => {
    const ws = new WebSocket('wss://nutriplanner.up.railway.app/support');
    ws.onopen = () => console.log('WS soporte abierto');
    ws.onerror = () => setError('⚠️ No se pudo conectar al servicio de soporte.');
    ws.onmessage = (event) => {
      try {
        const { data } = JSON.parse(event.data);
        setDoctors(data);
      } catch {
        setError('⚠️ Respuesta no válida del servidor.');
      } finally {
        ws.close();
      }
    };
    return () => { if (ws.readyState === WebSocket.OPEN) ws.close(); };
  }, []);

  if (error) {
    return (
      <section className={styles.container}>
        <p>{error}</p>
      </section>
    );
  }

  return (
    <section className={styles.container}>
    <h1>Soporte Nutricional</h1>
    <AnimatedList
      items={doctors}
      renderItem={(doc) => (
        <ul>
        <li className={styles.listItem}>
          <div key={doc.Name} className={styles.card}>
            <h2 className={styles.cardTitle}>{doc.Name}</h2>
            <h3 className={styles.cardSubtitle}>{doc.Especialidad}</h3>
            <p className={styles.cardText}>{doc.Descripcion}</p>
            <p className={styles.cardText}>📞 {doc.Telefono}</p>          
          </div>
        </li>
        </ul>
      )}
      displayScrollbar
    />
      {topOpacity > 0 && <div className={styles.topGradient} style={{ opacity: topOpacity }} />}
      {bottomOpacity > 0 && <div className={styles.bottomGradient} style={{ opacity: bottomOpacity }} />}
    </section>
  );
};
