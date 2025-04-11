'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React from 'react';
import styles from './Navbar.module.css';

export const Navbar = () => {
  const pathname = usePathname();

  return (
    <header className={styles.navbar}>
      <div className={styles.logo}>
        <Link href="/">NutriPlanner AI</Link>
      </div>
      <nav className={styles.navLinks}>
        <Link href="/" className={pathname === '/' ? styles.active : ''}>
          Inicio
        </Link>
        <Link href="/chatbot" className={pathname === '/chatbot' ? styles.active : ''}>
          Asistente
        </Link>
        <Link
          href="/accommodations-support"
          className={pathname === '/accommodations-support' ? styles.active : ''}
        >
          Soporte
        </Link>
      </nav>
    </header>
  );
};