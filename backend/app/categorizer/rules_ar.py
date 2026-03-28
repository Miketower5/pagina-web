"""
Reglas de categorización de gastos para el mercado argentino.

Cada entrada mapea una categoría a una lista de palabras clave / patrones
que se usan para clasificar transacciones automáticamente.
"""

CATEGORIAS_AR: dict[str, dict] = {
    "supermercados": {
        "keywords": [
            "carrefour", "coto", "disco", "jumbo", "la anonima",
            "dia", "vea", "changomas", "walmart", "makro",
        ],
        "subcategorias": ["frescos", "congelados", "limpieza", "bebidas"],
    },
    "combustible": {
        "keywords": ["ypf", "shell", "axion", "puma", "nafta", "gasoil"],
        "subcategorias": ["nafta", "gasoil", "gnc"],
    },
    "servicios_publicos": {
        "keywords": [
            "edenor", "edesur", "metrogas", "aysa", "telecom",
            "personal", "claro", "movistar", "fibertel", "cablevision",
        ],
        "subcategorias": ["electricidad", "gas", "agua", "internet", "telefonia"],
    },
    "salud": {
        "keywords": [
            "osde", "swiss medical", "medicus", "farmacity",
            "farmacia", "clinica", "hospital", "laboratorio",
        ],
        "subcategorias": ["medicamentos", "consultas", "prepaga"],
    },
    "restaurantes": {
        "keywords": [
            "pedidos ya", "rappi", "uberéats", "mcdonalds", "burger",
            "resto", "pizzeria", "sushi",
        ],
        "subcategorias": ["delivery", "comida_rapida", "restaurante_formal"],
    },
    "transporte": {
        "keywords": ["sube", "cabify", "uber", "peaje", "autoexpreso"],
        "subcategorias": ["colectivo", "subte", "taxi", "peaje"],
    },
    "indumentaria": {
        "keywords": ["zara", "h&m", "falabella", "paris", "zara", "adidas", "nike"],
        "subcategorias": ["ropa", "calzado", "accesorios"],
    },
    "entretenimiento": {
        "keywords": ["netflix", "spotify", "disney", "hbo", "amazon prime", "flow"],
        "subcategorias": ["streaming", "cine", "eventos"],
    },
    "educacion": {
        "keywords": ["uba", "utn", "conicet", "udemy", "coursera", "colegio"],
        "subcategorias": ["cuotas", "libros", "cursos"],
    },
    "impuestos": {
        "keywords": ["afip", "arba", "abl", "ingresos brutos", "monotributo"],
        "subcategorias": ["nacional", "provincial", "municipal"],
    },
    "mercado_pago": {
        "keywords": ["mercado pago", "mp", "mercadopago"],
        "subcategorias": ["transferencia", "pago_qr", "tarjeta_mp"],
    },
    "otros": {
        "keywords": [],
        "subcategorias": [],
    },
}


def categorizar(descripcion: str) -> tuple[str, str | None]:
    """
    Retorna (categoria, subcategoria) basándose en la descripción de la transacción.
    Fallback a 'otros' si no hay coincidencia.
    """
    desc_lower = descripcion.lower()
    for categoria, config in CATEGORIAS_AR.items():
        for keyword in config["keywords"]:
            if keyword in desc_lower:
                return categoria, None
    return "otros", None
