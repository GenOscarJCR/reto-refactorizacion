# Bitácora de refactorización

**Nombre:** Oscar Josué Coronilla Rangel
**Matrícula:** ocoronilla@gasen.mx
**Fecha:** 05 al 08 de octubre de 2026

## 1. Contexto del reto

Aplicar Claude Code como herramienta de desarrollo para mejorar código existente de forma sistemática, demostrando dominio de prompt engineering y flujos de trabajo efectivos con IA, sin romper la funcionalidad (20 tests) y dejando `ruff check src` sin errores.

## 2. Configuración

### 2.1 Preparación del repositorio
- El proyecto llegó como .zip con carpeta doble y basura de macOS (`__MACOSX`, `.DS_Store`).
- Moví la carpeta interior a `C:\Proyectos\ProyectosAprendizaje\reto-refactorizacion`.
- `git init`; commit de línea base en `main`: `d4f3895` "Línea base: proyecto original sin cambios (20 tests pasan)".
- Rama de trabajo: `refactorizacion` (PR hacia `main` de mi repo).

### 2.2 Entorno
- Windows + Cmder (cmd), Python 3.11.4.
- `python -m venv venv` → `venv\Scripts\activate` → `pip install -r requirements.txt`
- Nota: el README usa `.venv` y yo usé `venv`; ambos están en `.gitignore` y `.claudeignore`.

### 2.3 Línea base (antes de tocar código)
- pytest: 20 passed in 0.18s → [00-baseline-pytest.txt](logs/00-baseline-pytest.txt)
- `ruff check src`: 20 errores (UP009 x4, SIM102 x3, SIM115 x3, C901 x2, N802 x2, SIM108, N816, SIM103, UP015, I001, F401); 7 autocorregibles → [00-baseline-ruff.txt](logs/00-baseline-ruff.txt)

### 2.4 Investigación N802 (evidencia, no suposición)
- `agregarProducto` y `buscarProducto` NO aparecen: `pyproject.toml` ya los cubre con `ignore-names` → no hace falta `# noqa`.
- `hayArchivo`: solo se usa en `src\main.py:23` y no la usa ningún test → se renombra (y se actualiza ese llamado).
- `reporteViejoCSV`: solo existe su definición (`findstr` sobre src y tests) → código muerto, se elimina.

### 2.5 .gitignore


```
# Entornos virtuales
venv/
.venv/

# Archivos de caché de Python y pruebas
__pycache__/
.pytest_cache/
.ruff_cache/
src/datos_ejemplo.json

# Archivos del sistema operativo (macOS)
.DS_Store
__MACOSX/
```

| Entrada | Por qué |
|---|---|
| `venv/`, `.venv/` | Se ignoran para limitar el tamaño; las dependencias se declaran en `requirements.txt` |
| `__pycache__/` | Bytecode `.pyc` autogenerado que Python regenera solo; no es código fuente |
| `.pytest_cache/` | Caché que genera pytest en cada ejecución |
| `.ruff_cache/` | Caché que genera Ruff (linter) en cada ejecución |
| `src/datos_ejemplo.json` | Archivo generado al correr `main.py` dentro de `src` |
| `.DS_Store`, `__MACOSX/` | Archivos basura que venían en el zip de descarga |

### 2.6 .claudeignore

| Entrada | Por qué |
|---|---|
| `venv/`, `.venv/` | Son archivos pesados de las dependencias que consumirían tokens sin razón necesaria |
| `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/` | Archivos autogenerados (bytecode y cachés) que Python y las herramientas regeneran; no son código fuente |
| `__MACOSX/`, `.DS_Store` | Archivos basura |
| `docs/logs/` | Se excluye para que Claude no tome logs viejos como el estado actual |
| `src/datos_ejemplo.json` | Archivo generado en la ejecución de prueba |

Las razones principales: si se cargan esos archivos consumen tokens en el contexto sin aportar nada, y en otros proyectos algunos archivos pueden contener keys, usuarios o contraseñas. En este caso no hay secretos guardados; se especifica como medida de prevención.

- Decisión: NO excluyo `tests/`, porque Claude debe leerlos como contrato de comportamiento.
- Revisando la documentación de Claude Code (sección de settings) no hay referencia alguna a `.claudeignore`. Lo comprobé con un experimento (ver 2.8): **`.claudeignore` no tiene efecto**; la protección real viene de `permissions.deny`.

### 2.7 Decisiones de entrega
- La bitácora va en `docs/bitacora.md` (el formato de entrega manda sobre el README, que dice `BITACORA.md`).

### 2.8 Permisos y modos de Claude Code

`.claude/settings.json`:

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

- Prueba directa para validar `.claudeignore`:
    1. Hice la siguiente petición a Claude: "Muestra el contenido de docs/logs/00-baseline-pytest.txt".
    2. Claude contestó: "No pude mostrar el archivo. La configuración de permisos de este proyecto bloquea la lectura de docs/logs/00-baseline-pytest.txt: el directorio aparece como denegado. No intenté leerlo por otra vía (como cat en la terminal) para no saltarme esa regla. La regla probablemente está en tu .claude/settings.json o en .claudeignore, ambos sin rastrear en git."
    3. Quité la regla `"Read(./docs/logs/**)"` de `settings.json` y guardé (`docs/logs/` seguía en `.claudeignore`).
    4. Abrí un nuevo chat y le pedí lo mismo a Claude.
    5. Claude contestó "Este es el contenido de docs/logs/00-baseline-pytest.txt:" y me mostró el archivo.
    6. Regresé la regla a `settings.json`.

- **Conclusión:** Claude Code no respeta `.claudeignore`. En la primera prueba Claude mencionó ".claudeignore" como posible origen del bloqueo, pero la regla que realmente aplica es la de `settings.json`.
- **Limitación observada después (R8):** un comando `python` ejecutado por Claude leyó `src/datos_ejemplo.json` pese a la regla `deny`; la documentación indica que `deny` no cubre subprocesos arbitrarios.
- Evidencias: [1_config-deny-docs-logs.png](evidencias/1_config-deny-docs-logs.png) y [2_config-deny-docs-logs.png](evidencias/2_config-deny-docs-logs.png).
- Modo: Claude Code venía en **Auto** por defecto. Lo cambié a **Manual** para tener control: Claude pregunta antes de realizar acciones que pudieran ser peligrosas o estar fuera de los permisos. Para los refactors usé **Aceptar ediciones** (ver 3.6). Evidencia: [modo_manual_activo_claude_pregunta.png](evidencias/modo_manual_activo_claude_pregunta.png).
- La construcción de `CLAUDE.md` (v0 → v3) está en la sección 6.
- Commit: `e891556` chore: configuracion de Claude Code (.claudeignore, permissions.deny, logs de linea base) - 20 passed

## 3. Exploración

- Contexto: `/clear` al iniciar la fase. Modo: **Plan** (solo lectura).

### 3.1 Prompt


```
<contexto>Fase de exploración. No modifiques nada. Línea base de ruff: UP009 x4, SIM102 x3, SIM115 x3, C901 x2, N802 x2, SIM108, N816, SIM103, UP015, I001, F401.</contexto>
<tarea>Lee src/ y tests/ e inventaría los code smells en una tabla: ID (S1..), categoría, archivo:función, evidencia (1 línea), códigos ruff relacionados, refactor propuesto, riesgo para tests/comportamientos frágiles.</tarea>
<restricciones>No edites archivos ni ejecutes comandos. No propongas cambios a tests/ ni pyproject.toml.</restricciones>
<cobertura>Verifica cada categoría del README: funciones gigantes, duplicación, nombres crípticos, números mágicos, estado global, código muerto, anidamiento excesivo, nombrado mixto. Si no encuentras alguna, dilo. Lista los códigos ruff que no mapeaste.</cobertura>
<formato>Después de la tabla, agrupa los smells en ≥5 refactors atómicos ordenados de menor a mayor riesgo, justificando el orden.</formato>
```

### 3.2 Respuesta de Claude Code (resumen)

> Encontré 27 smells (S1–S27). Las 8 categorías del README aparecen en el código: funciones gigantes, duplicación, nombres crípticos, números mágicos, estado global, código muerto, anidamiento excesivo y nombrado mixto. Los 20 errores de la línea base de ruff corresponden a smells concretos.

- Resumen: 27 smells · 8/8 categorías del README · 20/20 códigos ruff mapeados · 0 sin mapear.
- Inventario completo: [01-exploracion-inventario.txt](logs/01-exploracion-inventario.txt) (copia legible por Claude: [plan-refactor.md](plan-refactor.md)).

### 3.3 Plan propuesto por Claude

Refactors atómicos, de menor a mayor riesgo (en cada paso, pytest debe dar 20 passed):

| # | Refactor | Errores de ruff que quita |
|---|---|---|
| R1 | Cabeceras e imports | 6 |
| R2 | with en almacen.py y hay_archivo | 5 |
| R3 | Eliminar código muerto | 2 |
| R4 | Constantes y renombrados (contador_ventas, formatear_dinero) | 1 |
| R5 | Simplificar reportes.py (sorted estable, helper de stock bajo) | 0 |
| R6 | Función de precios común con VIP explícito | 4 |
| R7 | Dividir registrar_venta | 1 |
| R8 | Dividir menu | 1 |

> Con los ocho, ruff baja de 20 a 0. R3 solo se aplica si lo pides explícitamente, como exige CLAUDE.md. R6 y R7 tocan las reglas más frágiles: el VIP que solo aplica a ventas, los redondeos, que cotizar coincida con el total de la venta y el orden de los mensajes de ultimo_error. R8 va al final porque main.py no tiene tests. El estado global (S24) se puede mitigar, pero no eliminar sin romper la API que usan los tests.

### 3.4 Mi revisión y ajustes al plan

Ajusto el plan de Claude según el README. Cabeceras, imports y el "r" redundante son autofixes de ruff, así que van en un commit chore que no cuenta como refactor. Divido "constantes y renombrados" en dos commits para que cada diff sea revisable. Agrego type hints, que el README marca como refactor válido y el plan de Claude no incluía.

### 3.5 Plan final

| ID | Refactor | Smells | Ejecutado |
|---|---|---|---|
| chore | Autofixes de ruff (no cuenta) | S21, S22, S23, UP015 | ✅ |
| R1 | with en persistencia + hay_archivo | S15, S18, S19 | ✅ |
| R2 | Eliminar código muerto | S16, S20 | ✅ |
| R3 | Constantes con nombre | S7, S10, S11 | ✅ |
| R4 | Renombrados claros | S12, S13, S14 | ✅ |
| R5 | Cálculo de precios común + VIP | S4, S5, S6 | ✅ |
| R6 | Dividir registrar_venta | S1, S3, S9, S26 | ❌ trabajo futuro |
| R7 | Simplificar reportes (+ helper de S7) | S7, S8, S25 | ❌ trabajo futuro |
| R8 | Dividir menu | S2 | ✅ |
| R9 | Type hints | — | ✅ |

### 3.6 Observaciones del proceso

- Al terminar, el modo Plan pidió aprobar y ejecutar todo el plan. No lo acepté: cada refactor se ejecuta por separado, con su propio prompt y su verificación. Modo de trabajo habilitado para cada refactor: **Aceptar ediciones** (los tests y un commit por refactor respaldan la autonomía).
- Detecté que `plan-refactor.md` tenía la numeración original de Claude y no coincidía con mis prompts. Agregué el plan final al inicio del archivo para evitar que Claude confundiera los refactors. Aun así, en R3 y R4 Claude citó la numeración original en sus notas (se aclara en cada entrada).
- Al tener la bitácora abierta en VS Code mientras Claude la editaba, sobrescribí su entrada de R8. La recuperé del commit con `git restore`. Lección: no editar el mismo archivo que el agente en paralelo; el commit por refactor fue la red de seguridad.

## 4. Resumen


| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | R1 — with en persistencia y hay\_archivo (ver 5. R1) | `almacen.py`: `with open(...)` en `guardar_datos`/`cargar_datos`; `hayArchivo` → `hay_archivo` con `return os.path.exists(ruta)`; `main.py` actualizado | Cierre de archivos garantizado; nombre PEP 8; quita if/else redundante. Ruff 13 → 9 (SIM115 x2, N802, SIM103) | 20 passed |
| 2  | R2 — eliminar código muerto (ver 5. R2) | `gestor.py`: eliminados `MODO_DEBUG`, `calcular_descuento_viejo` y el bloque comentado `exportar_txt`; `reportes.py`: eliminada `reporteViejoCSV` | Código sin referencias en `src/` ni `tests/` (verificado con búsqueda); menos ruido y mantenimiento. Ruff 9 → 7 (N802, SIM115) | 20 passed |
| 3  | R3 — constantes con nombre (ver 5. R3) | `gestor.py`: constantes `UMBRAL_DESCUENTO_ALTO/MEDIO`, `TASA_DESCUENTO_ALTO/MEDIO`, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_EXTRA_VIP`, `TASA_IVA` en `registrar_venta` y `cotizar`; `reportes.py`: `STOCK_MINIMO` en `productos_stock_bajo` y `reporte_inventario` | Reglas de negocio con nombre y en un solo lugar; mismos valores numéricos. Ruff 7 → 7 (no hay regla activa para números mágicos) | 20 passed |
| 4  | R4 — renombrados claros (ver 5. R4) | `gestor.py`: `contadorVentas` → `contador_ventas` y locales (`x`, `aux`, `temp2`, `desc`, `t`, `k`) con nombres descriptivos; `reportes.py`: `hacer_cosa` → `formatear_dinero` y locales (`s`, `t`, `aux`, `temp`, `p`, `k`, `v`); `almacen.py`: referencias a `contador_ventas` y locales (`d`, `f`, `k`, `v`) | Nombres que dicen qué guardan; `contador_ventas` sigue PEP 8. Claves de dicts/JSON intactas. Ruff 7 → 5 (N816; SIM108 deja de reportarse porque el ternario ya no cabe en 88 caracteres) | 20 passed |
| 5  | R5 — cálculo de precios común + VIP (ver 5. R5) | `gestor.py`: nuevas `_calcular_descuento_volumen`, `_es_cliente_vip` y `_calcular_montos(subtotal, cliente=None, aplica_vip=False)` con type hints; `registrar_venta` la usa con `aplica_vip=True` y `cotizar` sin VIP | Elimina el cálculo duplicado y los `if` anidados; el VIP queda como opción explícita y `cotizar` sigue sin aplicarlo. Mismos redondeos. Ruff 5 → 1 (SIM102 x3, C901 de `registrar_venta`) | 20 passed |
| 8  | R8 — dividir menu (ver 5. R8) | `main.py`: una función por opción (`agregar_producto`, `registrar_venta`, `cotizar`, `reporte_inventario`, `resumen_ventas`, `mas_vendidos`, `alertas_stock_bajo`, `guardar_y_salir`), `imprimir_opciones`, diccionario de despacho `ACCIONES` y constante `OPCION_SALIR`; `menu` queda como orquestador | Cada opción se lee y se cambia sola; agregar una opción es una función + una entrada del dict. Salida de consola idéntica (comparada contra `HEAD` por stdin). Ruff 1 → 0 (C901 de `menu`) | 20 passed |
| 9  | R9 — type hints (ver 5. R9) | `gestor.py`, `almacen.py`, `reportes.py`, `main.py`: anotaciones de parámetros y retorno en todas las firmas que no las tenían (`str \| None`, `int \| None`, `list[dict[str, Any]]`, `dict[str, Any] \| None`, `list[tuple[str, int]]`, …); `from typing import Any` en `gestor.py` y `reportes.py` | Las firmas documentan qué reciben y qué devuelven (incluido el `None`/`False` de error) y habilitan revisión estática. Sin cambios de lógica, nombres ni valores por defecto. Ruff 0 → 0 | 20 passed |

R6 y R7 no se ejecutaron por tiempo (ver sección 5, "R6 y R7 — trabajo futuro"). El chore no cuenta como refactor.

## 5. Detalle por refactor


### C0 — chore (no cuenta): autofixes de ruff

**Prompt:**

```
<tarea>Aplica SOLO este paso: chore — autofixes de ruff con `ruff check src --fix`. Smells: S21, S22, S23 y UP015 (S19), descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Te autorizo a usar --fix solo en este paso; no cuenta como refactor. Solo modifica archivos de src/ y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md, sección 5, agrega una entrada "chore (no cuenta)" con este prompt literal en un bloque de código, el cambio (resumen y archivos), el resultado de pytest y el conteo de ruff antes → después. No agregues fila a la tabla de la sección 4.</bitacora>
<commit>Haz un commit: "chore: autofixes de ruff - N passed, ruff X"</commit>
```

**Cambio:** se ejecutó `ruff check src --fix` (sin `--unsafe-fixes`). Antes se revisó el diff con
`--fix --diff`: solo contenía los 7 autofixes esperados, sin cambios de lógica.

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/almacen.py` | Quitada cabecera `# -*- coding: utf-8 -*-`; `open(ruta, "r", encoding=...)` → `open(ruta, encoding=...)` | UP009, UP015 | S23, S19 (parcial) |
| `src/gestor.py` | Quitada cabecera coding | UP009 | S23 |
| `src/main.py` | Quitada cabecera coding; imports ordenados (`almacen`, `gestor`, `reportes`) | UP009, I001 | S23, S22 |
| `src/reportes.py` | Quitada cabecera coding; eliminado `import os` sin uso | UP009, F401 | S23, S21 |

**pytest:** 20 passed.
**ruff check src:** 20 → 13 (quedan SIM102 x3, SIM115 x3, C901 x2, N802 x2, SIM108, N816, SIM103).

**Mi observación:** Claude revisó el diff con `--fix --diff` antes de aplicar y no usó `--unsafe-fixes`. Los 7 arreglos no tocan la lógica. Lo acepto. Nota: el commit incluyó también mis cambios previos a la bitácora (secciones 2 a 3.6).

**Commit:** `f8fd062`

### R1 — with en persistencia y hay_archivo

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R1 — usar with en la persistencia y renombrar/simplificar hayArchivo a hay_archivo. Smells: S15, S18, S19 (solo almacen.py), descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica src/almacen.py, src/main.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico. cargar_datos debe seguir devolviendo False con el mismo mensaje de error.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R1: with en persistencia y hay_archivo - N passed, ruff X"</commit>
```

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/almacen.py` | `guardar_datos`: `f = open(...)` + `f.close()` → `with open(ruta, "w", encoding="utf-8") as f:` | SIM115 | S19 |
| `src/almacen.py` | `cargar_datos`: `with open(ruta, encoding="utf-8") as f:` con el `try/except Exception` dentro; se quitan los dos `f.close()` manuales | SIM115 | S19 |
| `src/almacen.py` | `hayArchivo` → `hay_archivo`; cuerpo `return os.path.exists(ruta)`; el comentario pasa a docstring | N802, SIM103 | S15, S18 |
| `src/main.py` | Llamada `almacen.hayArchivo(ARCHIVO)` → `almacen.hay_archivo(ARCHIVO)` | — | S15 |

Sin type hints (quedan para R9). `reporteViejoCSV` (SIM115 en `reportes.py`) no se tocó: es código muerto reservado para R2.

**Justificación:** `with` garantiza el cierre del archivo aunque `json.load`/`json.dump` lancen excepción, y elimina el `f.close()` duplicado en `cargar_datos`. El `except Exception` se mantuvo sin estrechar, y el `return False` dentro del `with` cierra el archivo igual que antes. `hay_archivo` sigue PEP 8 y `os.path.exists` ya devuelve `bool`, así que el `if/else` era redundante. Ningún test usa `hayArchivo`; su único llamador es `main.py`.

**Verificación extra (manual):** archivo corrupto → `False`, `ultimo_error = "archivo corrupto"`; archivo inexistente → `False`, `"el archivo no existe"`; `hay_archivo` → `True`/`False` según exista.

**pytest:** 20 passed.
**ruff check src:** 13 → 9 (quedan N816, C901 x2, SIM108, SIM102 x3, N802 y SIM115 de `reporteViejoCSV`).

**Mi observación:** Claude propuso type hints fuera de alcance; los rechacé para mantener el refactor atómico, porque van en R9. También detectó la doble numeración en `plan-refactor.md` y eligió la del plan final. Verificó a mano los casos de archivo corrupto e inexistente, que no tienen test; ambos devuelven lo mismo que antes. Lo acepto.

**Commit:** `7f69aab`

### R2 — eliminar código muerto

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R2 — eliminar código muerto (calcular_descuento_viejo, comentario de exportar_txt, reporteViejoCSV y MODO_DEBUG). Smells: S16, S20, descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Te autorizo explícitamente a eliminar ese código muerto; antes de borrar, confirma con una búsqueda que no tiene referencias en src/ ni tests/. Solo modifica src/gestor.py, src/reportes.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R2: eliminar codigo muerto - N passed, ruff X"</commit>
```

**Verificación previa:** búsqueda de `calcular_descuento_viejo|exportar_txt|reporteViejoCSV|MODO_DEBUG` en `src/` y `tests/`: solo aparecían sus propias definiciones (`gestor.py:16`, `gestor.py:184`, `gestor.py:192`, `reportes.py:81`). Tras el cambio, la misma búsqueda no devuelve nada.

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/gestor.py` | Eliminada la constante `MODO_DEBUG = False` (sin uso) | — | S20 |
| `src/gestor.py` | Eliminada `calcular_descuento_viejo` (fórmula de 2023 que nadie llama) | — | S20 |
| `src/gestor.py` | Eliminado el bloque comentado `exportar_txt` | — | S20 |
| `src/reportes.py` | Eliminada `reporteViejoCSV` (camelCase y `open` sin `with`) | N802, SIM115 | S16, S20 |

**Justificación:** el código muerto confunde a quien lee ("¿esto se usa?"), hay que mantenerlo y arrastra sus propios smells (N802, SIM115) sin aportar nada. Como no tiene llamadores en `src/` ni `tests/`, eliminarlo no cambia el comportamiento observable. Si alguna vez hiciera falta, el historial de git lo conserva.

**pytest:** 20 passed.
**ruff check src:** 9 → 7 (quedan N816, C901 x2, SIM108, SIM102 x3).

**Mi observación:** Claude confirmó con búsqueda que no había referencias antes y después de borrar. Se saltó el plan previo de CLAUDE.md por interpretar mi autorización como aprobación. Lo acepto, y aclaro la regla en CLAUDE.md v3 (sección 6.5).

**Commit:** `8811c39`

### R3 — constantes con nombre

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R3 — reemplazar números mágicos por constantes con nombre en MAYÚSCULAS (umbrales y tasas de descuento, IVA, VIP, stock mínimo). Smells: S7, S10, S11, descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica src/gestor.py, src/reportes.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico. Las constantes conservan exactamente los mismos valores numéricos.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R3: constantes con nombre - N passed, ruff X"</commit>
```

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/gestor.py` | Bloque de constantes al inicio: `UMBRAL_DESCUENTO_ALTO = 1000`, `TASA_DESCUENTO_ALTO = 0.10`, `UMBRAL_DESCUENTO_MEDIO = 500`, `TASA_DESCUENTO_MEDIO = 0.05`, `PREFIJO_VIP = "VIP"`, `MONTO_MINIMO_VIP = 200`, `TASA_EXTRA_VIP = 0.02`, `TASA_IVA = 0.16` | — | S10 |
| `src/gestor.py` | `registrar_venta`: literales reemplazados por las constantes; `len(cliente) >= 3` y `cliente[0:3] == "VIP"` → `len(PREFIJO_VIP)` y `PREFIJO_VIP` | — | S10 |
| `src/gestor.py` | `cotizar`: umbrales, tasas de descuento e IVA reemplazados por las mismas constantes (sigue sin aplicar el extra VIP) | — | S10 |
| `src/reportes.py` | Constante `STOCK_MINIMO = 5`, usada en `productos_stock_bajo` y `reporte_inventario` en lugar del `< 5` repetido | — | S7 (parcial), S11 |


No se tocó la estructura (`if` anidados, `else: desc = 0`, burbuja, etc.): SIM102/SIM108/C901 quedan para R6/R7. De S7 solo se unificó el umbral; el helper `_es_stock_bajo` queda para R5.

*Nota de numeración: aquí Claude usó la numeración de su propuesta original. En el plan final, los `if` anidados y SIM108 se atendieron en R5, y el helper de S7 pasó a R7 (no ejecutado).*


**Justificación:** los literales 1000, 0.10, 500, 0.05, 200, 0.02, 0.16 y 5 son reglas de negocio sin nombre y estaban duplicados entre `registrar_venta`/`cotizar` y entre dos funciones de `reportes.py`; si cambiara el IVA o un umbral habría que encontrar cada copia. Con constantes, la regla se lee por su nombre y se cambia en un solo lugar. Los valores son exactamente los mismos (mismos `float`), así que los cálculos y redondeos no cambian. `PREFIJO_VIP` con `len(PREFIJO_VIP)` = 3 conserva la comprobación original. Además, deja listas las constantes que usará la función común de precios (R6).

**pytest:** 20 passed.
**ruff check src:** 7 → 7 (sin cambio esperado: los números mágicos no tienen regla activa en la configuración de ruff; quedan N816, C901 x2, SIM108, SIM102 x3).

**Comparación de variantes:**

- **Variante A** (prompt de 1 línea: "Reemplaza los números mágicos por constantes."): Claude hizo el ciclo completo (tests, ruff, bitácora y commit "R3: constantes con nombre"), tocando `gestor.py` y `reportes.py`. Lo atribuyo al contexto persistente: CLAUDE.md, `plan-refactor.md` y el historial de commits. Commit de la variante A conservado como evidencia: `6cc4585` → [R3-variante-A.txt](logs/R3-variante-A.txt). Evidencias: [R3_A_1_pide_permiso_p_run_test_ruff.png](evidencias/R3_A_1_pide_permiso_p_run_test_ruff.png), [R3_A_2_trabajando.png](evidencias/R3_A_2_trabajando.png).
- **Variante B** (prompt estructurado): nuevamente Claude hizo el ciclo completo, de acuerdo con la estructura del prompt.
- **Conclusión:** /clear borra la conversación, así que la variante A funcionó por el contexto persistente (CLAUDE.md, plan-refactor.md e historial de commits), no por memoria del chat. La variante B agregó control explícito (alcance, archivos permitidos, restricciones), pero un buen CLAUDE.md hace que incluso un prompt corto funcione. Hice `git reset --hard` del commit de la variante A y me quedé con la variante B.

**Mi observación:** Mismos valores en las constantes; `cotizar` sigue sin VIP. El helper de S7 quedó pendiente porque Claude usó la numeración original del plan; lo muevo a R7.

**Commit:** `d229e84`

### R4 — renombrados claros

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R4 — renombrar para claridad: contadorVentas a contador_ventas, hacer_cosa a formatear_dinero y variables locales crípticas a nombres descriptivos. Smells: S12, S13, S14, descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica src/gestor.py, src/reportes.py, src/almacen.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico. No cambies claves de diccionarios ni del JSON, ni los nombres agregarProducto y buscarProducto. Verifica que ningún test use los nombres que cambias.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R4: renombrados claros - N passed, ruff X"</commit>
```

**Verificación previa:** búsqueda de `contadorVentas|hacer_cosa` en todos los `.py`: solo aparecían en `src/gestor.py`, `src/almacen.py` y `src/reportes.py`. Ningún test ni `main.py` los usa. Tras el cambio, la búsqueda no devuelve nada.

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/gestor.py` | Global `contadorVentas` → `contador_ventas` (declaración, `reiniciar_sistema`, `registrar_venta`) | N816 | S14 |
| `src/gestor.py` | Locales: `agregarProducto` `x` → `producto`; `actualizar_stock` `aux` → `nuevo_stock`; `buscarProducto` `temp2` → `resultados`, `k` → `codigo`; `registrar_venta` `temp2` → `producto`, `aux` → `subtotal`, `desc` → `descuento`, `t` → `ticket`; `cotizar` `aux` → `subtotal`, `desc` → `descuento` | — | S12 |
| `src/reportes.py` | `hacer_cosa(v)` → `formatear_dinero(monto)` y sus 4 llamadas | — | S13 |
| `src/reportes.py` | Locales: `productos_stock_bajo` `temp2` → `resultados`; `reporte_inventario` `s` → `reporte`, `aux` → `valor_total`, `p` → `producto`; `total_vendido`/`resumen_ventas` `t` → `total`, `v` → `venta`, `s` → `resumen`; `mas_vendidos` `aux` → `unidades`, `temp` → `ranking`, `t` → `intercambio`; `k` → `codigo` | — | S12 |
| `src/almacen.py` | `gestor.contadorVentas` → `gestor.contador_ventas` en `guardar_datos` y `cargar_datos`; locales `d` → `datos`, `f` → `archivo`, `k` → `codigo`, `v` → `venta` | — | S12, S14 |

Tres líneas de `reportes.py` se partieron en dos para no rebasar 88 caracteres con los nombres largos; la concatenación da el mismo texto. Las claves de dicts (`"codigo"`, `"descuento"`, `"contador"`, …), los textos y la estructura (ifs anidados, burbuja) no cambiaron. Sin type hints (quedan para R9).

**Justificación:** `x`, `aux`, `temp2`, `t` o `hacer_cosa` obligan a leer el cuerpo para saber qué contienen; con `subtotal`, `descuento`, `ticket` o `formatear_dinero` la función se entiende por sus nombres. Además ayuda a R6, donde el cálculo de precios se extrae con nombres claros. `contador_ventas` sigue la convención `snake_case` del módulo (N816); se actualizó `almacen.py`, que reasigna la global desde fuera. La clave JSON `"contador"` no cambió, así que los archivos guardados antes se siguen cargando.

**Verificación extra (manual):** un script ejecutó las mismas operaciones contra `HEAD` y contra la versión nueva: altas, `actualizar_stock` con error, búsqueda, ventas normales, VIP y fallidas (los 4 mensajes de `ultimo_error`), `cotizar`, los tres reportes, `guardar_datos` y `cargar_datos` (ida y vuelta, y archivo inexistente). Las 102 líneas de salida son idénticas, sin contar `fecha`.

**pytest:** 20 passed.
**ruff check src:** 7 → 5 (quedan C901 x2, SIM102 x3). Se fue N816 (esperado). SIM108 también dejó de reportarse sin cambio de estructura: ruff no lo sugiere si el ternario resultante pasa de 88 caracteres, y con `descuento`/`subtotal` ya no cabe. El `if/else` anidado sigue ahí y se aplana en R6.

*Nota de numeración: "R6" es de la propuesta original; en el plan final el anidamiento se aplanó en R5.*

**Mi observación:** Claude comparó la salida del commit anterior contra el nuevo (102 líneas idénticas) y aclaró que SIM108 desapareció por longitud de línea, no por un arreglo real. Lo acepto; el anidamiento se atiende en R5.

**Commit:** `553b94d`

### R5 — cálculo de precios común + VIP

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R5 — extraer una función común de cálculo de montos (descuento por volumen e IVA) usada por registrar_venta y cotizar, con el VIP como opción explícita, y aplanar los if anidados del VIP. Smells: S4, S5, S6, descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica src/gestor.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico. El VIP solo aplica en registrar_venta, nunca en cotizar. Conserva los mismos redondeos y que cotizar coincida con el total de la venta.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R5: calculo de precios comun - N passed, ruff X"</commit>
```

**Aprobación:** CLAUDE.md lo clasifica como riesgo medio/alto (cálculo de precios), así que Claude presentó el plan y esperó aprobación antes de editar. Al aprobar pedí además comparar la salida del commit anterior contra la nueva en casos límite.

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/gestor.py` | Nueva `_calcular_descuento_volumen(subtotal) -> float`: `if`/`if`/`return 0` planos en lugar de `else: if … else: descuento = 0` | (SIM108) | S5 |
| `src/gestor.py` | Nueva `_es_cliente_vip(cliente) -> bool`: `bool(cliente) and cliente.startswith(PREFIJO_VIP)` reemplaza los 3 `if` de `""`/`None`, longitud y prefijo | SIM102 x3 | S4 |
| `src/gestor.py` | Nueva `_calcular_montos(subtotal, cliente=None, aplica_vip=False) -> tuple[float, float, float]`: devuelve `(descuento, base, impuesto)` sin redondear; el extra VIP solo si `aplica_vip` y la base ya con descuento por volumen es > `MONTO_MINIMO_VIP` | — | S6 |
| `src/gestor.py` | `registrar_venta`: el bloque de descuento/VIP/IVA → `_calcular_montos(subtotal, cliente, aplica_vip=True)` | C901 | S6 |
| `src/gestor.py` | `cotizar`: el bloque duplicado → `_calcular_montos(subtotal)` (sin VIP); devuelve `round(base + impuesto, 2)` | — | S6 |

Sin cambios en la validación de `registrar_venta`, el folio, el stock, el ticket ni las claves del dict. Las funciones existentes siguen sin type hints (R9); solo las nuevas los tienen.

**Justificación:** el mismo cálculo de descuento e IVA estaba copiado en dos funciones; un cambio de regla había que hacerlo dos veces y podía desincronizarse, cuando un test exige que `cotizar` coincida con el total de la venta. Con una sola función ambas usan el mismo código. El VIP pasa a ser un parámetro explícito (`aplica_vip`), así la diferencia entre venta y cotización queda a la vista en la llamada, en lugar de depender de que una copia tenga un bloque que la otra no. Detalles que se preservaron: sin descuento se devuelve el entero `0` (no `0.0`), para que `venta["descuento"]` y el JSON salgan iguales; `base + impuesto` es exactamente la misma operación de punto flotante que `base + base * TASA_IVA`; y los redondeos siguen en `registrar_venta`/`cotizar`, no en la función común.

**Verificación extra (manual):** un script corrió 15 casos contra el `gestor.py` de `HEAD` (19a77d6) y contra el nuevo, comparando `cotizar`, el dict completo de la venta (valores y tipos, sin `fecha`), el ticket, el stock y `ultimo_error`: subtotal exactamente 500 y 1000 (y 499.99 / 999.99); VIP con base exactamente 200 (no aplica) y 200.01 (aplica); VIP con subtotal 500 y 1000; cliente `"VIP"`, `"VI"`, `None`, `""` y `"vip001"` en minúsculas. **Salidas idénticas.** `cotizar == total` da `True` en todos los casos sin VIP y `False` en los 4 con VIP aplicado, igual que antes (cotizar no aplica el extra VIP).

**pytest:** 20 passed.
**ruff check src:** 5 → 1 (se fueron SIM102 x3 y C901 de `registrar_venta`, que bajó de 12 a ≤ 10 al salir los `if` del cálculo; queda C901 de `menu` en `main.py`).

**Mi observación:** Acepté type hints solo en las funciones nuevas. Pedí una verificación con casos límite del VIP y de los umbrales, porque es la regla de negocio más frágil y los tests no la cubren completa.

**Commit:** `4277244`

### R6 y R7 — trabajo futuro (no ejecutados)

Por tiempo no se ejecutaron. Quedan pendientes con sus smells:

- **R6 — dividir `registrar_venta`** (S1, S3, S9, S26): guard clauses en la validación, extraer el armado del ticket y un helper para registrar errores. El C901 de `registrar_venta` ya desapareció con R5, pero la función sigue mezclando validación, stock, folio y ticket.
- **R7 — simplificar reportes** (S7 helper, S8, S25): helper `_es_stock_bajo`, reutilizar `total_vendido` en `resumen_ventas` y cambiar la burbuja de `mas_vendidos` por `sorted` conservando el orden de empates.


### R8 — dividir menu

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R8 — dividir menu en una función por opción y un diccionario de despacho. Smells: S2, descritos en docs/plan-refactor.md.</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica src/main.py y docs/bitacora.md. No atiendas otros smells. Comportamiento observable idéntico. Los textos de consola, las opciones y su numeración deben quedar idénticos. main.py no tiene tests: al terminar dime qué opciones debo probar a mano.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R8: dividir menu - N passed, ruff X"</commit>
```

**Aprobación:** CLAUDE.md lo clasifica como riesgo medio/alto (dividir el menú de `main.py`), así que Claude presentó el plan y esperó aprobación. Al aprobar pedí comparar la salida de consola del commit anterior contra la nueva, alimentando `main.py` por stdin desde `src/`, y no versionar el `datos_ejemplo.json` generado.

**Cambio:**

| Archivo | Cambio | Ruff | Smell |
|---|---|---|---|
| `src/main.py` | Nueva `imprimir_opciones() -> None` con los mismos 9 `print` del menú (línea vacía + opciones 1–8) | — | S2 |
| `src/main.py` | Un handler `-> None` por opción con el cuerpo de su rama, sin cambios: `agregar_producto`, `registrar_venta`, `cotizar`, `reporte_inventario`, `resumen_ventas`, `mas_vendidos`, `alertas_stock_bajo`, `guardar_y_salir` | — | S2 |
| `src/main.py` | Diccionario de despacho `ACCIONES: dict[str, Callable[[], None]]` para las opciones `"1"`–`"7"` y constante `OPCION_SALIR = "8"` | — | S2 |
| `src/main.py` | `menu() -> None`: bienvenida y carga inicial igual; el `while` imprime opciones, lee `op`, sale con `guardar_y_salir()` + `break` si es `OPCION_SALIR`, despacha con `ACCIONES.get(op)` o imprime `"Opcion no valida."` | C901 | S2 |

`pedir_numero`, `ARCHIVO`, los nombres locales (`c`, `cant`, `cli`, …), los textos y el orden de `input`/`print` no cambiaron. La salida queda fuera del diccionario para que el `break` siga visible en el bucle y todos los handlers tengan la misma firma.

**Justificación:** `menu` mezclaba en un solo bloque la presentación del menú, la lectura de datos y la llamada a `gestor`/`reportes`/`almacen` de las 8 opciones (complejidad 17). Con un handler por opción cada caso se entiende y se modifica por separado, y el despacho por diccionario sustituye la cadena `if/elif`: agregar una opción es escribir una función y añadir una entrada. Como los cuerpos se movieron sin tocarlos, los textos y el flujo de entrada son los mismos.

**Verificación extra (manual, por stdin):** un script ejecutó desde `src/` el `main.py` de `HEAD` (d1f8379) y el nuevo con las mismas entradas simuladas, en dos escenarios: (A) sin `datos_ejemplo.json`: reportes vacíos (4–7), altas con stock bajo, con número inválido y reintento, y con código duplicado; venta VIP con descuento, venta sin descuento y los 4 errores (código vacío, no existe, cantidad inválida, stock insuficiente); cotizar válido e inexistente; reportes con datos; opciones inválidas `9`, vacío y `abc`; salir (8). (B) arrancando con el JSON generado en A ("Datos cargados de"): reportes, una venta y salir. **Salidas idénticas** (272 y 81 líneas), sin errores en stderr. El `datos_ejemplo.json` del usuario se respaldó antes y se restauró después; está en `.gitignore` y no se versiona.

**pytest:** 20 passed.
**ruff check src:** 1 → 0 (se fue C901 de `menu`). `All checks passed!`

**Mi observación:** Claude comparó la consola por stdin (272 y 81 líneas idénticas). Admitió que un comando python leyó `datos_ejemplo.json` saltándose mi regla deny, lo que confirma la limitación documentada: deny no cubre subprocesos. Lo acepto.

**Commit:** `c2f6098`

### R9 — type hints

**Prompt:**

```
<tarea>Aplica SOLO este refactor: R9 — agregar type hints a las firmas de las funciones de src/ (sintaxis de Python 3.10+, como str | None).</tarea>
<restricciones>Respeta CLAUDE.md. Solo modifica archivos de src/ y docs/bitacora.md. Solo anotaciones: no cambies lógica, nombres ni valores por defecto. Comportamiento observable idéntico.</restricciones>
<verificacion>Ejecuta pytest y ruff check src. Si algo falla, corrige el código (nunca los tests) y repite.</verificacion>
<bitacora>En docs/bitacora.md: agrega una fila a la tabla de la sección 4 y, en la sección 5, una entrada con título, este prompt literal en un bloque de código, el cambio (resumen y archivos), la justificación, el resultado de pytest y el conteo de ruff antes → después.</bitacora>
<commit>Haz un commit: "R9: type hints - N passed, ruff X"</commit>
```

**Aprobación:** CLAUDE.md clasifica los type hints como riesgo bajo y el prompt autoriza aplicarlos, así que Claude mostró el plan y lo aplicó sin esperar.

**Cambio:**

| Archivo | Cambio |
|---|---|
| `src/gestor.py` | `from typing import Any`; `reiniciar_sistema() -> None`; `agregarProducto(codigo: str \| None, nombre: str, precio: float, stock: int) -> bool`; `eliminar_producto(codigo: str) -> bool`; `actualizar_stock(codigo: str, cantidad: int) -> bool`; `buscarProducto(texto: str) -> list[dict[str, Any]]`; `registrar_venta(codigo: str \| None, cantidad: int \| None, cliente: str \| None = "") -> dict[str, Any] \| None`; `cotizar(codigo: str, cantidad: int \| None) -> float \| None` |
| `src/almacen.py` | `guardar_datos`, `cargar_datos` y `hay_archivo`: `(ruta: str) -> bool` |
| `src/reportes.py` | `from typing import Any`; `formatear_dinero(monto: float) -> str`; `productos_stock_bajo() -> list[dict[str, Any]]`; `reporte_inventario() -> str`; `total_vendido() -> float`; `mas_vendidos(n: int = 3) -> list[tuple[str, int]]`; `resumen_ventas() -> str` |
| `src/main.py` | `pedir_numero(mensaje: str) -> float` (los demás ya tenían `-> None` desde R8) |

Las funciones de R5 (`_calcular_descuento_volumen`, `_es_cliente_vip`, `_calcular_montos`) y los handlers de R8 ya estaban anotados y no se tocaron. Los `| None` reflejan lo que el código ya acepta (`codigo is None`, `cantidad is None`, `cliente` vacío o `None` en `_es_cliente_vip`) y los `None` de error que devuelven `registrar_venta`/`cotizar`. Valores por defecto (`cliente=""`, `n=3`) y nombres intactos. `git diff -w` solo muestra líneas `def` y los dos `import`. La firma de `registrar_venta` se partió en tres líneas para respetar los 88 caracteres; `ruff format --check src` no pide cambios.

**Justificación:** sin anotaciones había que leer el cuerpo para saber, por ejemplo, que `registrar_venta` devuelve un dict o `None`, o que `mas_vendidos` devuelve pares `(codigo, unidades)`. Con type hints la firma documenta el contrato y un analizador estático puede detectar llamadas incorrectas. Las anotaciones no se evalúan al ejecutar ni cambian el resultado, así que el comportamiento observable es idéntico.

**pytest:** 20 passed.
**ruff check src:** 0 → 0 (`All checks passed!`; la configuración no activa reglas ANN, así que el conteo no cambia).

**Mi observación:** Por la regla de CLAUDE.md v3 (riesgo bajo), Claude aplicó sin esperar aprobación. Revisé que el cambio solo agrega anotaciones: según su reporte, `git diff -w` solo muestra líneas `def` y los dos `import`, y pytest y ruff siguen en 20 passed y 0 errores. Lo acepto.


## 6. Ajustes a CLAUDE.md

### 6.1 v0 — generado con `/init`

Respuesta de Claude Code:

> Creé CLAUDE.md, en español como el resto del proyecto. Antes de escribirlo corrí las pruebas y el linter: los 20 tests pasan y ruff check src reporta 20 errores.
>
> Qué contiene: Comandos (usan tu venv/, no el .venv que dice el README, e incluyen cómo correr un solo test). Reglas del reto: no tocar tests/ ni pyproject.toml; el comportamiento debe quedar idéntico; se conservan agregarProducto y buscarProducto; un commit por refactorización documentado en docs/bitacora.md; docs/logs/ no se lee. Arquitectura: gestor.py guarda el estado global, y almacen.py y reportes.py lo modifican a través de gestor.X; si renombras contadorVentas (N816) también hay que cambiar almacen.py. Comportamientos fáciles de romper: el VIP solo se aplica en registrar_venta; los redondeos de venta y cotización deben dar el mismo total; el orden de las validaciones decide el mensaje de ultimo_error; al reemplazar la burbuja con sorted, los empates deben seguir en el mismo orden; los reportes imprimen y devuelven el texto. Código muerto ya identificado: calcular_descuento_viejo, exportar_txt y reporteViejoCSV.
>
> Un dato para la bitácora: tu sección 2.3 dice 23 errores de ruff, pero hoy da 20.

- Corregí la sección 2.3 a 20 errores. Versión guardada: [claude-md-v0.md](logs/claude-md-v0.md).

### 6.2 v1 — reescritura estructurada


```
<contexto>Reto: refactorizar este proyecto sin cambiar su comportamiento observable.</contexto>
<tarea>Reescribe CLAUDE.md con estas secciones: Propósito; Comandos (activar venv en Windows cmd con venv\Scripts\activate, pytest, ruff check src, cd src && python main.py); Convenciones (PEP 8, snake_case, type hints, constantes en MAYÚSCULAS, con un ejemplo corto antes/después); Restricciones; Flujo de verificación; Formato de respuesta.</tarea>
<restricciones>
- NUNCA modificar tests/ ni pyproject.toml.
- Conservar los nombres agregarProducto y buscarProducto.
- Salida de consola y formato JSON idénticos.
- Un refactor a la vez; no usar ruff --fix salvo que lo pida.
- Si un test falla, se corrige el código, nunca el test.
- Solo edita CLAUDE.md, máximo ~80 líneas.
- No inventes comandos que no estén en README.md o pyproject.toml.
</restricciones>
<formato>Antes de editar código: plan breve, archivos afectados, y esperar mi aprobación.</formato>
<verificacion>Al terminar, indica qué tomaste de README.md y de pyproject.toml.</verificacion>
```

- **Problema identificado:** perdió contexto importante de la v0: arquitectura, detalles de comportamiento fáciles de romper y código muerto ya identificado. Fue porque la instrucción decía "reescribe" en lugar de "integra". Versión guardada: [claude-md-v1.md](logs/claude-md-v1.md).

### 6.3 v2 — primer intento (fallido)

```
<tarea>Reincorpora a CLAUDE.md, Arquitectura, Detalles de comportamiento fáciles de romper y Código muerto del archivo [docs\logs\claude-md-v0.md] que fueron reemplazados en el prompt anterior</tarea>
<restricciones>
- No elimines secciones existentes
- Solo edita CLAUDE.md, máximo ~80 líneas.
</restricciones>
<verificacion>Al terminar, indica qué tomaste de [docs\logs\claude-md-v0.md]</verificacion>
```

- **No se ejecutó:** mi propia regla `deny` sobre `docs/logs/` impedía que Claude leyera la fuente. Además, el límite de ~80 líneas obligaba a recortar otras secciones.

### 6.4 v2 — prompt corregido (fuente pegada en el prompt)

```
<contexto>CLAUDE.md perdió estas secciones del borrador generado por /init. Te las pego literal abajo.</contexto>
<fuente>

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

</fuente>
<tarea>Integra esas tres secciones en CLAUDE.md, después de "Convenciones" y antes de "Restricciones". En "Código muerto" agrega la nota: "No eliminar hasta que se solicite en un refactor específico".</tarea>
<restricciones>
- No elimines ni modifiques las secciones existentes.
- Solo edita CLAUDE.md; máximo ~120 líneas (condensa la fuente si hace falta, sin perder datos).
</restricciones>
<verificacion>Al terminar, dime qué incluiste, qué condensaste, el número total de líneas, y confirma que Restricciones quedó idéntica.</verificacion>
```

Respuesta de Claude Code (resumen):

> Integré las tres secciones entre "Convenciones" y "Restricciones". El archivo quedó en 115 líneas y solo edité ese archivo. Condensé solo la redacción, sin perder datos; todos los nombres, porcentajes, umbrales, fórmulas y claves de diccionario quedaron igual. Restricciones quedó idéntica palabra por palabra. Ahora hay información repetida: los dos últimos puntos de "Restricciones" repiten datos de "Arquitectura" y "Detalles". No los toqué porque pediste no modificar las secciones existentes.

- Claude identificó la información repetida y **no la tocó** porque mi restricción lo prohibía: evidencia de que las restricciones negativas funcionan. Decidí dejar la duplicación.
- Versión guardada: [claude-md-v2.md](logs/claude-md-v2.md). Commit: `9ace35b`.

### 6.5 v3 — regla de aprobación por riesgo

Motivo: en R2 Claude se saltó el plan previo porque interpretó la autorización del prompt como aprobación; la instrucción de CLAUDE.md era ambigua.

```
<tarea>En CLAUDE.md, sección "Formato de respuesta", aclara la regla de aprobación: para refactors de riesgo bajo (cambios mecánicos, código muerto, constantes, renombrados, type hints) aplica directamente si el prompt lo autoriza; para refactors de riesgo medio/alto (cálculo de precios, dividir registrar_venta, dividir menu) presenta siempre el plan y espera aprobación.</tarea>
<restricciones>Solo edita esa sección. No toques nada más.</restricciones>
<verificacion>Muéstrame la sección antes y después.</verificacion>
```

- Versión guardada: [claude-md-v3.md](logs/claude-md-v3.md). Commit: `463e386`.
- **Validación:** en R3 y R9 (riesgo bajo) Claude mostró el plan y aplicó sin esperar; en R5 y R8 (riesgo alto) presentó el plan y esperó mi aprobación, tal como define la nueva regla.

## 7. Logs y evidencias


### Logs (`docs/logs/`)

- [00-baseline-pytest.txt](logs/00-baseline-pytest.txt)
- [00-baseline-ruff.txt](logs/00-baseline-ruff.txt)
- [01-exploracion-inventario.txt](logs/01-exploracion-inventario.txt)
- [C0-respuesta-claude-code.txt](logs/C0-respuesta-claude-code.txt)
- [R3-variante-A.txt](logs/R3-variante-A.txt)
- [claude-md-v0.md](logs/claude-md-v0.md)
- [claude-md-v1.md](logs/claude-md-v1.md)
- [claude-md-v2.md](logs/claude-md-v2.md)
- [claude-md-v3.md](logs/claude-md-v3.md)
- [99-final-pytest.txt](logs/99-final-pytest.txt)
- [99-final-ruff.txt](logs/99-final-ruff.txt)

### Evidencias (`docs/evidencias/`)

- [permisssions_inicio_con_claude_code.png](evidencias/permisssions_inicio_con_claude_code.png)
- [1_config-deny-docs-logs.png](evidencias/1_config-deny-docs-logs.png)
- [2_config-deny-docs-logs.png](evidencias/2_config-deny-docs-logs.png)
- [modo_manual_activo_claude_pregunta.png](evidencias/modo_manual_activo_claude_pregunta.png)
- [chore_autofixes_ruff_prompt_ejecucion.png](evidencias/chore_autofixes_ruff_prompt_ejecucion.png)
- [R1-plan-trabajo-Claude-espera-confirmacion.png](evidencias/R1-plan-trabajo-Claude-espera-confirmacion.png)
- [R1-prueba_funciona_main_despues_de_cambio.png](evidencias/R1-prueba_funciona_main_despues_de_cambio.png)
- [R2-ejecucion_de_plan_sin-espera-confirmacion.png](evidencias/R2-ejecucion_de_plan_sin-espera-confirmacion.png)
- [R3_A_1_pide_permiso_p_run_test_ruff.png](evidencias/R3_A_1_pide_permiso_p_run_test_ruff.png)
- [R3_A_2_trabajando.png](evidencias/R3_A_2_trabajando.png)

### Commits de la rama `refactorizacion`

| Commit | Contenido |
|---|---|
| `d4f3895` | Línea base (en `main`) |
| `e891556` | Configuración de Claude Code |
| `9ace35b` | CLAUDE.md v2 |
| `f8fd062` | chore: autofixes de ruff (20 → 13) |
| `7f69aab` | R1 (13 → 9) |
| `8811c39` | R2 (9 → 7) |
| `463e386` | CLAUDE.md v3 |
| `d229e84` | R3 (7 → 7) |
| `553b94d` | R4 (7 → 5) |
| `4277244` | R5 (5 → 1) |
| `c2f6098` | R8 (1 → 0) |
| `de3f704` | R9 (0 → 0) |

## 8. Reflexión final

Ver [reflexion.md](reflexion.md).
