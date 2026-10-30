"""
Pruebas unitarias para app/repositories/medico.py.
Aísla la capa de persistencia con AsyncMock.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.medico import Medico
from app.repositories import medico as medico_repo


@pytest.mark.asyncio
async def test_create_medico_llama_add_commit_refresh():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    medico = Medico(
        usuario_id="u1", especialidad="Pediatría", num_colegiado="COL-001", activo=True,
    )
    resultado = await medico_repo.create(mock_db, medico)
    mock_db.add.assert_called_once_with(medico)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(medico)
    assert resultado is medico


@pytest.mark.asyncio
async def test_get_by_colegiado_devuelve_medico_cuando_existe():
    medico = Medico(
        id="m1", usuario_id="u1", especialidad="General",
        num_colegiado="COL-123", activo=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = medico
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await medico_repo.get_by_colegiado(mock_db, num_colegiado="COL-123")
    assert resultado is medico


@pytest.mark.asyncio
async def test_list_active_devuelve_solo_medicos_activos():
    medico_activo = Medico(
        id="m1", usuario_id="u1", especialidad="General",
        num_colegiado="COL-A", activo=True,
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [medico_activo]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await medico_repo.list_active(mock_db)
    assert len(resultado) == 1
    assert resultado[0].activo is True


@pytest.mark.asyncio
async def test_get_by_usuario_id_devuelve_medico():
    medico = Medico(
        id="m1", usuario_id="u1", especialidad="Cardiología",
        num_colegiado="COL-C", activo=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = medico
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await medico_repo.get_by_usuario_id(mock_db, usuario_id="u1")
    assert resultado.especialidad == "Cardiología"
