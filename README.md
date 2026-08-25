# MiMedidor

Aplicación web progresiva (PWA) para el registro y la verificación del consumo de agua domiciliar en Costa Rica, mediante la lectura automática por fotografía del hidrómetro ya instalado en la vivienda.

Proyecto Integrador — Invenio Fest, III Trimestre 2026.

> **¿Primera vez en el proyecto?** Empezá por [`docs/como-empezar.md`](docs/como-empezar.md):
> qué instalar, cómo conectarte a GitHub y cómo trabajar una tarjeta de principio a fin.

## Problema

En Costa Rica la lectura del consumo de agua domiciliar se realiza de forma manual y el abonado no tiene forma práctica de verificarla contra lo que paga. MiMedidor permite fotografiar el hidrómetro, obtener la lectura automáticamente, mantener un historial propio y contrastarlo contra la factura, sin requerir hardware adicional.

## Equipo

| Integrante | Rol Scrum |
|---|---|
| José Pablo Ramírez Sánchez | Scrum Master · Equipo de desarrollo |
| Yariel Andrey Elizondo Jiménez | Equipo de desarrollo |
| Isaac Felipe Morún Moreira | Product Owner · Equipo de desarrollo |

Universidad Invenio · Carrera de Tecnología de la Información y Comunicación Empresarial (TICE)

## Stack tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| Cliente | Vite + React + TypeScript | Instalable sin tienda de aplicaciones; compatible con pruebas end-to-end estándar (Cypress); reversible a nativo si el proyecto continúa. **La PWA en sí (manifest y service worker) todavía no está armada** — ver `CLAUDE.md` §13.5. |
| Backend | Python + FastAPI + Uvicorn | Permite ejecutar el procesamiento de imagen en el mismo proceso, sin un servicio adicional. |
| Procesamiento de imagen | OpenCV + Tesseract (vía `pytesseract`) | Corrección de perspectiva, segmentación y reconocimiento de dígitos. La librería de OCR quedó decidida en T-02b. |
| Base de datos | PostgreSQL | Motor relacional, autorizado por el profesor de Base de Datos. Ver `/database/README.md` para la equivalencia de mecanismos de control de errores respecto a la rúbrica. |
| CI/CD | GitHub Actions | Integración continua con tres jobs (cliente, servidor y base de datos) en cada Pull Request. **La entrega continua todavía no está** — ver `CLAUDE.md` §13.7. |

## Estructura del repositorio

```
mimedidor/
├── CLAUDE.md            # Contexto del proyecto — leer antes de trabajar
├── client/              # Aplicación web (Vite + React + TS)
├── server/              # API backend y procesamiento de imagen
├── database/
│   ├── scripts/         # Creación de esquema, roles, permisos
│   └── migrations/       # Cambios incrementales al esquema
├── docs/
│   ├── architecture/     # Diagramas y decisiones técnicas
│   └── scrum/             # Registro de ceremonias, backlog, retrospectivas
└── .github/
    └── workflows/         # Pipelines de CI/CD
```

## Flujo de trabajo (Feature Branch Workflow)

La rama `main` se mantiene siempre estable y desplegable. Todo cambio se desarrolla en una rama derivada:

- `feature/descripcion-corta` — funcionalidad nueva
- `bugfix/descripcion-corta` — corrección de errores

**Reglas sobre `main`:**
1. No se permite push directo.
2. Todo cambio entra mediante Pull Request.
3. El PR requiere al menos una aprobación de otro integrante.
4. Los checks de integración continua deben pasar antes de habilitar el merge.

## Definition of Done

Una tarjeta se considera Hecha cuando:

1. El código está en una rama `feature/` o `bugfix/`.
2. Se abrió un Pull Request hacia `main`.
3. Al menos otro integrante aprobó el PR.
4. Los checks de CI pasaron en verde.
5. El PR fue mergeado a `main`.
6. La documentación asociada quedó actualizada si aplica.
7. Los criterios de aceptación de la tarjeta se cumplen y fueron verificados.

Detalle completo en [`docs/definition-of-done.md`](docs/definition-of-done.md).

## Metodología

El desarrollo se gestiona bajo Scrum. Las tareas son [Issues de este repositorio](../../issues), agrupadas por *milestone* según la entrega a la que pertenecen, y etiquetadas por área, tipo, estimación en puntos y rúbrica del curso que las evalúa.

Las ceremonias se registran en [`docs/scrum/`](docs/scrum/).

El Sprint 1 se gestionó en Trello; ese tablero quedó congelado como archivo y su contenido está respaldado en [`docs/scrum/sprint-1-tarjetas.md`](docs/scrum/sprint-1-tarjetas.md). El historial no se migró a Issues a propósito — ver `CLAUDE.md` §9.

## Cómo ejecutar el proyecto

*(completar una vez definido el backend en T-01/T-15)*
