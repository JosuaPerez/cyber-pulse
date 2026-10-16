import pytest

from app.publicador_x import indices_imagenes_hilo


@pytest.mark.parametrize("count,expected", [(4, [[0], [1, 2], [3]]), (5, [[0], [1, 2], [3, 4]])])
def test_hilo_preserva_relacion_entre_texto_e_imagenes(count, expected):
    assert indices_imagenes_hilo(count) == expected
    assert sorted(i for group in expected for i in group) == list(range(count))


@pytest.mark.parametrize("count", [0, 1, 2, 3, 6])
def test_hilo_rechaza_carrusel_incompleto(count):
    with pytest.raises(ValueError):
        indices_imagenes_hilo(count)
