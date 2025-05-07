import React from 'react';
import { Accommodation } from '@/components/Accommodation/Accommodation';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Plan Nutricional',
  description: 'Revisa tu plan presentado por la IA.',
};
const AccommodationPage = async ({
  params,
}: {
  params: { id: string };
}) => {
  const accommodationId = params.id;

  return <Accommodation accommodationId={accommodationId} />;
};

export default AccommodationPage;