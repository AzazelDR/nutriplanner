// app/layout.tsx (RootLayout)

'use client';                       // asegúrate de que sea client‑side
import './globals.css';
import { Navbar } from '@/components/Navbar/Navbar';
import Particles from '@/components/desing/Particles/Particles';
import ClickSpark from '@/components/desing/ClickSpark/ClickSpark';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        {/* Fondo de partículas sigue igual */}
        <Particles 
          particleColors={['#0052CC', '#FFD600', '#FFFFFF']}
          particleCount={200}
          particleSpread={10}
          speed={0.3}
          particleBaseSize={200}
        />

        {/* Barra de navegación */}
        <Navbar />

        {/* ---------- Chispas globales ---------- */}
        <ClickSpark
          sparkColor="#FFDF33"   // usa colores de tu paleta
          sparkSize={8}
          sparkRadius={20}
          sparkCount={10}
          duration={500}
        >
          <main>
            {children}           {/* todo tu sitio queda envuelto */}
          </main>
        </ClickSpark>
      </body>
    </html>
  );
}
