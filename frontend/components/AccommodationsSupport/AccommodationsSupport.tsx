'use client';

import React, { useEffect, useState } from 'react';
import styles from './AccommodationsSupport.module.css';

type Doctor = {
  Name: string;
  Especialidad: string;
  Telefono: string;
  Descripcion: string;
  Link: string;
};

export const AccommodationsSupport: React.FC = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/support')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(json => setDoctors(json.data))
      .catch(() => setError('No se pudieron cargar los doctores.'));
  }, []);

  if (error) {
    return <section className={styles.container}><p>{error}</p></section>;
  }

  return (
    <section className={styles.container}>
      <h1 className={styles.title}>Soporte Nutricional</h1>
      <p className={styles.description}>
        Nuestro equipo de especialistas está listo para apoyarte.
      </p>

      <div className={styles.list}>
        {doctors.map(doc => (
          <div className={styles.card} key={doc.Name}>
            <h2 className={styles.cardTitle}>{doc.Name}</h2>
            <h3 className={styles.cardSubtitle}>{doc.Especialidad}</h3>
            <p className={styles.cardText}>📞 {doc.Telefono}</p>
            <p className={styles.cardText}>{doc.Descripcion}</p>
            <a
              href={doc.Link}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.cardButton}
            >
              Ver Perfil
            </a>
          </div>
        ))}
      </div>
    </section>
  );
};
