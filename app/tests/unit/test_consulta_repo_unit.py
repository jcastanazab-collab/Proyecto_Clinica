"""
Pruebas unitarias para app/repositories/consulta.py.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.consulta import Consulta
from app.repositories import consulta as consulta_repo


@pytest.mark.asyncio
async def test_create_consulta_llama_add_commit_refresh():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    consulta = Consulta(
        cita_id="cita-1",
        diagnostico="Faringitis aguda",
        notas_clinicas="Garganta inflamada",
        plan_tratamiento="Reposo + ibuprofeno",
    )
    resultado = await consulta_repo.create(mock_db, consulta)
    mock_db.add.assert_called_once_with(consulta)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(consulta)
    assert resultado is consulta


@pytest.mark.asyncio
async def test_get_by_cita_id_devuelve_consulta_cuando_existe():
    consulta = Consulta(
        id="co1", cita_id="cita-1",
        diagnostico="Dx test", notas_clinicas=None, plan_tratamiento=None,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = consulta
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await consulta_repo.get_by_cita_id(mock_db, cita_id="cita-1")
    assert resultado is consulta
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_cita_id_devuelve_none_cuando_no_hay_consulta():
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await consulta_repo.get_by_cita_id(mock_db, cita_id="cita-sin-consulta")
    assert resultado is None


@pytest.mark.asyncio
async def test_get_by_id_devuelve_consulta_cuando_existe():
    consulta = Consulta(
        id="co1", cita_id="cita-1", diagnostico="Dx",
        notas_clinicas=None, plan_tratamiento=None,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = consulta
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await consulta_repo.get_by_id(mock_db, consulta_id="co1")
    assert resultado is consulta


@pytest.mark.asyncio
async def test_save_consulta_llama_commit_y_refresh():
    consulta = Consulta(
        id="co1", cita_id="cita-1", diagnostico="Dx",
        notas_clinicas=None, plan_tratamiento=None,
    )
    mock_db = AsyncMock()
    resultado = await consulta_repo.save(mock_db, consulta)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(consulta)
    assert resultado is consulta
