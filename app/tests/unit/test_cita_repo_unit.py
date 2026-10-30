"""
Pruebas unitarias para app/repositories/cita.py.
Usa AsyncMock para aislar la BD. Verifica contratos de ensamblado
y transiciones sin tocar PostgreSQL.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.cita import Cita
from app.models.enums import EstadoCita
from app.repositories import cita as cita_repo


def _mock_db_with_scalar(scalar_result):
    """Helper: crea AsyncSession mock cuyo execute devuelve scalar()."""
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = scalar_result
    mock_result.scalar_one_or_none.return_value = scalar_result
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db, mock_result


@pytest.mark.asyncio
async def test_create_cita_persiste_entidad():
    """DOBLE DE PRUEBA: verifica que create llama add, commit y refresh."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    cita = Cita(
        paciente_id="p1", medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
        estado=EstadoCita.PROGRAMADA,
    )
    resultado = await cita_repo.create(mock_db, cita)

    mock_db.add.assert_called_once_with(cita)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(cita)
    assert resultado is cita


@pytest.mark.asyncio
async def test_existe_conflicto_true_cuando_hay_cita_programada():
    mock_db, _ = _mock_db_with_scalar(scalar_result=1)
    resultado = await cita_repo.existe_conflicto(
        mock_db, medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
    )
    assert resultado is True
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_existe_conflicto_false_cuando_no_hay_cita():
    mock_db, _ = _mock_db_with_scalar(scalar_result=0)
    resultado = await cita_repo.existe_conflicto(
        mock_db, medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
    )
    assert resultado is False


@pytest.mark.asyncio
async def test_existe_conflicto_con_exclude_id_filtra_cita_dada():
    """Al pasar exclude_id, la query excluye esa cita del conteo (reprogramar)."""
    mock_db, _ = _mock_db_with_scalar(scalar_result=0)
    resultado = await cita_repo.existe_conflicto(
        mock_db, medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
        exclude_id="cita-reprog-id",
    )
    assert resultado is False
    assert mock_db.execute.await_count == 1


@pytest.mark.asyncio
async def test_count_by_medico_devuelve_entero():
    mock_db, _ = _mock_db_with_scalar(scalar_result=7)
    resultado = await cita_repo.count_by_medico(mock_db, medico_id="m-7")
    assert resultado == 7
    assert isinstance(resultado, int)


@pytest.mark.asyncio
async def test_delete_cita_llama_db_delete_cuando_existe():
    cita_existente = Cita(
        id="c1", paciente_id="p1", medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
    )
    mock_db, _ = _mock_db_with_scalar(scalar_result=cita_existente)

    await cita_repo.delete(mock_db, cita_id="c1")

    mock_db.delete.assert_awaited_once_with(cita_existente)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_by_fecha_devuelve_lista_ordenada():
    """DOBLE DE PRUEBA: scalars().all() devuelve citas del día."""
    from datetime import date
    cita1 = Cita(
        id="c1", paciente_id="p1", medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 8, 0, tzinfo=timezone.utc),
    )
    cita2 = Cita(
        id="c2", paciente_id="p2", medico_id="m2",
        fecha_hora=datetime(2026, 11, 1, 14, 0, tzinfo=timezone.utc),
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [cita1, cita2]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await cita_repo.list_by_fecha(mock_db, fecha=date(2026, 11, 1))
    assert len(resultado) == 2
    assert resultado[0] is cita1


@pytest.mark.asyncio
async def test_list_all_devuelve_todas_las_citas():
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await cita_repo.list_all(mock_db)
    assert resultado == []
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_cita_llama_commit_y_refresh():
    cita = Cita(
        id="c1", paciente_id="p1", medico_id="m1",
        fecha_hora=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
    )
    mock_db = AsyncMock()
    resultado = await cita_repo.save(mock_db, cita)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(cita)
    assert resultado is cita
