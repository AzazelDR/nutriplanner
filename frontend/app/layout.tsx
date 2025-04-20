import './globals.css';
import { Navbar } from '@/components/Navbar/Navbar';
import Particles from '@/components/Particles/Particles';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
      <Particles 
          particleColors={['#0052CC', '#FFD600', '#FFFFFF']}
          particleCount={200}
          particleSpread={10}
          speed={0.3}
          particleBaseSize={200}
        />
        <Navbar />
        <main>        
          {children}
        </main>
      </body>
    </html>
  );
}