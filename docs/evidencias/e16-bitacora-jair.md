# Bitacora Individual - Fase 2

**Nombre:** Jair Moshed Castanaza Barrera
**Carne:** 0900-20-12951
**Rol:** Ingeniero de Plataforma / DevOps + Ingeniero de Automatizacion
**Periodo:** 27 al 30 de octubre 2026

## Lo que produje

- Estrategia de ramas GitFlow (dev, qa, main) con politica de promocion documentada
- 50 pruebas unitarias nuevas con dobles de prueba (AsyncMock de SQLAlchemy + patch)
- Pipeline CI/CD de 5 etapas en GitHub Actions (`ci.yml`)
- Coleccion Postman con 15 requests y aserciones automaticas
- Script PowerShell para analisis SonarQube local
- Script k6 para pruebas de carga con validacion de RNF-01
- Documentacion de evidencias para los entregables E9 al E14

## Dificultades que enfrente

**Linea base de cobertura sin medir en Fase 1.** El entregable E10 exige
+20 pp sobre la cobertura inicial, pero la Fase 1 no la registro. Tuve que
reconstruir la medicion antes de empezar a sumar: correr pytest-cov solo
con las 28 pruebas preexistentes para fijar el 63% base, luego sumar las
50 nuevas y medir el delta. Me tomo unas 2 horas que no habia presupuestado.

**Problema de line endings (CRLF vs LF).** Al clonar en Windows aparecieron
~86 archivos "modificados" sin cambio real, solo por diferencia de fin de
linea. Resolvi con `.gitattributes` + `core.autocrlf=false` y reset. Util
documentarlo para que el equipo no lo arrastre.

**El seed_admin no sobreescribe.** El primer run del pipeline fallaba
porque el admin existia en la BD con otra contrasena. Reset del volumen de
Docker + re-seed. Para el pipeline agregue variables de entorno dummy en
el job de unit tests porque pytest cargaba el conftest global.

## Lo que aprendi

- La diferencia practica entre pruebas unitarias (aislamiento con mocks)
  y pruebas de integracion. Las unitarias son 50x mas rapidas y permiten
  probar codigo que seria dificil de exponer con una peticion HTTP.
- Como disenar un pipeline multi-etapa en GitHub Actions con jobs
  dependientes, service containers, y quality gates. El `needs:` cambia
  todo cuando antes solo habia un workflow lineal.
- El valor de medir una linea base antes de prometer un delta. Sin la base
  no se puede defender el "+20 pp" con numeros.

## Lo que haria diferente

- Medir cobertura desde el dia 1 de Fase 1 con pytest-cov en el pipeline
  original. Habriamos ahorrado tiempo y tendria mas sentido historico.
- Separar las migraciones Alembic del arranque del Procfile. Hoy el
  `alembic upgrade head && uvicorn ...` se ejecuta en cada deploy a EB,
  lo cual es riesgoso para migraciones destructivas. En Fase 3 propondria
  un step previo manual.
- Agregar un ambiente de staging entre `qa` y produccion. Hoy la unica
  validacion antes de prod es el pipeline y una review manual.
