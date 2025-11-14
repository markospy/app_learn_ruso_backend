# Russian Learning API - FastAPI Backend

API REST para sistema de aprendizaje de conjugaciones verbales y sustantivos en ruso.

## Características

- Autenticación JWT
- Gestión de usuarios con roles (admin, teacher, student)
- CRUD completo para verbos y sustantivos rusos
- Grupos personalizados de verbos y sustantivos
- Sistema de vinculación estudiante-profesor
- Documentación automática con Swagger/OpenAPI

## Requisitos

- Python 3.10+
- PostgreSQL (opcional, SQLite por defecto)

## Instalación

1. Clonar el repositorio y navegar al directorio:
```bash
cd app_learn_ruso_backend
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Inicializar la base de datos y datos iniciales:
```bash
python -m app.scripts.seed
```

## Ejecución

### Desarrollo

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

### Documentación

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Migraciones con Alembic

### Crear una nueva migración

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Revertir migración

```bash
alembic downgrade -1
```

## Estructura del Proyecto

```
app/
├── __init__.py
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración de la aplicación
├── database.py          # Configuración de base de datos
├── models/              # Modelos SQLModel
├── schemas/             # Schemas Pydantic para validación
├── crud/                # Operaciones CRUD
├── api/
│   ├── deps.py         # Dependencias (auth, permisos)
│   └── routes/         # Endpoints de la API
├── core/
│   └── security.py     # Utilidades de seguridad (JWT, bcrypt)
└── scripts/
    └── seed.py         # Script de seeding inicial
```

## Usuario Admin por Defecto

Después de ejecutar el script de seeding:

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

**IMPORTANTE**: Cambiar la contraseña en producción.

## Endpoints Principales

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login (obtiene JWT token)
- `GET /api/auth/me` - Información del usuario actual

### Usuarios
- `GET /api/users/me` - Perfil del usuario actual
- `PUT /api/users/me` - Actualizar perfil

### Verbos
- `GET /api/verbs` - Listar verbos
- `GET /api/verbs/{id}` - Obtener verbo
- `GET /api/verbs/{id}/conjugations` - Conjugaciones agrupadas
- `POST /api/verbs` - Crear verbo (admin/teacher)
- `PUT /api/verbs/{id}` - Actualizar verbo (admin/teacher)
- `DELETE /api/verbs/{id}` - Eliminar verbo (admin/teacher)

### Grupos de Verbos
- `GET /api/verb-groups` - Listar grupos del usuario
- `POST /api/verb-groups` - Crear grupo
- `POST /api/verb-groups/{id}/verbs/{verb_id}` - Agregar verbo al grupo

### Sustantivos
- `GET /api/nouns` - Listar sustantivos
- `POST /api/nouns` - Crear sustantivo (admin/teacher)

### Grupos de Sustantivos
- `GET /api/noun-groups` - Listar grupos del usuario
- `POST /api/noun-groups` - Crear grupo

## Roles y Permisos

### Admin
- Acceso completo a todos los endpoints
- Gestión de usuarios

### Teacher
- Crear/editar/eliminar verbos y sustantivos
- Ver y gestionar estudiantes vinculados
- Crear grupos de verbos y sustantivos

### Student
- Lectura de verbos y sustantivos
- Crear sus propios grupos
- Ver su propio progreso

## Desarrollo

### Formato de código

El proyecto sigue las convenciones PEP 8 y usa herramientas de formato automático.

### Testing

```bash
# Ejecutar tests (cuando se implementen)
pytest
```

## Producción

1. Cambiar `SECRET_KEY` en `.env` (usar un valor seguro)
2. Configurar PostgreSQL en lugar de SQLite
3. Cambiar contraseña del usuario admin
4. Configurar CORS con los dominios correctos
5. Usar un servidor ASGI en producción (ej: Gunicorn con Uvicorn workers)

## Licencia

Este proyecto es privado.

