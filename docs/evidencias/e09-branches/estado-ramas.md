# Evidencia E9 — Estrategia de ramas

**Fecha:** 2026-10-27
**Autor:** Jair Moshed Castañaza Barrera

## Ramas creadas localmente

```
* dev    ← rama de trabajo (base para features)
  main   ← PROD (always deployable)
  qa     ← pre-producción (release candidate)
```

## Política de promoción

| Desde | Hacia | Trigger | Validación |
|-------|-------|---------|------------|
| `feature/*` | `dev` | PR con 1 review | CI verde (tests + lint) |
| `dev` | `qa` | PR semanal | CI verde + API tests OK |
| `qa` | `main` (PROD) | PR tras validación | CI verde + aprobación manual |

## Ramas en remoto (histórico Fase 1)

- `main`
- `feature/base-fastapi` (mergeada)
- `feature/setup-base` (mergeada — autor Jair, PR #3)
- `feature/gestion-clinica` (mergeada)
- `fix/env`, `fix/actualizar-readme-docker`, `fix/reparar-pruebas`
