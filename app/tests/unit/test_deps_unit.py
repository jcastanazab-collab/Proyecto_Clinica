"""
Pruebas unitarias para app/core/deps.py (dependencias de autenticación).
Usa AsyncMock para aislar la BD y HTTPBearerCredentials.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import deps, security
from app.models.enums import Rol
from app.models.usuario import Usuario


@pytest.mark.asyncio
async def test_get_current_user_con_token_invalido_lanza_401():
    """DOBLE DE PRUEBA: AsyncSession mockeada (nunca se consulta BD)."""
    mock_db = AsyncMock()
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "token-malformado-xyz"

    with pytest.raises(HTTPException) as exc_info:
        await deps.get_current_user(credentials=mock_credentials, db=mock_db)
    assert exc_info.value.status_code == 401
    assert "inv" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_con_usuario_inactivo_lanza_401():
    """DOBLE DE PRUEBA: result.scalar_one_or_none devuelve usuario inactivo."""
    token = security.create_access_token(sub="user-inactive-id", rol="MEDICO")
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = token

    usuario_inactivo = Usuario(
        id="user-inactive-id", nombre="Inactivo",
        email="x@x.com", password_hash="h", rol=Rol.MEDICO, activo=False,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = usuario_inactivo
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await deps.get_current_user(credentials=mock_credentials, db=mock_db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_require_role_rechaza_rol_no_autorizado():
    """require_role(ADMIN) con un usuario RECEPCIONISTA debe lanzar 403."""
    user_recep = Usuario(
        id="u1", nombre="Recep", email="r@r.com",
        password_hash="h", rol=Rol.RECEPCIONISTA, activo=True,
    )
    checker = deps.require_role(Rol.ADMIN)
    with pytest.raises(HTTPException) as exc_info:
        await checker(current_user=user_recep)
    assert exc_info.value.status_code == 403
