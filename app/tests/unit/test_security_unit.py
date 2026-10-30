"""
Pruebas unitarias para app/core/security.py
Funciones puras (hash_password, verify_password, create_access_token, decode_token).
Sin dobles de prueba porque son determinísticas y sin dependencias externas.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core import security
from app.core.config import settings


class TestHashPassword:
    """Pruebas unitarias para hash_password."""

    def test_hash_devuelve_string_no_vacio(self):
        resultado = security.hash_password("MiPass123!")
        assert isinstance(resultado, str)
        assert len(resultado) > 20

    def test_hash_del_mismo_password_es_diferente(self):
        """bcrypt genera salt aleatorio por hash."""
        h1 = security.hash_password("MismaPass")
        h2 = security.hash_password("MismaPass")
        assert h1 != h2


class TestVerifyPassword:
    """Pruebas unitarias para verify_password."""

    def test_verify_password_correcto_devuelve_true(self):
        plain = "ClavePrueba2026"
        hashed = security.hash_password(plain)
        assert security.verify_password(plain, hashed) is True

    def test_verify_password_incorrecto_devuelve_false(self):
        hashed = security.hash_password("ClaveReal")
        assert security.verify_password("ClaveFalsa", hashed) is False


class TestCreateAccessToken:
    """Pruebas unitarias para create_access_token."""

    def test_token_contiene_sub_y_rol(self):
        token = security.create_access_token(sub="user-123", rol="ADMIN")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        assert payload["sub"] == "user-123"
        assert payload["rol"] == "ADMIN"

    def test_token_incluye_expiracion_futura(self):
        token = security.create_access_token(sub="x", rol="MEDICO")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        ahora = datetime.now(timezone.utc)
        assert exp_dt > ahora
        assert exp_dt < ahora + timedelta(minutes=settings.JWT_EXPIRE_MINUTES + 1)


class TestDecodeToken:
    """Pruebas unitarias para decode_token."""

    def test_decode_token_valido_devuelve_payload(self):
        token = security.create_access_token(sub="abc", rol="RECEPCIONISTA")
        payload = security.decode_token(token)
        assert payload["sub"] == "abc"
        assert payload["rol"] == "RECEPCIONISTA"

    def test_decode_token_invalido_devuelve_dict_vacio(self):
        """Un token malformado no debe lanzar excepción, debe devolver {}."""
        resultado = security.decode_token("esto-no-es-un-jwt")
        assert resultado == {}
