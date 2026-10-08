# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexto

Reto académico de **refactorización sin cambiar comportamiento**: una app de consola en
Python (inventario y ventas de la tienda "La Esquina") que funciona, pero está llena de
*code smells* a propósito. El objetivo es mejorar `src/` hasta que `ruff check src` dé 0
errores, con los 20 tests pasando después de **cada** cambio. El código y la documentación
están en español; mantenlo así.

## Comandos

El entorno virtual es `venv/` (no `.venv` como dice el README), en Windows, Python 3.11.

```bash
venv/Scripts/python -m pytest                       # suite completa (20 tests)
venv/Scripts/python -m pytest tests/test_gestor.py::test_venta_cliente_vip_recibe_descuento_extra
venv/Scripts/python -m ruff check src               # debe terminar en 0 errores
venv/Scripts/python -m ruff check src --statistics  # resumen por regla
cd src && ../venv/Scripts/python main.py            # menú interactivo (lee/escribe datos_ejemplo.json en el cwd)
```

## Reglas del reto (no negociables)

- **No modificar `tests/` ni `pyproject.toml`** (también bloqueado en `.claude/settings.json`).
  Si un test falla, la refactorización alteró el comportamiento: se corrige el código, nunca el test.
- El comportamiento observable debe ser idéntico (valores de retorno, textos impresos,
  mensajes de `ultimo_error`, redondeos).
- `agregarProducto` y `buscarProducto` conservan su nombre (los usan los tests; `pyproject.toml`
  ya los exime de N802, no hace falta `# noqa`).
- Una refactorización por commit, en la rama `refactorizacion` (PR → `main`).
- Cada refactorización se documenta en `docs/bitacora.md` (prompt, cambio, justificación, resultado de tests).
- `docs/logs/` está bloqueado para lectura; no intentes leerlo por otra vía.

## Arquitectura

Cuatro módulos en `src/` que se importan de forma plana (`import gestor`), sin paquete:
`tests/conftest.py` agrega `src/` a `sys.path`, y `main.py` se ejecuta desde `src/`.

- **`gestor.py`** es dueño del **estado global**: `INVENTARIO` (dict código → dict producto),
  `VENTAS` (lista de dicts), `contadorVentas` (último folio) y `ultimo_error` (mensaje del último
  fallo). Las funciones señalan errores devolviendo `False`/`None` y escribiendo `ultimo_error`.
- **`almacen.py`** y **`reportes.py`** leen y escriben ese estado a través de `gestor.X`.
  `almacen.cargar_datos` reasigna `gestor.contadorVentas` y `gestor.ultimo_error` desde fuera,
  así que renombrar cualquiera de esas variables (p. ej. por N816) obliga a actualizar `almacen.py`.
- `conftest.py` llama `gestor.reiniciar_sistema()` antes y después de cada test; los tests
  inspeccionan `gestor.INVENTARIO` y `gestor.VENTAS` directamente, así que esos nombres y la
  forma de los dicts (`codigo`, `nombre`, `precio`, `stock`; venta con `folio`, `total`, `ticket`, …)
  son API pública.

### Detalles de comportamiento fáciles de romper

- **Precios** (`registrar_venta` y `cotizar` duplican el cálculo): descuento 10% si subtotal ≥ 1000,
  5% si ≥ 500; IVA 16% sobre (subtotal − descuento).
- El extra **VIP** (+2% del subtotal) aplica solo en `registrar_venta`, cuando `cliente` empieza con
  `"VIP"` y el monto **ya con el descuento por volumen** es > 200. `cotizar` **no** lo aplica. Si se
  extrae una función común de precios, debe preservar esta diferencia.
- Redondeo: la venta guarda `subtotal`, `descuento`, `impuesto` redondeados por separado y
  `total = round(base + impuesto, 2)`; `cotizar` devuelve `round(base + base * 0.16, 2)`. Hay un test
  que exige que ambos coincidan.
- El orden de validación en `registrar_venta` determina qué mensaje queda en `ultimo_error`
  (código vacío → producto no existe → cantidad inválida → stock insuficiente) y una venta fallida
  no debe tocar stock ni `VENTAS`.
- El ticket de texto solo incluye la línea "Descuento" si el descuento es > 0.
- `reportes.mas_vendidos` usa burbuja estable (empates conservan el orden de aparición);
  `sorted(..., key=..., reverse=True)` mantiene esa propiedad.
- `reporte_inventario` y `resumen_ventas` imprimen **y** devuelven el texto. El umbral de
  stock bajo (`< 5`) está repetido en dos funciones de `reportes.py`.

### Código muerto ya identificado

`calcular_descuento_viejo` y el bloque comentado `exportar_txt` en `gestor.py`, `reporteViejoCSV`
en `reportes.py` (sin referencias en `src/` ni `tests/`). `almacen.hayArchivo` solo se usa en
`main.py`, así que puede renombrarse/simplificarse actualizando esa llamada.
