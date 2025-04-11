import React from 'react';
import { Accommodation } from '@/components/Accommodation/Accommodation';

const AccommodationPage = async ({
  params,
}: {
  params: { id: string };
}) => {
  const accommodationId = params.id;

  return <Accommodation accommodationId={accommodationId} />;
};

export default AccommodationPage;