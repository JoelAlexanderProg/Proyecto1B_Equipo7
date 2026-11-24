"""Pruebas unitarias de la configuración por variables de entorno."""

import os

import pytest

from cafeteria.config import Configuracion, ConfiguracionInvalida, cargar_archivo_env


def test_clave_del_personal_es_obligatoria():
    with pytest.raises(ConfiguracionInvalida):
        Configuracion.desde_entorno({})
    with pytest.raises(ConfiguracionInvalida):
        Configuracion.desde_entorno({"CAFETERIA_CLAVE_PERSONAL": "corta"})


def test_valores_por_defecto_y_personalizados():
    config = Configuracion.desde_entorno(
        {"CAFETERIA_CLAVE_PERSONAL": "una-clave-larga", "CAFETERIA_CARGAR_SEMILLA": "0"}
    )
    assert config.usuario_personal == "personal"
    assert config.dominio_correo == "epn.edu.ec"
    assert config.cargar_semilla is False
    assert len(config.secreto_sesion) >= 32


def test_cargar_archivo_env_no_sobrescribe(tmp_path, monkeypatch):
    archivo = tmp_path / ".env"
    archivo.write_text(
        "# comentario\nCAFETERIA_PRUEBA_A=desde-archivo\nCAFETERIA_PRUEBA_B='con comillas'\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CAFETERIA_PRUEBA_A", "ya-definida")
    monkeypatch.delenv("CAFETERIA_PRUEBA_B", raising=False)
    cargar_archivo_env(archivo)
    assert os.environ["CAFETERIA_PRUEBA_A"] == "ya-definida"
    assert os.environ["CAFETERIA_PRUEBA_B"] == "con comillas"
    monkeypatch.delenv("CAFETERIA_PRUEBA_B")
