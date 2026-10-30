"""
Pruebas unitarias para app/repositories/signos_vitales.py.
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.signos_vitales import SignosVitales
from app.repositories import signos_vitales as sv_repo


@pytest.mark.asyncio
async def test_create_signos_llama_add_commit_refresh():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    signos = SignosVitales(
        consulta_id="co1",
        presion_arterial="120/80",
        temperatura=Decimal("36.5"),
        frecuencia_cardiaca=72,
        peso=Decimal("70.5"),
        talla=Decimal("1.75"),
        imc=Decimal("23.0"),
    )
    resultado = await sv_repo.create(mock_db, signos)
    mock_db.add.assert_called_once_with(signos)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(signos)
    assert resultado is signos


@pytest.mark.asyncio
async def test_get_by_consulta_id_devuelve_signos():
    signos = SignosVitales(
        id="sv1", consulta_id="co1", presion_arterial="110/70",
        temperatura=Decimal("36.8"), frecuencia_cardiaca=68,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = signos
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await sv_repo.get_by_consulta_id(mock_db, consulta_id="co1")
    assert resultado is signos
    assert resultado.frecuencia_cardiaca == 68
