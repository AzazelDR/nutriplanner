'use client';

import React, { useEffect, useState } from 'react';
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

  useEffect(() => {
    const ws = new WebSocket('wss://nutriplanner.up.railway.app/support');

    ws.onopen = () => {
      console.log('WS soporte abierto');
    };
    ws.onerror = () => {
      setError('⚠️ No se pudo conectar al servidor de soporte');
    };
    ws.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        setDoctors(payload.data);
      } catch {
        setError('⚠️ Formato de datos inválido');
      }
    };
    // No esperamos más mensajes: cerramos al recibir la lista
    ws.onclose = () => {
      console.log('WS soporte cerrado');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, []);

  if (error) {
    return (
      <section className={styles.container}>
        <p className={styles.description}>{error}</p>
      </section>
    );
  }

  return (
    <section className={styles.container}>
      <h1 className={styles.title}>Soporte Nutricional</h1>
      <p className={styles.description}>
        Contáctanos con uno de nuestros especialistas:
      </p>

      <div className={styles.list}>
        {doctors.map((doc) => (
          <div key={doc.Name} className={styles.card}>
            <h2 className={styles.cardTitle}>{doc.Name}</h2>
            <h3 className={styles.cardSubtitle}>{doc.Especialidad}</h3>
            <p className={styles.cardText}>{doc.Descripcion}</p>
            <p className={styles.cardText}>
              📞 <a href={`tel:${doc.Telefono}`}>{doc.Telefono}</a>
            </p>
            <a
              href={doc.Link}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.button}
            >
              Ver perfil
            </a>
          </div>
        ))}
      </div>
    </section>
  );
};
