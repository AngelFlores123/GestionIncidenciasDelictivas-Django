# **Sistema geográfico para la gestión de reportes de incidencias delictivas**

[![Estado del Proyecto](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow.svg)](URL_DEL_REPOSITORIO)

Descripción de la aplicación.
> Este proyecto es una aplicación web CRUD (Crear, Leer, Actualizar, Borrar) desarrollada en **Django** que permite gestionar la ubicación y los datos de distintos reportes sobre incidencias delictivas ocurridas en la CDMX, utilizando como gestor de bases de datos **POSTGRESQL** con la extensión **PostGIS** para el manejo de datos geográficos. Fue desarrollado como parte de mi servicio social. Además, el sistema permite agrupar las ubicaciones de las incidencias y mostrar un mapa de calor que permite ver que grupos en que área geográfica tienen mas o menos incidencias reportadas.

Objetivo.
> Esta es la primer etapa de un proyecto que se desea permita que las autoridades lleven un **control** y **organizacion** de todos los reportes sobre actos delictivos que ocurren en la ciudad para una mayor organizacion. También podría servir de recurso de consulta para que los ciudadanos se enteren de hechos delictivos cerca o en sus comunidades y hacer un senso de los que podrían ser los lugares con mayor índice delictivo de la capital.

---

## 1. Tecnologías Clave

Lista de las herramientas y tecnologías principales utilizadas en el proyecto.

| Capa | Componente | Versión Utilizada | Próposito |
| :--- | :--- | :--- | :--- |
| **Web Framework Backend** | Django con python **3.12.1** | **4.2.11** | Backend principal, ORM y sistema de rutas. |
| **Web Frontend** | HTML5, CSS3, Bootstrap | **5.3.6** (Bootstrap) | |
| **Mapeo Frontend** | Leaflet.js | **1.9.4** | Renderizado interactivo del mapa en el navegador. |
| **Base de Datos** | PostgreSQL | **16.9** | Almacenamiento de datos relacionales. |
| **Extensiones Geo** | PostGIS | **3.4.2** | Habilita tipos de datos (`PointField`) y funciones espaciales. |
| **Adaptador Python** | psycopg2-binary | **2.9.10** | Conexión de Django a PostgreSQL. |
| **Interoperabilidad** | GDAL | **3.11.0** | Motor de importación y exportacion de datos geoespaciales entre muchos formatos (Shapefile, KML, CSV, etc.). |
| | GEOS | **3.12.1** | Motor matemático para operaciones espaciales y validación entre geometrías. |
| | PROJ | **8.2.1** | Motor de proyección y transformación de coordenadas. |
| **Herramienta GIS** | QGIS | **3.40.8**| Software de escritorio para la visualización, edición y validación de datos en PostGIS. |

---

## 2. Configuración del Entorno (Guía Rápida)

Sigue estos pasos para tener la aplicación funcionando en tu máquina local.

### 2.1. Prerrequisitos

Asegúrate de tener instalado:

* Python
* Pip (Administrador de paquetes de Python)
* Git
* PostgreSQL **[VERSIÓN]** con la extensión **PostGIS** instalada.

### 2.2. Instalación y Puesta en Marcha

1.  **Clonar el repositorio:**
    ```bash
    cd /ruta/NOMBRE_DE_CARPETA/ # Navega a la carpeta donde quieres clonarlo
    git clone https://github.com/AngelFlores123/GestionIncidenciasDelictivas-Django.git
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    python -m venv venv
    venv\Scripts\activate   # En Windows
    ```

3.  **Instalar dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos:**
    * Crea una base de datos en PostgreSQL (ej: `my_app_db`).
    * **Importante:** Habilita la extensión PostGIS en la base de datos:
        ```sql
        CREATE EXTENSION postgis;
        ```
    * Asegúrate de que tu archivo `settings.py` en el proyecto Django esté configurado con las credenciales de tu base de datos.
      ```bash
      DATABASES = {
      'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # No 'django.db.backends.postgresql'
        'NAME': 'my_app_db',
        'USER': '...',
        'PASSWORD': '...',
        'HOST': 'localhost',
        'PORT': '5432',
       }
      }
      ```
    * Modifica las rutas de las librerias al final de `settings.py`:
      ```bash
      GDAL_LIBRARY_PATH = r'C:\Users\...\envs\geodjango_env\Library\bin\gdal.dll'
      GEOS_LIBRARY_PATH = r'C:\Users\...\envs\geodjango_env\Library\bin\geos_c.dll'
      ```

    * Para cargar datos de un archivo, geojson o shapefile, a la base de datos, hacer lo siguiente:
    1. Vamos a usar la herramienta de GDAL llamada `ogr2ogr`.
    2. Con el software QGIS instalado, abrir la consola `OSGeo4W Shell`.
    3. Dentro, dirigete a la carpeta donde se encuentra el dataset.
       ```bash
       cd C:User/ruta/carpeta
       ```
    4. Ejecuta el siguiente comando (quitar `-nlt MultiPolygon` si el dataset solo contiene puntos, lineas o poligonos simples):
       ```bash
       ogr2ogr -f "PostgreSQL" PG:"dbname=NOMBRE_DE_TU_BD host=localhost port=5432 user=TU_USUARIO password=TU_CONTRASENA" "NOMBRE_DATASET.geojson/.shp" -nlt MultiPolygon
       ```
    5. Ahora podrá ver sus datos en una tabla en su base de datos.

5.  **Ejecutar Migraciones:**
    * Ejecutar en la terminal en la raíz de proyecto con el entorno virtual activado:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Iniciar el Servidor:**
    ```bash
    python manage.py runserver
    ```
    La aplicación estará disponible en: `http://127.0.0.1:8000/`

---

## 3. Estructura y Modelos de Datos

### 3.1. Arquitectura de Apps de Django

| App | Propósito | URL Base |
| :--- | :--- | :--- |
| `sid` | Configuraciones principales del proyecto. | NA |
| `**principal**` | Contiene los Modelos, Vistas y Templates para el CRUD de **[ENTIDAD]**. | `/` |

### 3.2. Modelo Geográfico Principal

E
