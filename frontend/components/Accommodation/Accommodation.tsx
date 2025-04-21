'use client';

import React, { FC, useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation'; // Importa useRouter
import { IAccommodationData } from '@/interfaces/IAccommodationData';
import styles from './Accommodation.module.css';

export const Accommodation: FC<{ accommodationId: string }> = ({
  accommodationId,
}) => {
  const [planData, setPlanData] = useState<IAccommodationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter(); // Inicializa useRouter

  useEffect(() => {
    const getPlanData = async () => {
      try {
        const response = await axios.get(
          `https://nutriplanner.up.railway.app/accommodation/${accommodationId}`
        );

        console.log('Respuesta de la API:', response.data);

        if (response.data && response.data.data) {
          setPlanData(response.data.data);
        } else {
          throw new Error('No se encontraron datos del plan.');
        }
      } catch (error: unknown) {
        console.error('Error fetching plan data:', error);
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError('Error desconocido al obtener los datos del plan.');
        }
      }
    };

    getPlanData();
  }, [accommodationId]);

  if (error) {
    return <p className={styles.error}>{error}</p>;
  }

  if (!planData) {
    return <p className={styles.loading}>Cargando detalles del plan...</p>;
  }

  return (
    <section className={styles.container}>
      <h1 className={styles.title}>{planData.nombre}</h1>
      <p className={styles.description}>{planData.descripcion}</p>
      <p>
        <span className={styles.strongText}>Duración:</span> {planData.duracion}
      </p>
      <h2 className={styles.subTitle}>Macronutrientes</h2>
      <ul className={styles.list}>
        <li className={styles.listItem}>
          <span className={styles.strongText}>Carbohidratos:</span> {planData.macros.carbohidratos}
        </li>
        <li className={styles.listItem}>
          <span className={styles.strongText}>Proteínas:</span> {planData.macros.proteinas}
        </li>
        <li className={styles.listItem}>
          <span className={styles.strongText}>Grasas:</span> {planData.macros.grasas}
        </li>
      </ul>
      <h2 className={styles.subTitle}>Alimentos Clave</h2>
      <ul className={styles.list}>
        {planData.alimentos_clave.map((alimento, index) => (
          <li key={index} className={styles.listItem}>
            {alimento}
          </li>
        ))}
      </ul>
      <h2 className={styles.subTitle}>Evitar</h2>
      <ul className={styles.list}>
        {planData.evitar.map((item, index) => (
          <li key={index} className={styles.listItem}>
            {item}
          </li>
        ))}
      </ul>
      {/* Botón para regresar al chat */}
      <button className={styles.backButton} onClick={() => router.push('/chatbot')}>
        Regresar al Chat
      </button>
    </section>
  );
};
