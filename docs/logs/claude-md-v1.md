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
3. **Esperar aprobación** antes de aplicar el cambio.

Después de aplicarlo, reportar el resultado de `pytest` y de `ruff check src`.
