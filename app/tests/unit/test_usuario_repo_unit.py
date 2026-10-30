"""
Pruebas unitarias para app/repositories/usuario.py.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import Rol
from app.models.usuario import Usuario
from app.repositories import usuario as usuario_repo


@pytest.mark.asyncio
async def test_create_usuario_llama_add_commit_refresh():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    user = Usuario(
        nombre="Jair", email="jair@sece.local",
        password_hash="hashed_pass", rol=Rol.ADMIN,
    )
    resultado = await usuario_repo.create(mock_db, user)
    mock_db.add.assert_called_once_with(user)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(user)
    assert resultado is user


@pytest.mark.asyncio
async def test_get_by_email_devuelve_usuario_cuando_existe():
    user = Usuario(
        id="u1", nombre="Test", email="test@sece.local",
        password_hash="h", rol=Rol.MEDICO, activo=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await usuario_repo.get_by_email(mock_db, email="test@sece.local")
    assert resultado is user
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_count_active_admins_devuelve_entero():
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 2
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    resultado = await usuario_repo.count_active_admins(mock_db)
    assert resultado == 2
    assert isinstance(resultado, int)


@pytest.mark.asyncio
async def test_get_by_id_devuelve_usuario_cuando_existe():
    user = Usuario(
        id="u1", nombre="X", email="x@x.com",
        password_hash="h", rol=Rol.MEDICO, activo=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await usuario_repo.get_by_id(mock_db, user_id="u1")
    assert resultado is user


@pytest.mark.asyncio
async def test_list_all_devuelve_lista_ordenada():
    users = [
        Usuario(id="u1", nombre="Ana", email="a@a.com",
                password_hash="h", rol=Rol.ADMIN, activo=True),
        Usuario(id="u2", nombre="Bob", email="b@b.com",
                password_hash="h", rol=Rol.MEDICO, activo=True),
    ]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = users
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    resultado = await usuario_repo.list_all(mock_db)
    assert len(resultado) == 2


@pytest.mark.asyncio
async def test_delete_usuario_llama_db_delete_cuando_existe():
    user = Usuario(
        id="u1", nombre="X", email="x@x.com",
        password_hash="h", rol=Rol.MEDICO, activo=True,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    await usuario_repo.delete(mock_db, user_id="u1")
    mock_db.delete.assert_awaited_once_with(user)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_usuario_llama_commit_y_refresh():
    user = Usuario(
        id="u1", nombre="X", email="x@x.com",
        password_hash="h", rol=Rol.MEDICO, activo=True,
    )
    mock_db = AsyncMock()
    resultado = await usuario_repo.save(mock_db, user)
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(user)
    assert resultado is user
