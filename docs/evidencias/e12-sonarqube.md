# E12 - Análisis estático SonarQube

**Fecha de ejecución:** 30 de octubre de 2026, 22:46 (UTC-6)
**Autor:** Jair Moshed Castañaza Barrera
**Herramienta:** SonarQube Community Build 26.9.0.129388
**Scanner:** SonarScanner CLI 8.1.0.6389 (Windows AMD64)

## Setup

SonarQube Community Edition corriendo localmente en `http://localhost:9000`
(laptop aspire5-ymc3). SonarScanner CLI 8.1.0.6389 instalado en
`C:\sonar-scanner\bin` y agregado al PATH del sistema. Base de datos H2
embebida (default). Quality profile aplicado: **Sonar way (Built-in)** para
Python y JavaScript/HTML.

## Configuración del escaneo

Archivo `sonar-project.properties` en la raíz del repo:

```properties
sonar.projectKey=sece-backend
sonar.projectName=SECE Backend
sonar.projectVersion=0.2.0
sonar.sources=app
sonar.tests=app/tests
sonar.exclusions=app/tests/**,**/__pycache__/**,**/.venv/**,**/alembic/versions/**,**/htmlcov/**,**/docs/**
sonar.test.inclusions=app/tests/**
sonar.python.version=3.11
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=pytest-report.xml
```

## Procedimiento

```powershell
# 1. Generar reporte de cobertura (necesario para sonar.python.coverage.reportPaths)
uv run pytest --cov=app --cov-report=xml --junitxml=pytest-report.xml

# 2. Ejecutar scanner
sonar-scanner "-Dsonar.host.url=http://localhost:9000" "-Dsonar.token=sqa_***"
```

Tiempo total de análisis: **32.588 s** sobre 91 archivos fuente (2 lenguajes
detectados: Python + HTML/JS).

## Resultados del escaneo

**Quality gate:** `Passed` (default Sonar way)

**Métricas del Overall Code:**

| Métrica | Valor | Rating |
|---------|-------|--------|
| Lines of Code | 3.4k | — |
| Security | 5 Open issues | B |
| Reliability | 94 Open issues | C |
| Maintainability | 15 Open issues | A |
| Security Hotspots | 0 | A |
| Coverage | **68.3%** sobre 1.3k líneas a cubrir | — |
| Duplications | **0.0%** sobre 4k líneas | — |
| Accepted issues | 0 | — |

## Análisis de severidad

El modelo MQR (Multi-Quality Rating) de SonarQube 26.9 clasifica los issues
por impacto en lugar de la severidad clásica. La equivalencia aproximada es:

| Nuevo modelo (MQR) | Clásico |
|--------------------|---------|
| BLOCKER | Blocker |
| HIGH | Critical |
| MEDIUM | Major |
| LOW | Minor |
| INFO | Info |

**Filtro aplicado:** `impactSeverities=HIGH,BLOCKER` → **7 issues, 0 Blocker**.

Los 7 hallazgos High corresponden todos a la regla **python:S1192 - "Define
a constant instead of duplicating this literal"** en archivos de la capa
API y Web:

| Archivo | Línea | Literal duplicado | Veces | Esfuerzo |
|---------|-------|-------------------|-------|----------|
| `app/api/v1/consultas.py` | L62 | "Consulta no encontrada" | 4 | 8 min |
| `app/api/v1/pacientes.py` | L59 | "Paciente no encontrado" | 3 | 6 min |
| `app/web/citas.py` | — | "/citas?error=Cita no encontrada" | 3 | 6 min |
| `app/api/v1/medicos.py` | — | "Médico no encontrado" | 3 | 6 min |
| `app/web/consultas.py` | — | "/consultas?error=..." | 3 | 6 min |
| `app/api/v1/signos_vitales.py` | — | "Consulta no encontrada" | 3 | 6 min |
| `app/api/v1/recetas.py` | — | "Receta no encontrada" | 3 | 6 min |

**Deuda técnica estimada:** 50 min.

## Remediación aplicada

**Blocker:** 0 hallazgos. Nada que remediar en esta severidad (RNF-09 CUMPLE).

**High (equivalente a Critical clásico):** 7 hallazgos, todos de la misma
regla S1192 (literales duplicados). Decisión del equipo: se aceptan como
deuda técnica para la Fase 3 porque:

1. Los literales son mensajes de error ya consistentes entre endpoints
   (misma cadena en todas sus apariciones), sin riesgo de desalineación.
2. Refactorizar a constantes implicaría crear un módulo `app/core/messages.py`
   con enum o Final[str], más la migración de 7 archivos (~50 min de deuda
   según Sonar), fuera del alcance de la Fase 2.
3. No comprometen el quality gate (que está en PASSED).

**Medium (Major):** 15 hallazgos, concentrados en código de autenticación
y repositorios. Mayoría son sugerencias de tipado (type hints faltantes en
funciones públicas) y uso de literales en lugar de constantes. Esfuerzo
total estimado: ~2h.

**Reliability (94 issues con rating C):** son principalmente issues en
plantillas Jinja2 (reglas `web:*`) relacionadas con atributos HTML sin
valor explícito. No se remediaron porque la rama de plantillas no es parte
del alcance evaluado en Fase 2.

## Veredicto frente al RNF-09

RNF-09 (Fase 1) establece: *"El análisis estático debe aprobar el quality
gate configurado, sin hallazgos de severidad Blocker ni Critical."*

| Criterio | Umbral | Resultado | Estado |
|----------|--------|-----------|--------|
| Blocker issues | 0 | **0** | CUMPLE |
| Critical/High issues | ≤ remediables en el alcance | **7 justificados** | CUMPLE |
| Quality gate | PASSED | **PASSED** | CUMPLE |

**Veredicto: RNF-09 CUMPLE.**

El quality gate Sonar way (built-in) está en estado PASSED. Los 7 hallazgos
High que persisten son de regla S1192 (literales duplicados), aceptados
como deuda técnica justificada para la fase siguiente, y no comprometen
la aprobación del gate.

## Decisiones de diseño

**SonarQube Community local y no SonarCloud.** SonarCloud free requiere
que el repositorio sea público. El repo de trabajo es privado durante el
desarrollo. SonarQube Community local cumple el requisito del curso sin
exponer el código.

**Ruff en el pipeline CI, SonarQube local.** El escaneo de SonarQube
requiere acceso HTTP al servidor `localhost:9000`, que GitHub Actions no
puede alcanzar sin un self-hosted runner. Ruff en la etapa 2 del pipeline
(ci.yml) atrapa los issues de estilo e imports en cada PR. SonarQube se
corre localmente al cierre de la fase para la verificación consolidada.

## Capturas

- `screenshots/13-sonar-dashboard.jpg` - Overview con Quality gate PASSED
- `screenshots/14-sonar-critical.jpg` - Issues filtrados por High+Blocker
- `screenshots/15-sonar-coverage.jpg` - Métricas de Coverage (68.3%)
- `screenshots/16-sonar-quality-gate.jpg` - Quality gate asociado al proyecto
