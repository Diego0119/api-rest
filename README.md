# Gastos Compartidos

## Descripción

Proyecto base para tarea N° 2 de Bases de Datos II.

## ¿Cómo generar una copia del repositorio?

### Fork

Hacer fork al repositorio (botón ubicado en la parte superior derecha).
En este caso, el repositorio quedará como público.

### Copia privada

Primero, crea un repositorio vacío en GitHub, y copia su URL.

```bash
# clona el repositorio y entra al directorio
git clone https://github.com/dialvarezs/hw2-bd2-2024
cd hw2-bd2-2024
# renombra el origin a upstream
git remote rename origin upstream
# agrega tu repositorio como origin
git remote add origin <url de tu repositorio>
```

## ¿Cómo inicializar el repositorio?

1. Dentro del directorio del proyecto, instala las dependencias con `uv``:
    ```bash
    uv sync
    ````
2. Configura la base de datos en un archivo `.env` (si no quieres usar la base de datos por defecto).
3. Aplica las migraciones con Alembic para crear las tablas en la base de datos. Recuerda que la base de datos debe
   estar creada.
    ```bash
    uv run alembic upgrade head
    ```
4. Levanta la API:
    ```bash
    uv run litestar run --reload
    ```

## Tips
Para formatear el código, puedes usar `ruff format`:
```bash
uv run ruff format app/ migrations/
```

Para verificar la calidad del código, puedes usar `ruff check`:
```bash
uv run ruff check app/ migrations/
```
Puedes añadir `--fix` para intentar corregir los errores automáticamente.

Para verificar errores de tipos, puedes usar `mypy`:
```bash
uv run mypy app/
```