import React from 'react';
import styles from './AccommodationsSupport.module.css';

export const AccommodationsSupport = () => {
  return (
    <section className={styles.container}>
      <h1 className={styles.title}>Soporte Nutricional</h1>
      <p className={styles.description}>
        Contáctanos para obtener soporte personalizado en tu plan nutricional. Nuestro equipo está listo para ayudarte a alcanzar tus objetivos de salud.
      </p>
      <a href="mailto:soporte@nutriclinica.com" className={styles.button}>
        Enviar Correo
      </a>
    </section>
  );
};