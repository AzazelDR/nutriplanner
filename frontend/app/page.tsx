import React from 'react';
import { Home } from '@/components/Home/Home';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Inicio',
  description: 'AR Nutrición IA es un sistema de recomendación de planes de alimentación saludable con un agente virtual basado en inteligencia artificial.',
};

const HomePage = () => {
  return <Home />;
};

export default HomePage;