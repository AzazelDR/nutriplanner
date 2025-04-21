'use client';

import React from 'react';
import Link from 'next/link';
import SpotlightCard from '@/components/desing/SpotlightCard/SpotlightCard';
import styles from './Home.module.css';

const featureList = [
  'Planes de alimentación personalizados.',
  'Asistente virtual para consultas en tiempo real.',
  'Recetas saludables basadas en tus ingredientes disponibles.',
  'Optimización de la planificación alimenticia.',
];

export const Home: React.FC = () => {
  const ctaItems = [
    { href: '/chatbot', label: 'Asistente Virtual' },
    { href: '/accommodations-support', label: 'Soporte Nutricional' },
  ];

  return (
    <main className={styles.main}>
      <section className={styles.hero}>
        <h1 className={styles.title}>Bienvenido a NutriPlanner AI</h1>
        <p className={styles.subtitle}>Optimiza tu alimentación con inteligencia artificial.</p>
      </section>

      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>¿Qué Ofrecemos?</h2>
        <div className={styles.cardsGrid}>
          {featureList.map(feature => (
            <SpotlightCard
              key={feature}
              className={styles.card}
              spotlightColor="rgba(0, 229, 255, 0.2)"
            >
              <div className={styles.cardContent}>
                <p className={styles.cardText}>{feature}</p>
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      <section className={styles.ctaSection}>
        <h2 className={styles.sectionTitle}>Explora Más</h2>
        <div className={styles.cardsGrid}>
          {ctaItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={styles.linkWrapper}
            >
              <SpotlightCard
                className={styles.card}
                spotlightColor="rgba(255, 184, 0, 0.2)"
              >
                <div className={styles.cardContent}>
                  <span className={styles.ctaLink}>{item.label}</span>
                </div>
              </SpotlightCard>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
};
