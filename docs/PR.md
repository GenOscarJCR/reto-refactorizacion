# Refactorización de "La Esquina" con Claude Code: ruff 20 → 0 sin cambiar el comportamiento

## Resumen

La app de consola de inventario y ventas de "La Esquina" funcionaba y pasaba sus 20 tests, pero
tenía *code smells* a propósito: `ruff check src` reportaba 20 errores. Con Claude Code se aplicaron
un commit `chore` de autofixes y 7 refactors atómicos: manejo de archivos con `with`, eliminación de
código muerto, constantes con nombre, renombrados, cálculo de precios común con VIP explícito,
división del menú y type hints. Resultado: **ruff 20 → 0** y **20 tests en verde en cada commit**.

## Configuración de Claude Code

### CLAUDE.md

Contiene: propósito del proyecto; comandos (`venv\Scripts\activate`, `pytest`, `ruff check src`,
`cd src && python main.py`); convenciones (PEP 8, `snake_case`, type hints, constantes en
MAYÚSCULAS, `with`, complejidad ≤ 10, con ejemplo antes/después); arquitectura y estado global de
`gestor.py`; detalles de comportamiento fáciles de romper (precios, VIP solo en `registrar_venta`,
redondeos, orden de validación, ticket, burbuja estable); código muerto ya identificado;
restricciones (no tocar `tests/` ni `pyproject.toml`, conservar `agregarProducto`/`buscarProducto`,
salida y JSON idénticos); flujo de verificación; y formato de respuesta con aprobación por riesgo.

| Versión | Cómo se obtuvo | Resultado |
|---|---|---|
| v0 | Generado con `/init` | Incluía arquitectura, comportamientos frágiles y código muerto; detectó que la bitácora decía 23 errores de ruff en lugar de 20 |
| v1 | Reescritura estructurada (Propósito, Comandos, Convenciones, Restricciones, Flujo, Formato) | Perdió arquitectura, detalles frágiles y código muerto porque el prompt decía "reescribe" en vez de "integra" |
| v2 | Reincorporación de esas secciones pegando la fuente en el prompt (`9ace35b`) | 115 líneas; Restricciones quedó idéntica; Claude señaló la duplicación y no la tocó por la restricción |
| v3 | Regla de aprobación por riesgo en "Formato de respuesta" (`463e386`) | Riesgo bajo: aplica si el prompt lo autoriza; riesgo medio/alto: plan y espera aprobación. Validada en R3/R9 (aplicó) y R5/R8 (esperó) |

### .claudeignore

Excluye `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `__MACOSX/`,
`.DS_Store`, `docs/logs/` y `src/datos_ejemplo.json`. Motivos: dependencias, bytecode y cachés
consumen tokens sin aportar nada; `__MACOSX/` y `.DS_Store` son basura del zip; `docs/logs/` evita
que Claude tome logs viejos como el estado actual; `datos_ejemplo.json` se genera al ejecutar.
`tests/` **no** se excluye: Claude debe leerlos como contrato de comportamiento.

### Hallazgo: `.claudeignore` no tiene efecto

La documentación de settings de Claude Code no menciona `.claudeignore`. Experimento: con
`Read(./docs/logs/**)` en `settings.json`, Claude no pudo leer `docs/logs/00-baseline-pytest.txt`;
al quitar esa regla (manteniendo `docs/logs/` en `.claudeignore`) y abrir un chat nuevo, Claude
mostró el archivo. La protección real viene de `permissions.deny` en `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./venv/**)", "Read(./.venv/**)",
      "Read(./**/__pycache__/**)", "Read(./.pytest_cache/**)",
      "Read(./.ruff_cache/**)", "Read(./docs/logs/**)",
      "Read(./src/datos_ejemplo.json)",
      "Edit(./tests/**)", "Edit(./pyproject.toml)"
    ]
  }
}
```

## Refactors

El commit `chore` de autofixes (`f8fd062`, ruff 20 → 13) no cuenta como refactor. Detalle de cada
uno en la [bitácora](bitacora.md#5-detalle-por-refactor).

1. **[R1 — `with` en persistencia y `hay_archivo`](bitacora.md#r1--with-en-persistencia-y-hay_archivo)**
   (`7f69aab`, ruff 13 → 9): `with open(...)` en `guardar_datos`/`cargar_datos`; `hayArchivo` →
   `hay_archivo` con `return os.path.exists(ruta)`.
2. **[R2 — eliminar código muerto](bitacora.md#r2--eliminar-código-muerto)** (`8811c39`, ruff 9 → 7):
   `MODO_DEBUG`, `calcular_descuento_viejo`, bloque comentado `exportar_txt` y `reporteViejoCSV`,
   tras verificar que no tenían referencias.
3. **[R3 — constantes con nombre](bitacora.md#r3--constantes-con-nombre)** (`d229e84`, ruff 7 → 7):
   umbrales y tasas de descuento, IVA, VIP y `STOCK_MINIMO` con los mismos valores.
4. **[R4 — renombrados claros](bitacora.md#r4--renombrados-claros)** (`553b94d`, ruff 7 → 5):
   `contadorVentas` → `contador_ventas`, `hacer_cosa` → `formatear_dinero` y locales descriptivos;
   claves de dicts y JSON intactas.
5. **[R5 — cálculo de precios común + VIP](bitacora.md#r5--cálculo-de-precios-común--vip)**
   (`4277244`, ruff 5 → 1): `_calcular_descuento_volumen`, `_es_cliente_vip` y `_calcular_montos`
   con `aplica_vip` explícito; `cotizar` sigue sin VIP.
6. **[R8 — dividir menu](bitacora.md#r8--dividir-menu)** (`c2f6098`, ruff 1 → 0): un handler por
   opción, `imprimir_opciones`, diccionario de despacho `ACCIONES` y `OPCION_SALIR`.
7. **[R9 — type hints](bitacora.md#r9--type-hints)** (`de3f704`, ruff 0 → 0): anotaciones en todas
   las firmas de `src/`, sin cambios de lógica.

## Instalación y ejecución

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest
ruff check src
cd src && python main.py
```

## Evidencia

- [99-final-pytest.txt](logs/99-final-pytest.txt): resultado final de `pytest`.
- [99-final-ruff.txt](logs/99-final-ruff.txt): resultado final de `ruff check src`.

## Notas

### Intentos fallidos

- **CLAUDE.md v1:** "reescribe" en lugar de "integra" hizo perder arquitectura, detalles frágiles y
  código muerto.
- **CLAUDE.md v2, primer intento:** no se ejecutó; la propia regla `deny` sobre `docs/logs/` impedía
  leer la fuente y el límite de ~80 líneas obligaba a recortar. Se corrigió pegando la fuente en el
  prompt.
- **R3, variante A** (prompt de una línea): funcionó por el contexto persistente, pero se descartó
  con `git reset --hard` en favor de la variante B (prompt estructurado).
- **Bitácora de R8:** se sobrescribió al editarla en VS Code mientras Claude la editaba; se recuperó
  del commit con `git restore`.

### Limitaciones

- `.claudeignore` no tiene efecto; solo `permissions.deny` bloquea lecturas.
- `deny` no cubre subprocesos: en R8 un comando `python` ejecutado por Claude leyó
  `src/datos_ejemplo.json` pese a la regla.
- `main.py` no tiene tests; R8 se verificó comparando la consola por stdin contra el commit anterior.
- En R3 y R4 Claude citó la numeración original de `plan-refactor.md` en sus notas.

### Trabajo futuro

- **R6 — dividir `registrar_venta`** (S1, S3, S9, S26): guard clauses en la validación, extraer el
  armado del ticket y un helper para registrar errores.
- **R7 — simplificar reportes** (S7 helper, S8, S25): helper `_es_stock_bajo`, reutilizar
  `total_vendido` en `resumen_ventas` y cambiar la burbuja de `mas_vendidos` por `sorted`
  conservando el orden de empates.
