# Pruebas de carga - k6

Entregable E14 Fase 2. Valida RNF-01 (percentil 95 < 3s con 50 VU concurrentes).

## Correr local

Requiere PostgreSQL + app arriba:

```powershell
# Terminal 1: levantar app
docker compose up -d
uv run alembic upgrade head
uv run python -m app.scripts.seed_admin
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: correr k6
k6 run tests/load/sece-load.js
```

## Correr contra EB

```powershell
k6 run -e BASE_URL=https://tu-env.us-east-2.elasticbeanstalk.com `
       -e ADMIN_EMAIL=admin@sece.local `
       -e ADMIN_PASSWORD=TuPassword `
       tests/load/sece-load.js
```

## Interpretar resultados

- `http_req_duration p(95)`: debe ser < 3000ms para pasar RNF-01
- `http_req_failed rate`: tasa de errores debe ser < 1%
- `vus_max`: debe llegar a 50

## Perfil de carga

| Fase | Duracion | VUs objetivo |
|------|----------|--------------|
| Calentamiento | 1 min | 0 -> 20 |
| Meseta | 3 min | 50 |
| Enfriamiento | 1 min | 50 -> 0 |

Total: 5 minutos. Endpoints probados:
1. GET /api/v1/pacientes?q=P (busqueda)
2. GET /api/v1/medicos (listado)
