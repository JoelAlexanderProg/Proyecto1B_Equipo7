"""Pruebas unitarias del código de retiro (RN-NEG-05) y de los datos del cliente (A2)."""

import pytest

from cafeteria.dominio import excepciones as exc
from cafeteria.dominio.codigo_retiro import (
    ALFABETO,
    es_codigo_valido,
    generar_codigo_retiro,
    normalizar_codigo_retiro,
)
from cafeteria.dominio.validaciones import (
    validar_cedula,
    validar_celular,
    validar_correo_institucional,
    validar_nombre_persona,
)


def test_codigo_generado_tiene_formato_y_alfabeto_sin_ambiguos():
    for _ in range(200):
        codigo = generar_codigo_retiro()
        assert es_codigo_valido(codigo)
    assert not set("0O1IL") & set(ALFABETO)


def test_codigos_generados_no_se_repiten_en_una_muestra():
    muestra = {generar_codigo_retiro() for _ in range(2000)}
    assert len(muestra) == 2000


@pytest.mark.parametrize("texto", ["k7p4qx", "K7P 4QX", " k7p-4qx"])
def test_normalizar_codigo(texto):
    assert normalizar_codigo_retiro(texto) == "K7P-4QX"


@pytest.mark.parametrize("cedula", ["1710034065", "0102030400"])
def test_cedula_valida(cedula):
    assert validar_cedula(cedula) == cedula


@pytest.mark.parametrize("cedula", ["1712345678", "171003406", "9910034065", "1790034065", "abc"])
def test_cedula_invalida(cedula):
    with pytest.raises(exc.DatoInvalido):
        validar_cedula(cedula)


def test_celular_valido_se_normaliza():
    assert validar_celular("099 123 4567") == "0991234567"


@pytest.mark.parametrize("celular", ["0891234567", "09912345", "+593991234567"])
def test_celular_invalido(celular):
    with pytest.raises(exc.DatoInvalido):
        validar_celular(celular)


def test_correo_institucional_valido():
    assert validar_correo_institucional(" Ana.Perez@EPN.edu.ec ", "epn.edu.ec") == (
        "ana.perez@epn.edu.ec"
    )


@pytest.mark.parametrize("correo", ["ana@gmail.com", "ana.perez", "@epn.edu.ec", "a b@epn.edu.ec"])
def test_correo_no_institucional_se_rechaza(correo):
    with pytest.raises(exc.DatoInvalido):
        validar_correo_institucional(correo, "epn.edu.ec")


@pytest.mark.parametrize("nombre", ["", "A", "Ana3", "x" * 41])
def test_nombre_invalido(nombre):
    with pytest.raises(exc.DatoInvalido):
        validar_nombre_persona(nombre, "nombre")
