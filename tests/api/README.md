# Pruebas API con Postman + Newman

**Entregable:** E11 Fase 2 (15 pruebas API con aserciones automáticas)

## Archivos esperados

- `sece.postman_collection.json` — Colección exportada desde Postman Desktop
- `sece.postman_environment.json` — Variables de entorno (BASE_URL, admin_token)

## Correr localmente

```powershell
# Requiere Newman instalado globalmente: npm install -g newman
newman run tests/api/sece.postman_collection.json `
       --environment tests/api/sece.postman_environment.json `
       --reporters cli,htmlextra `
       --reporter-htmlextra-export newman-report.html
```

## Correr en CI

Se ejecuta automáticamente en la etapa 5 del pipeline (`.github/workflows/ci.yml`).
El reporte queda como artifact descargable del run.

## Estructura mínima de la colección (15 requests)

| Grupo | Request | Status esperado |
|-------|---------|-----------------|
| Auth | POST /api/v1/auth/login (admin OK) | 200 |
| Auth | POST /api/v1/auth/login (bad password) | 401 |
| Auth | POST /api/v1/auth/login (inactive user) | 401 |
| Pacientes | POST /api/v1/pacientes (crear) | 201 |
| Pacientes | GET /api/v1/pacientes (listar) | 200 |
| Pacientes | GET /api/v1/pacientes?q=DPI (buscar) | 200 |
| Pacientes | POST /api/v1/pacientes (DPI duplicado) | 409 |
| Flujo clínico | POST /api/v1/citas (crear) | 201 |
| Flujo clínico | PATCH /api/v1/citas/{id} (cancelar) | 200 |
| Flujo clínico | POST /api/v1/consultas | 201 |
| Flujo clínico | POST /api/v1/consultas/{id}/signos-vitales | 201 |
| Flujo clínico | POST /api/v1/recetas | 201 |
| Autorización | POST /api/v1/pacientes (recepcionista OK) | 201 |
| Autorización | POST /api/v1/pacientes (medico — rol equivocado) | 403 |
| Autorización | GET /api/v1/usuarios (medico — DEF-06) | 403 |
