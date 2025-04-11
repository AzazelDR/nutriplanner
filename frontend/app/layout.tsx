import './globals.css';
import { Navbar } from '@/components/Navbar/Navbar';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        <Navbar />
        <main>        
          {children}
        </main>
      </body>
    </html>
  );
}