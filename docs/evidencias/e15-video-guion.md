# E15 - Guion video YouTube (segmento Jair)

**Duracion objetivo:** 4m30s - 5m00s
**Rol defendido:** Ingeniero de Plataforma / DevOps + Ingeniero de Automatizacion
**Formato:** una sola toma, camara + pantalla compartida

## Setup previo

- OBS Studio con escena: pantalla completa + webcam esquina inferior derecha
- Pestanas abiertas: GitHub repo, GitHub Actions, htmlcov local, SonarQube
- Terminal PowerShell en `C:\Users\YMC3\Proyecto_Clinica`
- Carne a la vista los primeros 20s

## Guion

### [00:00 - 00:25] Identificacion
"Hola, soy Jair Moshed Castanaza Barrera, carne 0900-20-12951, estudiante
plan sabado. En esta Fase 2 me correspondio el rol de Ingeniero de Plataforma
y Automatizacion. Voy a mostrar lo que trabaje para los entregables E9, E10,
E11, E12, E13 y E14."

### [00:25 - 01:10] E9 - Estrategia de ramas
Mostrar GitHub Desktop:
"Primero defini la estrategia GitFlow adaptada: tres ramas - dev para
trabajo diario, qa para pre-produccion y main como production-ready. Las
promociones van siempre por Pull Request con CI verde obligatorio."

Mostrar PRs en GitHub.

### [01:10 - 02:00] E10 - Pruebas unitarias
Terminal:
```
cd $env:USERPROFILE\Proyecto_Clinica
code app\tests\unit\
uv run pytest app/tests/unit/ -v
```

"Agregue 50 pruebas unitarias con dobles de prueba AsyncMock de SQLAlchemy.
Aislan la logica de los repositorios y los servicios core sin tocar la base
de datos. Corren en menos de 2 segundos. Sumadas a las 28 de integracion de
Fase 1 nos da una suite de 78 pruebas que la cobertura total subio de 63% a
69%, y la logica de negocio paso del 69% al 95%."

Mostrar htmlcov en Chrome.

### [02:00 - 03:00] E13 - Pipeline CI/CD
Abrir GitHub Actions:
"Construi un pipeline multi-etapa en GitHub Actions. Cinco etapas: build,
lint con Ruff, pruebas unitarias con el gate de minimo 30, integracion
contra Postgres 16 con quality gate del 60%, y pruebas de API con Newman.
Corre en menos de dos minutos y bloquea el merge si cualquier etapa critica
falla."

Mostrar un run exitoso.

### [03:00 - 03:30] E11 - Postman
Abrir Postman:
"Para la validacion de contratos de API arme una coleccion con 15 requests
que recorren el flujo clinico completo: login, creacion de pacientes,
programacion de cita, consulta y receta con medicamentos. Incluye casos
negativos como DPI duplicado o conflicto de agenda."

### [03:30 - 04:00] E12 - SonarQube
Mostrar dashboard local:
"Para analisis estatico profundo use SonarQube Community localmente. Partio
con 1 Critical y 7 Majors, remedi los Blocker y Critical, el quality gate
quedo verde cumpliendo RNF-09."

### [04:00 - 04:30] E14 - Pruebas de carga
Terminal:
"Las pruebas de carga con k6 - 50 usuarios virtuales durante 5 minutos
contra dos endpoints criticos. El threshold valida que el percentil 95 este
por debajo de 3 segundos. Esto demuestra RNF-01."

### [04:30 - 05:00] Cierre
"En resumen: 78 pruebas automatizadas, pipeline CI/CD completo con 5
etapas, cobertura al 69% con 20+ puntos porcentuales de incremento en
modulos criticos, y validacion de RNF-01 y RNF-09. Gracias."

## Checklist tecnico pre-grabacion

- [ ] Cerrar notificaciones de Windows
- [ ] Fuente de VSCode a 16pt minimo
- [ ] Tamano de ventana consistente
- [ ] Ensayo cronometrado completo
- [ ] Audio probado (ruido ambiente)
- [ ] Carne visible primeros 15s
