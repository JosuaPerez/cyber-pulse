from pathlib import Path
from unittest.mock import Mock, patch

from app import almacenamiento_r2


def _configurar_r2(monkeypatch):
    monkeypatch.setattr(almacenamiento_r2.config, "R2_ENDPOINT_URL", "https://r2.example")
    monkeypatch.setattr(almacenamiento_r2.config, "R2_ACCESS_KEY_ID", "access")
    monkeypatch.setattr(almacenamiento_r2.config, "R2_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr(almacenamiento_r2.config, "R2_BUCKET_NAME", "bucket")
    monkeypatch.setattr(
        almacenamiento_r2.config,
        "R2_PUBLIC_BASE_URL",
        "https://cdn.example/images",
    )


def test_subida_exitosa_devuelve_url_publica(tmp_path, monkeypatch):
    _configurar_r2(monkeypatch)
    imagen = tmp_path / "prueba.jpg"
    imagen.write_bytes(b"imagen")
    cliente = Mock()

    with patch.object(almacenamiento_r2.boto3, "client", return_value=cliente):
        resultado = almacenamiento_r2.subir_imagen_publica(imagen)

    assert resultado.startswith("https://cdn.example/images/")
    assert resultado.endswith(".jpg")
    cliente.upload_file.assert_called_once()


def test_fallo_tras_tres_intentos_devuelve_none(tmp_path, monkeypatch):
    _configurar_r2(monkeypatch)
    imagen = tmp_path / "prueba.png"
    imagen.write_bytes(b"imagen")
    cliente = Mock()
    cliente.upload_file.side_effect = almacenamiento_r2.ClientError(
        {"Error": {"Code": "SlowDown", "Message": "temporary"}}, "PutObject"
    )

    with (
        patch.object(almacenamiento_r2.boto3, "client", return_value=cliente),
        patch.object(
            almacenamiento_r2.time,
            "sleep",
            return_value=None,
        ) as dormir,
    ):
        resultado = almacenamiento_r2.subir_imagen_publica(imagen)

    assert resultado is None
    assert cliente.upload_file.call_count == 3
    assert [llamada.args[0] for llamada in dormir.call_args_list] == [2, 4]


def test_nombre_de_archivo_es_unico_entre_llamadas(tmp_path, monkeypatch):
    _configurar_r2(monkeypatch)
    imagen = tmp_path / "prueba.webp"
    imagen.write_bytes(b"imagen")
    cliente = Mock()

    with patch.object(almacenamiento_r2.boto3, "client", return_value=cliente):
        almacenamiento_r2.subir_imagen_publica(imagen)
        almacenamiento_r2.subir_imagen_publica(imagen)

    primera_clave = cliente.upload_file.call_args_list[0].kwargs["Key"]
    segunda_clave = cliente.upload_file.call_args_list[1].kwargs["Key"]
    assert primera_clave != segunda_clave
    assert Path(primera_clave).suffix == ".webp"
    assert Path(segunda_clave).suffix == ".webp"
