import React from 'react';
import styles from './Home.module.css';

export const Home = () => {
  return (
    <main className={styles.main}>
      <section className={styles.hero}>
        <h1 className={styles.title}>Bienvenido a NutriPlanner AI</h1>
        <p className={styles.subtitle}>
          Optimiza tu alimentación con inteligencia artificial.
        </p>
      </section>

      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>¿Qué Ofrecemos?</h2>
        <ul className={styles.list}>
          <li>Planes de alimentación personalizados.</li>
          <li>Asistente virtual para consultas en tiempo real.</li>
          <li>Recetas saludables basadas en tus ingredientes disponibles.</li>
          <li>Optimización de la planificación alimenticia.</li>
        </ul>
      </section>
      
      <h2 className={styles.sectionTitle}>Explora Más</h2>
      <section className={styles.cta}>
      
        <div className={styles.buttons}>
          <a href="/chatbot" className={styles.button}>
            Asistente Virtual
          </a>
          <a href="/accommodations-support" className={styles.button}>
            Soporte Nutricional
          </a>
        </div>
      </section>
    </main>
  );
};