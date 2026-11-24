"""Fixtures de las pruebas de sistema: la aplicación completa sobre una base temporal."""

import pytest
from fastapi.testclient import TestClient

from cafeteria.config import Configuracion
from cafeteria.presentacion.web import crear_app

CLAVE_PERSONAL = "clave-de-prueba"

DATOS_ANA = {
    "nombre": "Ana",
    "apellido": "Pérez",
    "cedula": "1710034065",
    "celular": "0991234567",
    "correo": "ana.perez@epn.edu.ec",
}
DATOS_LUIS = {
    "nombre": "Luis",
    "apellido": "Cruz",
    "cedula": "0102030400",
    "celular": "0987654321",
    "correo": "luis.cruz@epn.edu.ec",
}


@pytest.fixture
def app(tmp_path):
    config = Configuracion(
        ruta_bd=tmp_path / "web.db",
        usuario_personal="personal",
        clave_personal=CLAVE_PERSONAL,
        secreto_sesion="secreto-de-pruebas-" * 3,
    )
    return crear_app(config)


@pytest.fixture
def navegador(app):
    """Cliente HTTP con su propia cookie de sesión, como un navegador."""
    return TestClient(app)


@pytest.fixture
def otro_navegador(app):
    return TestClient(app)


@pytest.fixture
def servicios(app):
    return app.state.servicios


def registrar(navegador, datos=None):
    return navegador.post("/registro", data=datos or DATOS_ANA)


def pedir(navegador, cantidades):
    """Revisa y confirma un pedido; devuelve la respuesta final."""
    datos = {f"cant-{codigo}": str(cantidad) for codigo, cantidad in cantidades.items()}
    revision = navegador.post("/pedido/revisar", data=datos)
    assert revision.status_code == 200, revision.text
    total = revision.text.split('name="total_revisado" value="')[1].split('"')[0]
    return navegador.post("/pedido/confirmar", data={"total_revisado": total})
