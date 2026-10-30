# Workflows de CI/CD — SECE

## Archivos

| Workflow | Trigger | Propósito |
|----------|---------|-----------|
| `ci.yml` | PR + push a dev/qa/main | Pipeline de 5 etapas (build → lint → unit → integration → api) |
| `deploy.yml` | push a main | Deploy automático a AWS Elastic Beanstalk |
| `tests.yml` | (legacy) PR | Pipeline simple preexistente de Fase 1 — mantenido por compatibilidad |

## Pipeline `ci.yml` — Las 5 etapas

```
┌─────────────┐
│  1. Build   │ ◄── Setup uv + install deps
└──────┬──────┘
       ├─────────────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  2. Lint    │   │  3. Unit    │ ◄── 50 pruebas con mocks (sin BD)
│   (Ruff)    │   │   tests     │     Valida mínimo 30 pruebas (E10)
└─────────────┘   └──────┬──────┘
                         │
                         ▼
                  ┌──────────────────────┐
                  │ 4. Integration tests │ ◄── Postgres 16 + pytest completo
                  │    + coverage        │     Quality gate: ≥60% global
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ 5. API tests        │ ◄── Newman + Postman collection
                  │    (Newman)         │     Opcional hasta que E11 esté lista
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ ✓ Pipeline Status   │ ◄── Status check para branch protection
                  └─────────────────────┘
```

## Secrets requeridos en GitHub

| Secret | Dónde se usa | Valor típico |
|--------|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | deploy.yml | IAM user con permisos EB + S3 |
| `AWS_SECRET_ACCESS_KEY` | deploy.yml | — |
| `AWS_REGION` | deploy.yml | `us-east-2` |
| `S3_BUCKET` | deploy.yml | Nombre del bucket de artefactos |
| `EB_APP` | deploy.yml | Nombre de la Application en EB |
| `EB_ENV` | deploy.yml | Nombre del Environment en EB |

Configurar en: `Settings → Secrets and variables → Actions → New repository secret`

## Branch protection recomendado

Activar en `Settings → Branches` para `main` y `qa`:

- [x] Require a pull request before merging
- [x] Require approvals (1)
- [x] Require status checks to pass before merging:
  - `✓ Pipeline Status`
- [x] Require branches to be up to date before merging
- [x] Do not allow bypassing the above settings

## Análisis estático con SonarQube (local)

El pipeline usa Ruff en CI (SonarQube requiere servidor accesible).
Para análisis SonarQube completo correr localmente:

```powershell
.\scripts\sonar-scan.ps1 -Token "squ_tu_token"
```

Requisitos:
- SonarQube Community corriendo en localhost:9000
- `sonar-scanner` CLI en el PATH
- Token generado en SonarQube

Esto cumple el entregable E12.
