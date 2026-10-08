"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime
from typing import Any

# ---------------------------------------------------------------
# Reglas de precios: descuentos por volumen, extra VIP e IVA
# ---------------------------------------------------------------
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_EXTRA_VIP = 0.02
TASA_IVA = 0.16

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""


def reiniciar_sistema() -> None:
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo: str | None, nombre: str, precio: float, stock: int) -> bool:
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    producto = {}
    producto["codigo"] = codigo
    producto["nombre"] = nombre
    producto["precio"] = precio
    producto["stock"] = stock
    INVENTARIO[codigo] = producto
    return True


def eliminar_producto(codigo: str) -> bool:
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo: str, cantidad: int) -> bool:
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    nuevo_stock = INVENTARIO[codigo]["stock"] + cantidad
    if nuevo_stock < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = nuevo_stock
    return True


def buscarProducto(texto: str) -> list[dict[str, Any]]:
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    resultados = []
    for codigo in INVENTARIO:
        if texto.lower() in INVENTARIO[codigo]["nombre"].lower():
            resultados.append(INVENTARIO[codigo])
    return resultados


def _calcular_descuento_volumen(subtotal: float) -> float:
    """Descuento por volumen de compra segun el subtotal."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _es_cliente_vip(cliente: str | None) -> bool:
    """Los clientes cuyo codigo empieza con VIP tienen un descuento extra."""
    return bool(cliente) and cliente.startswith(PREFIJO_VIP)


def _calcular_montos(
    subtotal: float, cliente: str | None = None, aplica_vip: bool = False
) -> tuple[float, float, float]:
    """Calcula (descuento, base, impuesto) sin redondear.

    El extra VIP solo se suma si aplica_vip es True y la compra, ya con
    el descuento por volumen, pasa de MONTO_MINIMO_VIP.
    """
    descuento = _calcular_descuento_volumen(subtotal)
    if (
        aplica_vip
        and _es_cliente_vip(cliente)
        and subtotal - descuento > MONTO_MINIMO_VIP
    ):
        descuento = descuento + subtotal * TASA_EXTRA_VIP
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    return descuento, base, impuesto


def registrar_venta(
    codigo: str | None, cantidad: int | None, cliente: str | None = ""
) -> dict[str, Any] | None:
    """Registra una venta completa.

    Esta funcion hace de todo: valida los datos, calcula descuentos e
    impuestos, descuenta el stock, genera el folio, arma el ticket en
    texto y guarda el registro en la lista de ventas. Si algo falla
    regresa None y deja el motivo en ultimo_error.
    """
    global contador_ventas, ultimo_error
    producto = None
    if codigo is not None and codigo != "":
        if codigo in INVENTARIO:
            if cantidad is not None and cantidad > 0:
                if INVENTARIO[codigo]["stock"] >= cantidad:
                    producto = INVENTARIO[codigo]
                else:
                    ultimo_error = "stock insuficiente"
                    return None
            else:
                ultimo_error = "cantidad invalida"
                return None
        else:
            ultimo_error = "producto no existe"
            return None
    else:
        ultimo_error = "codigo vacio"
        return None
    # calculo del subtotal
    subtotal = producto["precio"] * cantidad
    descuento, base, impuesto = _calcular_montos(subtotal, cliente, aplica_vip=True)
    total = round(base + impuesto, 2)
    # descontar del inventario
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = producto["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(subtotal, 2)
    venta["descuento"] = round(descuento, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # armar el ticket en texto plano
    ticket = ""
    ticket = ticket + "TIENDA LA ESQUINA\n"
    ticket = ticket + "----------------------------\n"
    ticket = ticket + "Folio: " + str(venta["folio"]) + "\n"
    ticket = ticket + venta["nombre"] + " x" + str(cantidad) + "\n"
    ticket = ticket + "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if descuento > 0:
        ticket = ticket + "Descuento: -$" + str(venta["descuento"]) + "\n"
    ticket = ticket + "IVA: $" + str(venta["impuesto"]) + "\n"
    ticket = ticket + "TOTAL: $" + str(venta["total"]) + "\n"
    venta["ticket"] = ticket
    VENTAS.append(venta)
    return venta


def cotizar(codigo: str, cantidad: int | None) -> float | None:
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    subtotal = INVENTARIO[codigo]["precio"] * cantidad
    _, base, impuesto = _calcular_montos(subtotal)
    return round(base + impuesto, 2)
