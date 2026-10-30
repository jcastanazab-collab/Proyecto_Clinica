# E12 - Analisis estatico SonarQube

**Fecha:** 29/10/2026
**Autor:** Jair Moshed Castanaza Barrera

## Setup

SonarQube Community corriendo localmente en `localhost:9000` (laptop
aspire5-ymc3). SonarScanner CLI 8.1.0.6389 instalado en `C:\sonar-scanner\bin`
y agregado al PATH del sistema.

Config: `sonar-project.properties` en la raiz del repo. Reglas por defecto
del plugin de Python + reglas custom del quality profile "Sonar way".

## Procedimiento de escaneo

```powershell
# 1. Generar reporte cobertura previo (necesario para sonar.python.coverage.reportPaths)
uv run pytest --cov=app --cov-report=xml --junitxml=pytest-report.xml

# 2. Ejecutar scanner con el helper script
.\scripts\sonar-scan.ps1 -Token "squ_xxx"
```

## Hallazgos iniciales

Tras el primer escaneo sobre la rama `dev` (commit `a2d42e2`):

| Severidad | Cantidad | Observacion |
|-----------|----------|-------------|
| Blocker | 0 | - |
| Critical | 1 | python:S5411 en `app/api/v1/pacientes.py` - endpoint GET sin filtro de rol expone campo direccion a cualquier usuario autenticado |
| Major | 5 | S1192 (literales duplicados), S5886 (type hint faltante en 3 funciones repo), S1481 (variable local no usada en web/consultas.py) |
| Minor | 14 | Comentarios TODO sin dueno, docstrings faltantes en funciones publicas |
| Info | 23 | Sugerencias de estilo cubiertas por Ruff |

Coverage detectada por Sonar: **69%** (consistente con pytest-cov)
Duplicacion: **1.4%**
Technical debt estimado: **2h10m**

## Remediaciones aplicadas

### Critical (1)

**S5411** - `GET /api/v1/pacientes/{id}` solo exigia autenticacion
general pero el `response_model=PacienteRead` expone `direccion` y `email`,
datos sensibles para rol RECEPCIONISTA en contexto clinico.

Resolucion: alineada con DEF-06 catalogado en Fase 1. El equipo decidio
diferir la remediacion a Fase 3 porque implica un cambio de response schema
(`PacienteReadLimited` vs `PacienteReadFull`) que afecta tanto la API como
las vistas web. Se agrego en el backlog como issue bloqueante previo a prod.

### Major (5)

Aceptados como aprendizaje. Los 3 type hints faltantes y la variable no
usada se corrigen de forma segura:

- `app/repositories/consulta.py`: agregar `-> list[dict]` en
  `list_historial_paciente`
- `app/web/consultas.py` linea 32: remover variable `_old` no usada

Los 2 restantes (S1192 literales duplicados en templates HTML) se dejan
para Fase 3 porque son mas estilisticos que de riesgo.

### Minor + Info

No bloquean. Son objetivo del Fase 3 cuando se refactoricen docstrings.

## Resultado post-remediacion

| Severidad | Antes | Despues |
|-----------|-------|---------|
| Blocker | 0 | 0 |
| Critical | 1 | 1 (diferido con justificacion) |
| Major | 5 | 2 |
| Minor | 14 | 14 |
| Info | 23 | 23 |

**Quality gate:** PASS respecto a RNF-09 ("sin Blocker y Critical remediables
dentro del alcance"). El Critical restante tiene plan de accion documentado
en el backlog.

## Capturas (en screenshots/)

- `sonar-dashboard-inicial.png` - vista del primer scan
- `sonar-dashboard-final.png` - post-remediacion
- `sonar-quality-gate.png` - estado del gate

## Decisiones de diseno

**Por que SonarQube Community local y no SonarCloud.** SonarCloud free
requiere repo publico. El proyecto es privado durante el desarrollo. La
alternativa seria pagar o abrir el repo. Decidimos usar la version Community
local, que cubre el requisito del curso sin exponer el codigo.

**Por que Ruff en el pipeline CI.** El escaneo de SonarQube requiere acceso
HTTP al servidor en `localhost:9000`, que GitHub Actions no puede alcanzar
sin un self-hosted runner. Ruff en la etapa 2 del pipeline (`ci.yml`)
atrapa los issues de estilo e imports en cada PR. SonarQube se corre
localmente antes de PRs grandes o releases.
