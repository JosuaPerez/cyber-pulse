import json

import pytest

from app.editorial_alertas import EditorialAlerta, errores_editoriales, visual_editorial, fragmentos_fuente, resolver_editorial
from app.generador import construir_alerta_clara
from test_analizador import analisis_valido, TEXTO_FUENTE, ClienteFalso, NOTICIA
from app import analizador


@pytest.mark.parametrize("periodo", ["historica", "vigencia_no_confirmada"])
def test_caption_libre_no_contradice_temporalidad(periodo):
    e = ficha(temporalidad=periodo, caption="La campaña está siendo utilizada ahora para infectarte. ¿Estás listo?")
    normalizado, ajustes = resolver_editorial(e, {})
    assert "está siendo" not in normalizado.caption
    assert "actual" in normalizado.caption and "confirmada" in normalizado.caption
    assert normalizado.hecho in normalizado.caption
    assert normalizado.limite in normalizado.caption
    assert ajustes


@pytest.mark.parametrize("cita,admitida", [
    ('The company embedded JavaScript in ads to profile devices.', False),
    ('Researchers recommend using a trusted ad-blocking extension.', True),
    ('Researchers do not recommend using an ad-blocking extension.', False),
    ('Researchers recommend installing updates to affected devices.', False),
    ('Researchers recommend installing updates. The attack bypasses ad-blocking extensions.', False),
])
def test_cita_de_ataque_negada_o_control_distinto_no_respalda_medida(cita, admitida):
    e = ficha()
    e.acciones[0].texto = "Instala un bloqueador de anuncios confiable."
    e.acciones[0].orientacion_general = False
    e.acciones[0].evidencia = cita
    errores = errores_editoriales(e, TEXTO_FUENTE + ' ' + cita)
    assert (not any('mismo control' in error for error in errores)) == admitida


def test_historico_rechaza_hecho_redactado_como_actividad_actual():
    e = ficha(temporalidad="historica", evidencia_temporal="Attacks occurred in 2024.",
              hecho="La campaña está siendo utilizada para atacar dispositivos.")
    assert any("actividad actual" in error for error in errores_editoriales(e, TEXTO_FUENTE + " Attacks occurred in 2024."))


def test_analizador_reintenta_medida_con_cita_que_solo_describe_ataque(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    cita = "The company embedded JavaScript in ads to profile devices."
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda n: TEXTO_FUENTE + ' ' + cita)
    malo = json.loads(analisis_valido())
    malo["editorial"]["acciones"][0].update(
        texto="Instala un bloqueador de anuncios confiable.", orientacion_general=False, evidencia=cita)
    cliente = ClienteFalso([json.dumps(malo), analisis_valido()])
    resultado = analizador.analizar_noticia(cliente, NOTICIA)
    assert "mismo control" in cliente.llamadas[1]
    assert resultado["meta"]["editorial"]["acciones"][0]["orientacion_general"]
    assert "vigencia actual no está confirmada" in resultado["caption"]


def test_revisa_no_permite_ocultar_control_operativo_como_orientacion_general():
    e = ficha()
    e.acciones[1].texto = "Revisa el tráfico hacia dominios de publicidad sospechosos."
    normalizado, ajustes = resolver_editorial(e, {})
    assert "tráfico" not in normalizado.acciones[1].texto
    assert normalizado.acciones[1].texto.startswith("Consulta el aviso")
    assert ajustes


def test_riesgo_operativo_necesita_medida_respaldada_sin_rellenar_consultas():
    e = ficha(tipo_noticia="riesgo_operativo")
    assert any("medida concreta" in error for error in errores_editoriales(e, TEXTO_FUENTE))
    cita = "Organizations should review their acceptable use policy."
    e.acciones = [e.acciones[0]]
    e.acciones[0].texto = "Revisa la política de uso de IA con tu equipo."
    e.acciones[0].orientacion_general = False
    e.acciones[0].evidencia = cita
    normalizado, _ = resolver_editorial(e, {})
    assert len(normalizado.acciones) == 1
    assert not errores_editoriales(normalizado, TEXTO_FUENTE + ' ' + cita)
    assert "campaña" not in normalizado.caption
    assert "Riesgo de uso y política" in normalizado.caption


def test_consultas_del_mismo_rol_se_agrupan_y_no_mencionan_indicadores():
    e = ficha()
    e.acciones.append(e.acciones[1].model_copy(update={"texto": "Revisa los logs de acceso."}))
    normalizado, _ = resolver_editorial(e, {})
    assert len(normalizado.acciones) == 2
    assert all("indicadores" not in a.texto for a in normalizado.acciones)


@pytest.mark.parametrize("aviso", ["The case is hypothetical.", "Sponsored and written by Vendor."])
def test_escenarios_y_promociones_no_se_convierten_en_alerta_real(monkeypatch, aviso):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda n: TEXTO_FUENTE + aviso)
    cliente = ClienteFalso([])
    with pytest.raises(analizador.ErrorAnalisis, match="Revisión editorial requerida"):
        analizador.analizar_noticia(cliente, NOTICIA)
    assert cliente.llamadas == []


def test_clasificacion_explicita_obligatoria_para_analisis_nuevo(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda n: TEXTO_FUENTE)
    monkeypatch.setattr(analizador.time, "sleep", lambda s: None)
    incompleto = json.loads(analisis_valido())
    del incompleto["editorial"]["tipo_noticia"]
    cliente = ClienteFalso([json.dumps(incompleto), analisis_valido()])
    analizador.analizar_noticia(cliente, NOTICIA)
    assert "tipo_noticia es obligatorio" in cliente.llamadas[1]


def ficha(**cambios):
    data = json.loads(analisis_valido())["editorial"]
    data.update(cambios)
    return EditorialAlerta.model_validate(data)


def test_cualquier_noticia_tiene_visual_neutral_sin_inventar_cadena():
    for tema in ["VPN", "anuncios", "brecha", "ransomware", "actualización", "incidente desconocido"]:
        e = ficha(gancho=f"Aviso sobre {tema}", visual="cadena", nodos=[], evidencia_relacion="")
        assert visual_editorial(e, TEXTO_FUENTE) == {"tipo": "editorial", "clase": "resumen", "nodos": []}


def test_diagrama_exige_evidencia_de_nodos_y_relacion():
    source = "Targeted ads select devices before delivering spyware."
    e = ficha(visual="cadena", nodos=[{"texto": "Anuncio dirigido", "evidencia": source},
                                    {"texto": "Selección de objetivo", "evidencia": source}], evidencia_relacion=source)
    assert visual_editorial(e, source)["clase"] == "cadena"
    assert visual_editorial(e, "Unrelated research")["clase"] == "resumen"


@pytest.mark.parametrize("campo,texto", [("detalle", "SHA-256: " + "a" * 64), ("detalle", "Busca IOC en tus logs"),
                                       ("resumen", "Conecta con mtrtb[.]com"), ("detalle", "Ad server -> Screening -> C2")])
def test_jerga_e_indicadores_no_van_al_carrusel(campo, texto):
    assert errores_editoriales(ficha(**{campo: texto}), TEXTO_FUENTE)


def test_historico_no_se_acepta_sin_cita_temporal():
    assert any("histórico" in error for error in errores_editoriales(ficha(temporalidad="historica"), TEXTO_FUENTE))
    e = ficha(temporalidad="historica", evidencia_temporal="Attacks occurred in 2024 and 2025.")
    assert not errores_editoriales(e, TEXTO_FUENTE + " Attacks occurred in 2024 and 2025.")


def test_accion_especifica_exige_evidencia_y_personas_tienen_accion():
    e = ficha()
    e.acciones[0].orientacion_general = False
    assert any("medida específica" in error for error in errores_editoriales(e, TEXTO_FUENTE))
    for accion in e.acciones:
        accion.rol = "administradores"
    assert any("personas" in error for error in errores_editoriales(e, TEXTO_FUENTE))


def test_contrato_obligatorio_reintenta_sin_publicar(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda n: TEXTO_FUENTE)
    cliente = ClienteFalso([analisis_valido(editorial=None), analisis_valido()])
    data = analizador.analizar_noticia(cliente, NOTICIA)
    assert "Falta editorial" in cliente.llamadas[1]
    slides = construir_alerta_clara(data)
    assert slides[0]["title"] == data["meta"]["editorial"]["gancho"]
    assert slides[2]["description"] == data["meta"]["editorial"]["detalle"]
    assert "Para ti:" in slides[3]["summary"]
    assert data["slide_3"]["description"].startswith("CVE-")  # referencia íntegra conservada


def test_ids_se_resuelven_contra_la_fuente_y_desconocidos_se_rechazan():
    fragmentos = fragmentos_fuente(TEXTO_FUENTE)
    e, ajustes = resolver_editorial(ficha(evidencias=["FUENTE_001"]), fragmentos)
    assert e.evidencias == [fragmentos["FUENTE_001"]]
    assert not errores_editoriales(e, TEXTO_FUENTE)
    assert any("Caption reconstruido" in ajuste for ajuste in ajustes)
    e, _ = resolver_editorial(ficha(evidencias=["FUENTE_999"]), fragmentos)
    assert errores_editoriales(e, TEXTO_FUENTE)


def test_normalizacion_no_convierte_control_sin_fuente_en_medida_respaldada():
    e = ficha()
    e.acciones[0].texto = "Instala una herramienta desconocida"
    normalizado, ajustes = resolver_editorial(e, fragmentos_fuente(TEXTO_FUENTE))
    assert normalizado.acciones[0].texto.startswith("Consulta")
    assert ajustes
    e.acciones[0].orientacion_general = False
    normalizado, ajustes = resolver_editorial(e, {})
    assert normalizado.acciones[0].texto.startswith("Instala")
    assert errores_editoriales(normalizado, TEXTO_FUENTE)  # no se aprueba como específica


def test_indicadores_y_tareas_de_registros_se_remiten_sin_recortarlos():
    e = ficha(detalle="SHA-256: " + "a" * 64)
    e.acciones[0].texto = "Monitorea logs buscando Ad server -> Screening -> C2"
    e.acciones[0].orientacion_general = False
    normalizado, ajustes = resolver_editorial(e, {})
    assert normalizado.detalle == normalizado.resumen
    assert "logs" not in normalizado.acciones[0].texto
    assert normalizado.acciones[0].texto.startswith("Consulta")
    assert normalizado.acciones[0].orientacion_general
    assert ajustes
    assert not errores_editoriales(normalizado, TEXTO_FUENTE)


def test_normalizacion_no_trunca_un_texto_que_supera_limites():
    e = ficha(detalle="logs " * 35)
    with pytest.raises(ValueError):
        resolver_editorial(e, {})


def test_acciones_solo_admin_reciben_orientacion_personal_sin_inventar_medidas():
    e = ficha()
    for accion in e.acciones:
        accion.rol = "administradores"
    normalizado, ajustes = resolver_editorial(e, {})
    assert normalizado.acciones[0].rol == "personas"
    assert normalizado.acciones[0].orientacion_general
    assert len(normalizado.acciones) <= 3
    assert not errores_editoriales(normalizado, TEXTO_FUENTE)
    assert ajustes


@pytest.mark.parametrize("sin_autenticacion,esperada", [(True, "critical"), (False, "high")])
def test_prioridad_critica_sin_actividad_requiere_respaldo(monkeypatch, sin_autenticacion, esperada):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    source = TEXTO_FUENTE if sin_autenticacion else TEXTO_FUENTE.replace("unauthenticated", "authenticated")
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda n: source)
    cliente = ClienteFalso([analisis_valido(estado_explotacion="desconocido")])
    assert analizador.analizar_noticia(cliente, NOTICIA)["meta"]["severidad"] == esperada
