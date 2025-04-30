'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import styles from './Navbar.module.css';

const navItems = [
  { href: '/', label: 'Inicio' },
  { href: '/chatbot', label: 'Agente Virtual' },
  { href: '/accommodations-support', label: 'Soporte' },
];

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <motion.header
      className={styles.navbar}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 120 }}
    >
      <div className={styles.logo}>
        <Link href="/">AR Nutrición IA</Link>
      </div>

      <button
        className={styles.burger}
        onClick={() => setOpen(o => !o)}
        aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
      >
        {open ? <X /> : <Menu />}
      </button>

      <nav className={`${styles.navLinks} ${open ? styles.show : ''}`}>  
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`${styles.navLink} ${pathname === item.href ? styles.active : ''}`}
            onClick={() => setOpen(false)}
          >
            <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
              {item.label}
            </motion.span>
          </Link>
        ))}
      </nav>
    </motion.header>
  );
};