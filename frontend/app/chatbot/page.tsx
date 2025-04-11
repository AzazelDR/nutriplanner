import React from 'react';
import { ChatBot } from '@/components/ChatBot/ChatBot';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Asistente Virtual - NutriPlanner AI',
  description: 'Interactúa con nuestro asistente virtual para resolver tus dudas sobre nutrición.',
};

const ChatBotPage = () => {
  return <ChatBot />;
};

export default ChatBotPage;
