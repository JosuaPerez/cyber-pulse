import pytest

from app import config


def test_dry_run_tiene_default_seguro(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)

    assert config._get_bool("DRY_RUN", True) is True


@pytest.mark.parametrize("valor", ["1", "true", "yes", "on", "TRUE"])
def test_get_bool_acepta_valores_verdaderos(monkeypatch, valor):
    monkeypatch.setenv("TEST_BOOLEAN", valor)

    assert config._get_bool("TEST_BOOLEAN", False) is True


@pytest.mark.parametrize("valor", ["0", "false", "no", "off", "FALSE"])
def test_get_bool_acepta_valores_falsos(monkeypatch, valor):
    monkeypatch.setenv("TEST_BOOLEAN", valor)

    assert config._get_bool("TEST_BOOLEAN", True) is False


def test_get_bool_rechaza_valor_ambiguo(monkeypatch):
    monkeypatch.setenv("TEST_BOOLEAN", "quizas")

    with pytest.raises(RuntimeError, match="debe ser booleana"):
        config._get_bool("TEST_BOOLEAN", True)


def test_publicacion_real_exige_todas_las_credenciales(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", False)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "test-only")
    for nombre in (
        "META_ACCESS_TOKEN",
        "IG_USER_ID",
        "R2_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET_NAME",
        "R2_PUBLIC_BASE_URL",
    ):
        monkeypatch.setattr(config, nombre, None)

    with pytest.raises(RuntimeError, match="DRY_RUN=false"):
        config.validar_config_publicacion()

