# Prompt para Crear API FastAPI - Sistema de Aprendizaje de Ruso

Necesito crear una API REST con FastAPI para una aplicación de aprendizaje de conjugaciones verbales y sustantivos en ruso. La aplicación actual es un frontend Vue.js que usa SQLite en el navegador, y ahora necesito migrar a una arquitectura backend con autenticación y gestión de usuarios.

## Contexto del Proyecto

La aplicación permite a estudiantes practicar conjugaciones de verbos rusos. Actualmente funciona con SQLite en el navegador (sql.js), pero necesito escalar a un sistema multi-usuario con roles y grupos personalizados.

## Especificaciones de la Base de Datos

### 1. Tabla `roles`
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(50) UNIQUE NOT NULL (valores: 'admin', 'teacher', 'student')
```

**Datos iniciales:**
- (1, 'admin')
- (2, 'teacher')
- (3, 'student')

### 2. Tabla `users`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- name: VARCHAR(100) NOT NULL
- country: VARCHAR(100)
- email: VARCHAR(255) UNIQUE NOT NULL
- username: VARCHAR(50) UNIQUE NOT NULL
- password: VARCHAR(255) NOT NULL (hash bcrypt)
- language: VARCHAR(10) DEFAULT 'es' (código de idioma: 'es', 'en', etc.)
- id_rol: INTEGER NOT NULL, FOREIGN KEY REFERENCES roles(id)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- is_active: BOOLEAN DEFAULT TRUE
```

### 3. Tabla `link_student_teacher`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- id_student: INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id)
- id_teacher: INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE(id_student, id_teacher)
```

### 4. Tabla `verbs`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- infinitive: VARCHAR(100) NOT NULL UNIQUE
- conjugationType: INTEGER NOT NULL (1 o 2, para 1ª o 2ª conjugación)
- root: VARCHAR(100) NOT NULL
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Conjugaciones en Presente (Present Tense)
- present_ya: VARCHAR(50)      -- Я (yo)
- present_ty: VARCHAR(50)       -- Ты (tú)
- present_on_ona: VARCHAR(50)   -- Он/Она (él/ella)
- present_my: VARCHAR(50)      -- Мы (nosotros)
- present_vy: VARCHAR(50)      -- Вы (ustedes)
- present_oni: VARCHAR(50)     -- Они (ellos)

-- Conjugaciones en Pasado (Past Tense)
- past_masculine: VARCHAR(50)  -- Pasado masculino
- past_feminine: VARCHAR(50)   -- Pasado femenino
- past_neuter: VARCHAR(50)     -- Pasado neutro
- past_plural: VARCHAR(50)     -- Pasado plural

-- Conjugaciones en Futuro (Future Tense)
- future_ya: VARCHAR(50)
- future_ty: VARCHAR(50)
- future_on_ona: VARCHAR(50)
- future_my: VARCHAR(50)
- future_vy: VARCHAR(50)
- future_oni: VARCHAR(50)

-- Conjugaciones en Imperativo (Imperative)
- imperative_singular: VARCHAR(50)  -- Imperativo singular
- imperative_plural: VARCHAR(50)    -- Imperativo plural
```

### 5. Tabla `verb_groups`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- name_group: VARCHAR(100) NOT NULL
- id_user: INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### 6. Tabla `verb_group_verbs` (tabla de relación muchos a muchos)
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- id_group: INTEGER NOT NULL, FOREIGN KEY REFERENCES verb_groups(id) ON DELETE CASCADE
- id_verb: INTEGER NOT NULL, FOREIGN KEY REFERENCES verbs(id) ON DELETE CASCADE
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE(id_group, id_verb)
```

### 7. Tabla `noun_groups`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- name_group: VARCHAR(100) NOT NULL
- id_user: INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### 8. Tabla `nouns`
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- sustantivo: VARCHAR(100) NOT NULL
- singular: VARCHAR(100) NOT NULL
- plural: VARCHAR(100) NOT NULL
- gender: VARCHAR(10) NOT NULL CHECK(gender IN ('masculine', 'feminine', 'neuter'))
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### 9. Tabla `noun_group_nouns` (tabla de relación muchos a muchos)
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- id_group: INTEGER NOT NULL, FOREIGN KEY REFERENCES noun_groups(id) ON DELETE CASCADE
- id_noun: INTEGER NOT NULL, FOREIGN KEY REFERENCES nouns(id) ON DELETE CASCADE
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE(id_group, id_noun)
```

## Requisitos Técnicos

### Stack Tecnológico
- **Framework**: FastAPI
- **Base de datos**: PostgreSQL (o SQLite para desarrollo)
- **ORM**: SQLModel
- **Autenticación**: JWT (JSON Web Tokens)
- **Hashing de contraseñas**: bcrypt
- **Validación**: Pydantic v2
- **CORS**: Habilitado para frontend Vue.js

### Estructura del Proyecto
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── verb.py
│   │   ├── verb_group.py
│   │   ├── noun.py
│   │   └── noun_group.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── verb.py
│   │   ├── verb_group.py
│   │   ├── noun.py
│   │   └── noun_group.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py (dependencias: auth, get_current_user, etc.)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── verbs.py
│   │   │   ├── verb_groups.py
│   │   │   ├── nouns.py
│   │   │   └── noun_groups.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py (JWT, bcrypt)
│   │   └── config.py
│   └── crud/
│       ├── __init__.py
│       ├── user.py
│       ├── verb.py
│       ├── verb_group.py
│       ├── noun.py
│       └── noun_group.py
├── alembic/ (migraciones)
├── requirements.txt
└── .env
```

## Endpoints Requeridos

### Autenticación (`/api/auth`)
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login (retorna JWT token)
- `POST /api/auth/refresh` - Refrescar token
- `GET /api/auth/me` - Obtener usuario actual

### Usuarios (`/api/users`)
- `GET /api/users/me` - Perfil del usuario actual
- `PUT /api/users/me` - Actualizar perfil
- `GET /api/users/{id}` - Obtener usuario (solo admin/teacher)
- `GET /api/users` - Listar usuarios (solo admin)
- `PUT /api/users/{id}` - Actualizar usuario (solo admin)
- `DELETE /api/users/{id}` - Eliminar usuario (solo admin)

### Estudiantes-Profesores (`/api/students`)
- `GET /api/students` - Listar estudiantes del profesor actual
- `POST /api/students/{student_id}/link` - Vincular estudiante a profesor
- `DELETE /api/students/{student_id}/unlink` - Desvincular estudiante
- `GET /api/students/{student_id}/progress` - Progreso del estudiante (solo teacher)

### Verbos (`/api/verbs`)
- `GET /api/verbs` - Listar verbos (con paginación y filtros)
- `GET /api/verbs/{id}` - Obtener verbo por ID
- `POST /api/verbs` - Crear verbo (solo admin/teacher)
- `PUT /api/verbs/{id}` - Actualizar verbo (solo admin/teacher)
- `DELETE /api/verbs/{id}` - Eliminar verbo (solo admin/teacher)
- `GET /api/verbs/{id}/conjugations` - Obtener todas las conjugaciones de un verbo

### Grupos de Verbos (`/api/verb-groups`)
- `GET /api/verb-groups` - Listar grupos del usuario actual
- `GET /api/verb-groups/{id}` - Obtener grupo con sus verbos
- `POST /api/verb-groups` - Crear grupo
- `PUT /api/verb-groups/{id}` - Actualizar grupo
- `DELETE /api/verb-groups/{id}` - Eliminar grupo
- `POST /api/verb-groups/{id}/verbs/{verb_id}` - Agregar verbo al grupo
- `DELETE /api/verb-groups/{id}/verbs/{verb_id}` - Eliminar verbo del grupo

### Sustantivos (`/api/nouns`)
- `GET /api/nouns` - Listar sustantivos (con paginación y filtros)
- `GET /api/nouns/{id}` - Obtener sustantivo por ID
- `POST /api/nouns` - Crear sustantivo (solo admin/teacher)
- `PUT /api/nouns/{id}` - Actualizar sustantivo (solo admin/teacher)
- `DELETE /api/nouns/{id}` - Eliminar sustantivo (solo admin/teacher)

### Grupos de Sustantivos (`/api/noun-groups`)
- `GET /api/noun-groups` - Listar grupos del usuario actual
- `GET /api/noun-groups/{id}` - Obtener grupo con sus sustantivos
- `POST /api/noun-groups` - Crear grupo
- `PUT /api/noun-groups/{id}` - Actualizar grupo
- `DELETE /api/noun-groups/{id}` - Eliminar grupo
- `POST /api/noun-groups/{id}/nouns/{noun_id}` - Agregar sustantivo al grupo
- `DELETE /api/noun-groups/{id}/nouns/{noun_id}` - Eliminar sustantivo del grupo

## Reglas de Autorización

1. **Admin**: Acceso completo a todo
2. **Teacher**:
   - Puede crear/editar/eliminar verbos y sustantivos
   - Puede ver y gestionar sus estudiantes vinculados
   - Puede crear grupos de verbos y sustantivos
3. **Student**:
   - Solo lectura de verbos y sustantivos públicos
   - Puede crear sus propios grupos de verbos y sustantivos
   - Puede ver su propio progreso

## Funcionalidades Adicionales

1. **Sistema de migraciones**: Usar Alembic para gestionar cambios en la base de datos
2. **Seeding inicial**: Script para crear roles iniciales y usuario admin por defecto
3. **Validación de datos**: Usar Pydantic para validar todos los inputs
4. **Manejo de errores**: Respuestas de error consistentes
5. **Documentación automática**: FastAPI genera Swagger/OpenAPI automáticamente
6. **Variables de entorno**: Configuración mediante archivo .env

## Ejemplo de Respuesta JSON

### Login exitoso:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "juan_student",
    "email": "juan@example.com",
    "name": "Juan Pérez",
    "role": "student"
  }
}
```

### Verbo completo:
```json
{
  "id": 1,
  "infinitive": "говорить",
  "conjugationType": 2,
  "root": "говор",
  "present": {
    "ya": "говорю",
    "ty": "говоришь",
    "on_ona": "говорит",
    "my": "говорим",
    "vy": "говорите",
    "oni": "говорят"
  },
  "past": {
    "masculine": "говорил",
    "feminine": "говорила",
    "neuter": "говорило",
    "plural": "говорили"
  },
  "future": { ... },
  "imperative": {
    "singular": "говори",
    "plural": "говорите"
  }
}
```

## Tareas Específicas

1. Crear estructura de carpetas del proyecto
2. Configurar FastAPI con SQLAlchemy y PostgreSQL
3. Crear modelos SQLAlchemy para todas las tablas
4. Crear schemas Pydantic para validación
5. Implementar autenticación JWT
6. Crear CRUD operations para cada entidad
7. Implementar endpoints con autorización por roles
8. Crear sistema de migraciones con Alembic
9. Script de seeding para roles y usuario admin
10. Configurar CORS para frontend Vue.js
11. Documentación en código (docstrings)

## Notas Importantes

- Las contraseñas deben hashearse con bcrypt antes de guardarse
- Los tokens JWT deben tener expiración (ej: 24 horas)
- Implementar refresh tokens para mejor seguridad
- Validar que los emails y usernames sean únicos
- Los profesores solo pueden ver estudiantes que les están vinculados
- Los estudiantes solo pueden ver sus propios grupos
- Los verbos y sustantivos pueden ser públicos (sin id_user) o privados (con id_user)

Por favor, crea el código base completo siguiendo las mejores prácticas de FastAPI y Python.

