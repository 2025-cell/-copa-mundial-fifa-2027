# Copa Mundial FIFA 2027 — Sistema web (Flask + MongoDB)

Sistema completo para el proyecto escolar: registro/login, noticias, partidos,
equipos, estadísticas, apuestas (con restricción de edad) y panel de administrador.

## 1. Instalar dependencias

```
pip install -r requirements.txt
```

## 2. Configurar MongoDB Atlas

Edita la variable `MONGO_URI` en `app.py` (o defínela como variable de entorno)
con tu cadena de conexión real de MongoDB Atlas:

```
export MONGO_URI="mongodb+srv://usuario:password@tucluster.mongodb.net/copa_mundial_fifa"
```

## 3. Poblar datos de ejemplo (opcional pero recomendado)

```
python poblar_datos.py
```

Esto crea algunos equipos y estadios de prueba.

## 4. Ejecutar la aplicación

```
python app.py
```

Abre tu navegador en: http://127.0.0.1:5000

## 5. Crear el usuario administrador

Visita una sola vez: http://127.0.0.1:5000/setup-admin

Esto crea:
- Correo: admin@copamundial.com
- Contraseña: admin123

**Bórralo o coméntalo en app.py después de usarlo (ruta `/setup-admin`).**

## Estructura del proyecto

```
copa_mundial/
├── app.py                 # Rutas y lógica principal
├── poblar_datos.py        # Datos de ejemplo
├── requirements.txt
├── templates/              # HTML (Jinja2)
└── static/
    ├── css/style.css
    └── js/main.js
```

## Colecciones de MongoDB

- usuarios, equipos, jugadores, partidos, noticias, apuestas,
  estadios, resultados, estadisticas, administradores

## Nota sobre el login

La pantalla de inicio de sesión incluye una franja con fotos de jugadores
jóvenes destacados (Bellingham, Yamal, Musiala, Endrick, Pedri) como elemento
decorativo, siguiendo el estilo visual "moderno con jugadores atractivos y un
balón de fútbol" definido en tu cuestionario de diseño. Las imágenes se cargan
desde Unsplash; puedes reemplazarlas por tus propias fotos en
`static/img/` y actualizar las rutas en la lista `JUGADORES_LOGIN` de `app.py`.
