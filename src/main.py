"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

from collections.abc import Callable

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"
OPCION_SALIR = "8"


def pedir_numero(mensaje):
    # pide un numero al usuario hasta que escriba algo valido
    while True:
        temp2 = input(mensaje)
        try:
            return float(temp2)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def imprimir_opciones() -> None:
    print("")
    print("1) Agregar producto")
    print("2) Registrar venta")
    print("3) Cotizar")
    print("4) Reporte de inventario")
    print("5) Resumen de ventas")
    print("6) Mas vendidos")
    print("7) Alertas de stock bajo")
    print("8) Guardar y salir")


def agregar_producto() -> None:
    c = input("Codigo: ")
    n = input("Nombre: ")
    p = pedir_numero("Precio: ")
    s = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(c, n, p, s):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def registrar_venta() -> None:
    c = input("Codigo del producto: ")
    cant = int(pedir_numero("Cantidad: "))
    cli = input("Codigo de cliente (enter si no tiene): ")
    v = gestor.registrar_venta(c, cant, cli)
    if v is not None:
        print(v["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def cotizar() -> None:
    c = input("Codigo del producto: ")
    cant = int(pedir_numero("Cantidad: "))
    t = gestor.cotizar(c, cant)
    if t is not None:
        print("Total estimado (con IVA): $" + str(t))
    else:
        print("Error:", gestor.ultimo_error)


def reporte_inventario() -> None:
    reportes.reporte_inventario()


def resumen_ventas() -> None:
    reportes.resumen_ventas()


def mas_vendidos() -> None:
    for par in reportes.mas_vendidos():
        print(par[0], "->", par[1], "unidades")


def alertas_stock_bajo() -> None:
    bajos = reportes.productos_stock_bajo()
    if len(bajos) == 0:
        print("No hay productos con stock bajo.")
    else:
        for p in bajos:
            print("OJO:", p["nombre"], "solo tiene", p["stock"], "unidades")


def guardar_y_salir() -> None:
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")


ACCIONES: dict[str, Callable[[], None]] = {
    "1": agregar_producto,
    "2": registrar_venta,
    "3": cotizar,
    "4": reporte_inventario,
    "5": resumen_ventas,
    "6": mas_vendidos,
    "7": alertas_stock_bajo,
}


def menu() -> None:
    print("Bienvenido al gestor de la tienda La Esquina")
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)
    while True:
        imprimir_opciones()
        op = input("Opcion: ")
        if op == OPCION_SALIR:
            guardar_y_salir()
            break
        accion = ACCIONES.get(op)
        if accion is not None:
            accion()
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    menu()
