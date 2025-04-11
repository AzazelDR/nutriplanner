# NutriPlaner - Frontend

NutriPlaner es un sistema en línea que utiliza un chatbot con inteligencia artificial para ofrecer planes nutricionales personalizados. Este repositorio contiene la parte del frontend de la aplicación, desarrollada con [Next.js](https://nextjs.org) y arrancada con [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

> **Nota:** Este repositorio forma parte de un monorepo. La lógica del backend se encuentra en la carpeta `backend`, mientras que este es el código fuente del frontend.

## Getting Started

### Ejecutar el Servidor de Desarrollo

Para iniciar el servidor de desarrollo y ver los cambios en tiempo real, ejecuta:

```bash
npm run dev
# o
yarn dev
# o
pnpm dev
# o (si usas Bun)
bun dev
```
Abre http://localhost:3000 en tu navegador para ver la aplicación en acción. La página se actualizará automáticamente a medida que edites el código.

### Edición de Código
Puedes comenzar a editar la aplicación modificando el archivo app/page.tsx (o el correspondiente a la versión de Next.js que estés utilizando). Los cambios se reflejarán en tiempo real gracias al hot reload.

### Optimización de Fuentes
Este proyecto utiliza next/font para optimizar y cargar automáticamente la fuente Geist, proporcionando una experiencia visual optimizada y de alto rendimiento.

## Learn More
### Para aprender más sobre Next.js y profundizar en las funcionalidades de este framework, consulta los siguientes recursos:

- Next.js Documentation – Información completa sobre funciones y API.

- Learn Next.js – Un tutorial interactivo para aprender Next.js de forma práctica.

- Next.js GitHub Repository – Contribuye, da feedback y descubre ejemplos.

### Deploy on Vercel
La manera más sencilla de desplegar esta aplicación es utilizando la plataforma Vercel. Al configurar el despliegue, asegúrate de indicar que la carpeta raíz es la de frontend.

Consulta la documentación de despliegue de Next.js para más detalles sobre el proceso.

## Ejemplo de Configuración y Despliegue
### Sigue estos pasos para configurar y desplegar la aplicación localmente:

1. Instala las dependencias:

```bash
npm install
```
2. Configura las variables de entorno. Por ejemplo, crea un archivo .env con el siguiente contenido:

```bash
NEXT_PUBLIC_API_URL=http://localhost:3000
GOOGLE_MAPS_API_KEY=AIzaSyCxYIA4NtUc-A7BYAHePXG4YCLWGVRIM4M
```
3. Si aún no lo tienes, instala Vercel CLI globalmente:

```bash
npm install -g vercel
```
4. Construye la aplicación:

```bash
npm run build
```
5. Inicia la aplicación en modo producción:

```bash
npm start
```
