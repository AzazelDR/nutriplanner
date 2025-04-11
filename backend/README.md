# NutriPlaner - Backend

NutriPlaner es un sistema en línea que utiliza un chatbot con inteligencia artificial para ofrecer planes nutricionales personalizados. Este repositorio contiene la parte del backend de la aplicación, desarrollado con [FastAPI](https://fastapi.tiangolo.com) y otras herramientas de Python.

> **Nota:** Este repositorio forma parte de un monorepo. La parte del frontend se encuentra en la carpeta `frontend`.

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Ejecución en Desarrollo](#ejecución-en-desarrollo)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Despliegue](#despliegue)
- [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- [Python](https://www.python.org) (se recomienda la versión 3.8 o superior)
- [pip](https://pip.pypa.io)
- [virtualenv](https://virtualenv.pypa.io) (opcional, pero recomendado)
- [Git](https://git-scm.com)

## Instalación

1. **Clona el repositorio:**

    ```bash
    git clone https://github.com/tu-usuario/NutriPlaner.git
    ```

2. **Navega a la carpeta del backend:**

    ```bash
    cd NutriPlaner/backend
    ```

3. **Crea y activa un entorno virtual:**

    En Windows:
    ```bash
    python -m pip install --upgrade pip
    python -m pip install virtualenv
    virtualenv venv
    venv\Scripts\activate
    ```

    En macOS y Linux:
    ```bash
    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    virtualenv venv
    source venv/bin/activate
    ```

4. **Instala las dependencias:**

    ```bash
    pip install --no-cache-dir -r requirements.txt
    ```

> **Consejo:** Si necesitas agregar nuevos paquetes, actualiza el archivo `requirements.txt` para mantener la sincronización entre entornos.

## Ejecución en Desarrollo

Para iniciar el servidor en modo desarrollo y probar la API, utiliza [uvicorn](https://www.uvicorn.org) con el flag `--reload` para que se reinicie el servidor al detectar cambios en el código:

```bash
uvicorn main:app --reload
```
También puedes especificar host y puerto si es necesario:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Una vez iniciado, la API estará disponible en http://127.0.0.1:8000.

## Despliegue
Para un despliegue en producción, puedes utilizar servicios como Railway u otros proveedores de infraestructura para Python. Recuerda:

Configurar las variables de entorno necesarias.

Utilizar un servidor de aplicaciones (por ejemplo, Gunicorn) junto con uvicorn si es necesario.

Asegurarte de que el entorno de producción está configurado correctamente con las medidas de seguridad pertinentes.

## Configuración de Variables de Entorno
NutriPlaner requiere algunas variables de entorno para funcionar correctamente. Puedes definirlas en un archivo .env en la carpeta backend. Por ejemplo:

```bash
# Clave para el servicio de inteligencia artificial (reemplaza con tu clave real)
GEMINI_KEY=XXXXXXXXXXXXXXXXXXXXXXXXX

# URL de la base de datos (puede ser SQLite, Postgres, etc.)
DATABASE_URL=sqlite:///./test.db
```
Importante: Asegúrate de agregar el archivo .env al .gitignore para evitar exponer información sensible.