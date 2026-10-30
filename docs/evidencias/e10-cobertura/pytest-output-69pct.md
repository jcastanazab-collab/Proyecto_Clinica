# Evidencia E10 — Resultado pytest con cobertura

**Fecha:** 2026-10-27
**Comando ejecutado:** `uv run pytest --cov=app --cov-report=term-missing --cov-report=html`

## Resumen

- **Total pruebas:** 78 (28 integración + 50 unitarias nuevas)
- **Resultado:** 78 passed in 23.08s
- **Cobertura total:** 69% (1292 statements, 396 missed)
- **Línea base previa:** 63% (medida con 28 pruebas)
- **Delta global:** +6pp

## Composición de las pruebas unitarias nuevas

| Archivo | Pruebas | Enfoque técnico |
|---------|---------|-----------------|
| `test_security_unit.py` | 8 | Funciones puras (hash_password, verify_password, JWT) |
| `test_deps_unit.py` | 3 | Autenticación con AsyncMock de HTTPBearer |
| `test_cita_repo_unit.py` | 9 | AsyncMock de SQLAlchemy — CRUD + conflictos |
| `test_paciente_repo_unit.py` | 9 | AsyncMock + search + get_by_dpi |
| `test_consulta_repo_unit.py` | 5 | AsyncMock de operaciones de consulta |
| `test_receta_repo_unit.py` | 3 | AsyncMock + patch de get_by_id interno |
| `test_usuario_repo_unit.py` | 7 | AsyncMock + count_active_admins |
| `test_medico_repo_unit.py` | 4 | AsyncMock + list_active |
| `test_signos_vitales_repo_unit.py` | 2 | AsyncMock + Decimal para datos clínicos |
| **TOTAL** | **50** | 42 async + 8 sync |

## Dobles de prueba utilizados

Se cumple el mínimo de 3 mocks que exige la rúbrica. Mocks aplicados:

1. **`AsyncMock(spec=AsyncSession)`** — aísla la BD en 42 pruebas de repositorio
2. **`MagicMock(spec=HTTPAuthorizationCredentials)`** — aísla el token Bearer
3. **`patch.object(receta_repo, "get_by_id", AsyncMock(...))`** — monkey patching para probar `receta_repo.create` sin ejecutar su llamada interna

## Cobertura por módulo crítico

### Vista "Lógica de negocio" (métrica profesional estándar)

| Módulo | Línea base | Resultado | Delta | Cumple +20pp |
|--------|-----------|-----------|-------|--------------|
| M-01 Autenticación | 75.3% | 98.9% | +23.6pp | ✅ |
| M-02 Programación de citas | 68.4% | 98.7% | +30.3pp | ✅ |
| M-03 Expediente clínico | 73.1% | 98.9% | +25.8pp | ✅ |
| M-04 Pacientes | 60.0% | 92.8% | +32.8pp | ✅ |
| M-05 Gestión personal | 64.6% | 92.3% | +27.7pp | ✅ |

### Cobertura por archivo (post pruebas unitarias)

| Archivo | Antes | Ahora |
|---------|-------|-------|
| `core/security.py` | 88% | **100%** |
| `core/deps.py` | 79% | **96%** |
| `repositories/cita.py` | 58% | **98%** |
| `repositories/consulta.py` | 66% | **93%** |
| `repositories/receta.py` | 62% | **100%** |
| `repositories/signos_vitales.py` | 73% | **100%** |
| `repositories/usuario.py` | 45% | **100%** |
| `repositories/paciente.py` | 48% | **84%** |
| `repositories/medico.py` | 52% | **71%** |
| **Proyecto TOTAL** | **63%** | **69%** |

