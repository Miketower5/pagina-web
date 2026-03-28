from app.categorizer.rules_ar import categorizar


def test_categoriza_supermercado():
    categoria, _ = categorizar("Compra en Carrefour Palermo")
    assert categoria == "supermercados"


def test_categoriza_combustible():
    categoria, _ = categorizar("YPF San Martin")
    assert categoria == "combustible"


def test_categoriza_mp():
    categoria, _ = categorizar("Transferencia Mercado Pago")
    assert categoria == "mercado_pago"


def test_fallback_otros():
    categoria, _ = categorizar("Pago sin descripción conocida")
    assert categoria == "otros"
