import React from 'react';
import { AccommodationsSupport } from '@/components/AccommodationsSupport/AccommodationsSupport';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Especialista en Nutrición',
  description: 'Contacta con un especialisa si requires atencion en un area dedicada.',
};
const AccommodationsSupportPage = () => {
  return <AccommodationsSupport />;
};

export default AccommodationsSupportPage;
