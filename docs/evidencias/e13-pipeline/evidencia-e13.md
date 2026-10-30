# Evidencia E13 — Pipeline CI/CD

**Fecha:** 2026-10-27
**Autor:** Jair Moshed Castañaza Barrera (DevOps / Automatización)

## Alcance del entregable

Pipeline CI/CD completo con 5 etapas definidas, ejecutado automáticamente en
cada PR y push a las ramas protegidas (`dev`, `qa`, `main`).

## Las 5 etapas

### 1. Build
- Setup del runtime (Python 3.11 + uv)
- Instalación reproducible de dependencias (`uv sync` con lockfile)
- Verificación de versiones de las herramientas

### 2. Lint (Ruff)
- Análisis estático con Ruff (reglas E, F, I de PEP 8 + pyflakes + isort)
- Formato con `ruff format --check`
- Falla el pipeline ante errores de linting en `app/`

### 3. Unit tests (sin BD)
- Ejecuta solo `app/tests/unit/` (50 pruebas con mocks)
- Rápido (<5s), aislado de la BD
- Valida que haya **mínimo 30 pruebas unitarias** (requisito E10)
- Falla si no cumple el umbral

### 4. Integration tests + coverage
- Levanta PostgreSQL 16 como servicio sidecar
- Aplica migraciones Alembic
- Seedea admin con `python -m app.scripts.seed_admin`
- Corre suite completa (78 pruebas) con `pytest --cov=app`
- **Quality gate:** cobertura global ≥60% (configurable)
- Publica reporte HTML + XML como artifact (retención 30 días)

### 5. API tests (Newman)
- Setup de Node.js 22 + Newman + newman-reporter-htmlextra
- Levanta FastAPI en background
- Healthcheck con `/health` antes de correr tests
- Ejecuta la colección Postman (E11)
- Publica reporte HTML como artifact
- **Opcional** hasta que la colección Postman esté terminada

### 6. Status check final (pipeline-status)
- Job agregador que falla si cualquier etapa crítica falló
- Es el status check que **branch protection** debe exigir para mergear

## Características técnicas

| Característica | Implementación |
|----------------|----------------|
| Cache de dependencias | `astral-sh/setup-uv@v3 enable-cache: true` |
| Cancelación de runs duplicados | `concurrency: group` + `cancel-in-progress` |
| Paralelización | Lint + Unit tests corren en paralelo después de Build |
| Service containers | PostgreSQL 16 vía `services:` |
| Artifacts | Reporte HTML cobertura + reporte Newman HTML |
| Fail-fast condicional | Pipeline-status job con `if: always()` |

## Trigger

```yaml
on:
  pull_request:
    branches: [dev, qa, main]
  push:
    branches: [dev, qa, main]
```

Ejecuta en PR y en push a cualquiera de las 3 ramas protegidas.

## Secrets de GitHub Actions requeridos

| Secret | Workflow | Propósito |
|--------|----------|-----------|
| `AWS_ACCESS_KEY_ID` | deploy.yml | Credenciales AWS para deploy |
| `AWS_SECRET_ACCESS_KEY` | deploy.yml | — |
| `AWS_REGION` | deploy.yml | Región (us-east-2) |
| `S3_BUCKET` | deploy.yml | Bucket de artefactos |
| `EB_APP` | deploy.yml | Nombre app Elastic Beanstalk |
| `EB_ENV` | deploy.yml | Nombre environment EB |

## Protección de ramas

Branch protection recomendado en `main` y `qa`:

- Require pull request before merging (1 approval)
- Require status checks: `✓ Pipeline Status`
- Require branches to be up to date
- Dismiss stale reviews on new commits
- No bypass permitido

## Análisis estático SonarQube (E12)

**En CI:** se usa Ruff como sustituto (SonarQube requiere servidor accesible).

**Local (completo):** `.\scripts\sonar-scan.ps1 -Token "squ_..."`

## Archivos creados

- `.github/workflows/ci.yml` — Pipeline principal (309 líneas)
- `.github/workflows/README.md` — Documentación del flujo
- `.github/workflows/deploy.yml` — Deploy a EB (preexistente)
- `sonar-project.properties` — Config SonarQube
- `scripts/sonar-scan.ps1` — Script local para análisis estático
- `tests/api/README.md` — Documentación de pruebas API (E11 pendiente)
