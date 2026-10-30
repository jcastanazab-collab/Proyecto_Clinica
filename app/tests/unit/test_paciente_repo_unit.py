"""
Pruebas unitarias para app/repositories/paciente.py.
Aísla la capa de persistencia con AsyncMock de SQLAlchemy.
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import Sexo
from app.models.paciente import Paciente
from app.repositories import paciente as paciente_repo


def _mock_db_with_scalar(scalar_result):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = scalar_result
    mock_result.scalar_one_or_none.return_value = scalar_result
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db


def _mock_db_with_list(items):
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = items
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db


@pytest.mark.asyncio
async def test_create_paciente_llama_add_commit_refresh():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    paciente = Paciente(
        codigo_expediente="EXP-2026-0001",
        nombre_completo="Juan Pérez",
        dpi="1234567890101",
        fecha_nacimiento=date(1990, 1, 1),
        sexo=Sexo.M,
    )
    resultado = await paciente_repo.create(mock_db, paciente)
    mock_db.add.assert_called_once_with(paciente)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(paciente)
    assert resultado is paciente


@pytest.mark.asyncio
async def test_get_by_dpi_devuelve_paciente_cuando_existe():
    paciente = Paciente(
        id="p1", codigo_expediente="EXP-2026-0001",
        nombre_completo="Juan Pérez", dpi="1234567890101",
        fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M,
    )
    mock_db = _mock_db_with_scalar(scalar_result=paciente)
    resultado = await paciente_repo.get_by_dpi(mock_db, dpi="1234567890101")
    assert resultado is paciente
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_dpi_devuelve_none_cuando_no_existe():
    mock_db = _mock_db_with_scalar(scalar_result=None)
    resultado = await paciente_repo.get_by_dpi(mock_db, dpi="0000000000000")
    assert resultado is None


@pytest.mark.asyncio
async def test_search_por_nombre_devuelve_coincidencias():
    pacientes = [
        Paciente(id="p1", codigo_expediente="EXP-1", nombre_completo="Juan Pérez",
                 dpi="1111111111111", fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M),
        Paciente(id="p2", codigo_expediente="EXP-2", nombre_completo="Juana López",
                 dpi="2222222222222", fecha_nacimiento=date(1992, 2, 2), sexo=Sexo.F),
    ]
    mock_db = _mock_db_with_list(pacientes)
    resultado = await paciente_repo.search(mock_db, q="Juan")
    assert len(resultado) == 2
    assert resultado[0].nombre_completo == "Juan Pérez"


@pytest.mark.asyncio
async def test_get_by_id_devuelve_paciente_cuando_existe():
    paciente = Paciente(
        id="p1", codigo_expediente="EXP-1", nombre_completo="X",
        dpi="1111111111111", fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M,
    )
    mock_db = _mock_db_with_scalar(scalar_result=paciente)
    resultado = await paciente_repo.get_by_id(mock_db, paciente_id="p1")
    assert resultado is paciente


@pytest.mark.asyncio
async def test_get_by_codigo_devuelve_paciente_cuando_existe():
    paciente = Paciente(
        id="p1", codigo_expediente="EXP-2026-0001", nombre_completo="X",
        dpi="1111111111111", fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M,
    )
    mock_db = _mock_db_with_scalar(scalar_result=paciente)
    resultado = await paciente_repo.get_by_codigo(mock_db, codigo="EXP-2026-0001")
    assert resultado.codigo_expediente == "EXP-2026-0001"


@pytest.mark.asyncio
async def test_count_all_devuelve_entero():
    mock_db = _mock_db_with_scalar(scalar_result=42)
    resultado = await paciente_repo.count_all(mock_db)
    assert resultado == 42


@pytest.mark.asyncio
async def test_list_all_devuelve_lista_con_limite():
    paciente = Paciente(
        id="p1", codigo_expediente="E1", nombre_completo="A",
        dpi="1" * 13, fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M,
    )
    mock_db = _mock_db_with_list([paciente])
    resultado = await paciente_repo.list_all(mock_db, limit=50)
    assert len(resultado) == 1
    assert resultado[0].id == "p1"


@pytest.mark.asyncio
async def test_delete_paciente_llama_db_delete_cuando_existe():
    paciente = Paciente(
        id="p1", codigo_expediente="E1", nombre_completo="A",
        dpi="1" * 13, fecha_nacimiento=date(1990, 1, 1), sexo=Sexo.M,
    )
    mock_db = _mock_db_with_scalar(scalar_result=paciente)
    await paciente_repo.delete(mock_db, paciente_id="p1")
    mock_db.delete.assert_awaited_once_with(paciente)
    mock_db.commit.assert_awaited_once()
