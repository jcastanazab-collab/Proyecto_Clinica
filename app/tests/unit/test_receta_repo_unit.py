"""
Pruebas unitarias para app/repositories/receta.py.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.medicamento_receta import MedicamentoReceta
from app.models.receta import Receta
from app.repositories import receta as receta_repo


@pytest.mark.asyncio
async def test_get_by_id_devuelve_receta_con_medicamentos():
    receta = Receta(id="r1", consulta_id="co1")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = receta
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await receta_repo.get_by_id(mock_db, receta_id="r1")
    assert resultado is receta


@pytest.mark.asyncio
async def test_get_by_id_devuelve_none_cuando_no_existe():
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await receta_repo.get_by_id(mock_db, receta_id="r-inexistente")
    assert resultado is None


@pytest.mark.asyncio
async def test_create_receta_persiste_medicamentos_asociados():
    """create debe hacer add+flush de la receta y luego add de cada medicamento."""
    receta = Receta(id="r-nueva", consulta_id="co1")
    medicamentos = [
        MedicamentoReceta(nombre="Paracetamol", dosis="500mg", via="oral",
                          frecuencia="c/8h", duracion="5 días"),
        MedicamentoReceta(nombre="Ibuprofeno", dosis="400mg", via="oral",
                          frecuencia="c/12h", duracion="3 días"),
    ]
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    # Mockear get_by_id interno que se llama al final
    with patch.object(receta_repo, "get_by_id", AsyncMock(return_value=receta)):
        resultado = await receta_repo.create(mock_db, receta, medicamentos)

    # add llamado 3 veces: 1 receta + 2 medicamentos
    assert mock_db.add.call_count == 3
    mock_db.flush.assert_awaited_once()
    mock_db.commit.assert_awaited_once()
    assert resultado is receta
    # Cada medicamento recibe el receta_id
    for med in medicamentos:
        assert med.receta_id == "r-nueva"
