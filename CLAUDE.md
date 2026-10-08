# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito

App de consola en Python 3.10+ para el inventario y las ventas de la tienda "La Esquina"
(`src/gestor.py` lógica, `src/almacen.py` JSON, `src/reportes.py` reportes, `src/main.py` menú).
Funciona y sus tests pasan, pero tiene *code smells* a propósito. El reto es **refactorizarla
sin cambiar su comportamiento observable** hasta que `ruff check src` termine sin errores.

## Comandos

```
venv\Scripts\activate
pip install -r requirements.txt
pytest
ruff check src
cd src && python main.py
```

## Convenciones

- PEP 8, `snake_case` para funciones y variables, líneas de máximo 88 caracteres.
- Type hints en funciones nuevas o modificadas.
- Constantes con nombre en MAYÚSCULAS en lugar de números mágicos.
- Archivos abiertos con `with`, sin `if` anidados innecesarios, complejidad ≤ 10 por función.

```python
# Antes
if aux >= 1000:
    desc = aux * 0.10

# Después
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10

def calcular_descuento(subtotal: float) -> float:
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    ...
```

## Arquitectura

Cuatro módulos en `src/` importados de forma plana (`import gestor`), sin paquete:
`tests/conftest.py` agrega `src/` a `sys.path` y `main.py` se ejecuta desde `src/`.

- **`gestor.py`** es dueño del **estado global**: `INVENTARIO` (dict código → dict producto),
  `VENTAS` (lista de dicts), `contadorVentas` (último folio) y `ultimo_error` (mensaje del último
  fallo). Las funciones señalan errores devolviendo `False`/`None` y escribiendo `ultimo_error`.
- **`almacen.py`** y **`reportes.py`** leen/escriben ese estado vía `gestor.X`. `almacen.cargar_datos`
  reasigna `gestor.contadorVentas` y `gestor.ultimo_error` desde fuera: renombrarlas (p. ej. por N816)
  obliga a actualizar `almacen.py`.
- `conftest.py` llama `gestor.reiniciar_sistema()` antes y después de cada test; los tests leen
  `gestor.INVENTARIO` y `gestor.VENTAS` directamente, así que esos nombres y la forma de los dicts
  (`codigo`, `nombre`, `precio`, `stock`; venta con `folio`, `total`, `ticket`, …) son API pública.

### Detalles de comportamiento fáciles de romper

- **Precios** (cálculo duplicado en `registrar_venta` y `cotizar`): descuento 10% si subtotal ≥ 1000,
  5% si ≥ 500; IVA 16% sobre (subtotal − descuento).
- **VIP** (+2% del subtotal) solo en `registrar_venta`, si `cliente` empieza con `"VIP"` y el monto
  **ya con descuento por volumen** es > 200. `cotizar` **no** lo aplica; una función común de precios
  debe preservar esta diferencia.
- Redondeo: la venta guarda `subtotal`, `descuento`, `impuesto` redondeados por separado y
  `total = round(base + impuesto, 2)`; `cotizar` devuelve `round(base + base * 0.16, 2)`. Un test
  exige que ambos coincidan.
- El orden de validación de `registrar_venta` fija el mensaje de `ultimo_error` (código vacío →
  producto no existe → cantidad inválida → stock insuficiente); una venta fallida no toca stock ni `VENTAS`.
- El ticket incluye la línea "Descuento" solo si el descuento es > 0.
- `reportes.mas_vendidos` usa burbuja estable (empates en orden de aparición);
  `sorted(..., key=..., reverse=True)` mantiene esa propiedad.
- `reporte_inventario` y `resumen_ventas` imprimen **y** devuelven el texto. El umbral de stock bajo
  (`< 5`) está repetido en dos funciones de `reportes.py`.

### Código muerto ya identificado

`calcular_descuento_viejo` y el bloque comentado `exportar_txt` en `gestor.py`; `reporteViejoCSV` en
`reportes.py` (sin referencias en `src/` ni `tests/`). `almacen.hayArchivo` solo se usa en `main.py`:
puede renombrarse/simplificarse actualizando esa llamada.
**No eliminar hasta que se solicite en un refactor específico.**

## Restricciones

- **NUNCA** modificar `tests/` ni `pyproject.toml`.
- Conservar los nombres `agregarProducto` y `buscarProducto` (los usan los tests).
- La salida de consola y el formato del JSON deben quedar idénticos: textos, tickets,
  mensajes de `ultimo_error`, redondeos y claves de los dicts.
- Una refactorización a la vez. No usar `ruff check src --fix` salvo que se pida.
- Si un test falla, se corrige el código, nunca el test.
- `gestor.INVENTARIO`, `gestor.VENTAS` y `gestor.reiniciar_sistema` son API que usan los tests.
  `almacen.py` reasigna `gestor.contadorVentas` y `gestor.ultimo_error`: si se renombran, hay que
  actualizar `almacen.py` también.
- Ojo con `cotizar`: no aplica el descuento VIP que sí aplica `registrar_venta`. Hay que conservar
  esa diferencia aunque se extraiga lógica común.

## Flujo de verificación

Después de **cada** refactorización:

1. `pytest`: deben pasar los 20 tests.
2. `ruff check src`: el número de errores no debe subir.
3. Si algo falla, corregir o revertir el cambio antes de seguir con otro.
4. Commit atómico en la rama `refactorizacion` y registro en `docs/bitacora.md`.

## Formato de respuesta

Antes de editar código:

1. Plan breve: qué *smell* se ataca y cómo.
2. Archivos afectados.
3. Aprobación, según el riesgo del refactor:
   - **Riesgo bajo** (cambios mecánicos, eliminar código muerto, extraer constantes,
     renombrados, type hints): si el prompt autoriza aplicarlo, se aplica directamente
     tras mostrar el plan, sin esperar confirmación. Si el prompt no lo autoriza
     explícitamente, **esperar aprobación**.
   - **Riesgo medio/alto** (cálculo de precios, dividir `registrar_venta`, dividir el menú
     de `main.py`): presentar **siempre** el plan y **esperar aprobación** antes de aplicar
     el cambio, aunque el prompt pida aplicarlo directamente.

Después de aplicarlo, reportar el resultado de `pytest` y de `ruff check src`.
