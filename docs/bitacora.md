# Bitácora de refactorización

**Nombre:** OSCAR JOSUÉ CORONILLA RANGEL
**Matrícula:** ocoronilla@gasen.mx
**Fecha:** 05-Octubre-2026

## 1. Contexto del reto

Objetivos del reto:
Aplicar Claude Code como herramienta de desarrollo para mejorar código existente de forma sistemática, demostrando dominio de prompt engineering y flujos de trabajo efectivos con IA.

## 2. Configuración

### 2.1 Preparación del repositorio
- El proyecto llegó como .zip con carpeta doble y basura de macOS (__MACOSX, .DS_Store).
- Moví la carpeta interior a C:\Proyectos\ProyectosAprendizaje\reto-refactorizacion.
- git init; commit de línea base en main: d4f3895 "Línea base: proyecto original sin cambios (20 tests pasan)".
- Rama de trabajo: refactorizacion (PR hacia main de mi repo).

### 2.2 Entorno
- Windows + Cmder (cmd), Python 3.11.4.
- python -m venv venv → venv\Scripts\activate → pip install -r requirements.txt
- Nota: el README usa .venv y yo usé venv; ambos están en .gitignore y .claudeignore.

### 2.3 Línea base (antes de tocar código)
- pytest: 20 passed in 0.18s → docs/logs/00-baseline-pytest.txt
- ruff check src: 20 errores (UP009 x4, SIM102 x3, SIM115 x3, C901 x2, N802 x2,
  SIM108, N816, SIM103, UP015, I001, F401); 7 autocorregibles → docs/logs/00-baseline-ruff.txt


### 2.4 Investigación N802 (evidencia, no suposición)
- agregarProducto y buscarProducto NO aparecen: pyproject.toml ya los cubre con ignore-names → no hace falta # noqa.
- hayArchivo: solo se usa en src\main.py:23 y no la usa ningún test → se renombra (y se actualiza ese llamado).
- reporteViejoCSV: solo existe su definición (findstr sobre src y tests) → código muerto, se elimina.

### 2.5 .gitignore
| Entrada | Por qué |
|---|---|
|venv/ |se ignoran estas carpetas para limitar el tamaño y además las dependencias se colocan en el archivo requirements.txt|
|.venv/|se ignoran estas carpetas para limitar el tamaño y además las dependencias se colocan en el archivo requirements.txt|
'Archivos de caché de Python y pruebas'
|__pycache__/|Son archivos autogenerados que sirven solo en la compilación local para que inicie más rápido. Es bytecode .pyc que Python regenera solo, no es código fuente|
|.pytest_cache/|Son archivos autogenerados que sirven solo en la compilación local para que inicie más rápido. Es bytecode .pyc que Python regenera solo, no es código fuente|
|.ruff_cache/|carpetas generadas automáticamente por Ruff, un formateador y analizador de código (linter) extremadamente rápido para el lenguaje de programación Python|
|src/datos_ejemplo.json|Archivo generado al correr el main.py dentro de src|
'Archivos del sistema operativo (macOS)'
|.DS_Store |Archivos basura que venían  en el zip de descarga|
|__MACOSX/ |Archivos basura que venían  en el zip de descarga|


### 2.6 .claudeignore
| Entrada | Por qué |
|---|---|
| venv/, .venv/|Son archivos pesados de las dependencias que consumirían tokens sin razón necesaria|
| __pycache__/, *.pyc, .pytest_cache/, .ruff_cache/ |Son archivos autogenerados que sirven solo en la compilación local para que inicie más rápido. Es bytecode .pyc que Python regenera solo, no es código fuente|
| __MACOSX/, .DS_Store |Archivos basura|
| docs/logs/ |Se excluye para que Claude no tome logs viejos como el estado actual|
| src/datos_ejemplo.json |Archivos generados en la ejecución de prueba|

'La o las razones principales, es que si se cargan esos archivos consumen token's en el contexto que no sirve de nada y la otra razón es que algunos archivos pueden contener KEY's relevantes o usuarios y contraseñas. Para este caso no hay guarda de secretos, se especifica como medidas de prevención.'

- Decisión: NO excluyo tests/, porque Claude debe leerlos como contrato de comportamiento.
- Revisando la documentación de Claude en la sección de settings no hay referencia alguna de que Claude Code respete .claudeignore de forma nativa. 
 

### 2.7 Decisiones de entrega
- La bitácora va en docs/bitacora.md (el formato de entrega manda sobre el README, que dice BITACORA.md).

### 2.8 Permisos y modos de Claude Code
```
settings.json
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

- Prueda directa para validar .claudeignore: 
    1. Hice la siguiente petición a Claude "Muestra el contenido de docs/logs/00-baseline-pytest.txt"
    2. Claude contesto: 
        "No pude mostrar el archivo. La configuración de permisos de este proyecto bloquea la lectura de docs/logs/00-baseline-pytest.txt: el directorio
        aparece como denegado. No intenté leerlo por otra vía (como cat en la terminal) para no saltarme esa regla. La regla probablemente está en tu .claude/settings.json o en .claudeignore, ambos sin rastrear en git."
    3. Quite la regla de deny en el archivo settings.json "Read(./docs/logs/**)" y guarde
    4. Abri un nuevo chat y le pedi lo mismo a Claude: "Muestra el contenido de docs/logs/00-baseline-pytest.txt"
    5. Claude me contesto: "Este es el contenido de docs/logs/00-baseline-pytest.txt:" y me mostro el archivo
    6. Se regreso la regla a archivo settings.json

    Conclusión: Claude no respeta .claudeignore, en la primera prueba mismo Claude respondio lo siguiente "La regla probablemente está en tu .claude/settings.json o en .claudeignore..." aunque identifica que existe .claudeignore realmente toma las reglas de settings.json. 
 - Evidencias docs\evidencias\1_config-deny-docs-logs.png y docs\evidencias\2_config-deny-docs-logs.png

 - Se cambia el modo de Claude de Auto a Manual; para tener un control de lo que esta pasando, es decir, Claude pregunta antes de realizar alguna acción que pudiese ser peligrosa o esta fuera de los permisos asignados. 

 - [refactorizacion e891556] chore: configuracion de Claude Code (.claudeignore, permissions.deny, logs de linea base) - 20 passed


## 3. Exploración

- Contexto: /clear al iniciar la fase. Modo: Plan (solo lectura).

### 3.1 Prompt

Prompt

```
<contexto>Fase de exploración. No modifiques nada. Línea base de ruff: UP009 x4, SIM102 x3, SIM115 x3, C901 x2, N802 x2, SIM108, N816, SIM103, UP015, I001, F401.</contexto>
<tarea>Lee src/ y tests/ e inventaría los code smells en una tabla: ID (S1..), categoría, archivo:función, evidencia (1 línea), códigos ruff relacionados, refactor propuesto, riesgo para tests/comportamientos frágiles.</tarea>
<restricciones>No edites archivos ni ejecutes comandos. No propongas cambios a tests/ ni pyproject.toml.</restricciones>
<cobertura>Verifica cada categoría del README: funciones gigantes, duplicación, nombres crípticos, números mágicos, estado global, código muerto, anidamiento excesivo, nombrado mixto. Si no encuentras alguna, dilo. Lista los códigos ruff que no mapeaste.</cobertura>
<formato>Después de la tabla, agrupa los smells en ≥5 refactors atómicos ordenados de menor a mayor riesgo, justificando el orden.</formato>
```
### 3.2 Respuesta de Claude Code (resumen)

Encontré 27 smells (S1–S27). Las 8 categorías del README aparecen en el código: funciones gigantes, duplicación, nombres crípticos, números mágicos, estado global, código muerto, anidamiento excesivo y nombrado mixto.
Los 20 errores de la línea base de ruff corresponden a smells concretos.

Refactors atómicos, de menor a mayor riesgo (en cada paso, pytest debe dar 20 passed)

[Inventario completo](logs/01-exploracion-inventario.txt)

### 3.3 Plan propuesto por Claude

```
#	Refactor	Errores de ruff que quita
R1	Cabeceras e imports	6
R2	with en almacen.py y hay_archivo	5
R3	Eliminar código muerto	2
R4	Constantes y renombrados (contador_ventas, formatear_dinero)	1
R5	Simplificar reportes.py (sorted estable, helper de stock bajo)	0
R6	Función de precios común con VIP explícito	4
R7	Dividir registrar_venta	1
R8	Dividir menu	1
```

Con los ocho, ruff baja de 20 a 0.

R3 solo se aplica si lo pides explícitamente, como exige CLAUDE.md.
R6 y R7 tocan las reglas más frágiles: el VIP que solo aplica a ventas, los redondeos, que cotizar coincida con el total de la venta y el orden de los mensajes de ultimo_error.
R8 va al final porque main.py no tiene tests; habrá que comparar la salida de la consola a mano.

El estado global (S24) se puede mitigar, pero no eliminar sin romper la API que usan los tests.

### 3.4 Mi revisión y ajustes al plan

Ajusto el plan de Claude según el README. Cabeceras, imports y el "r" redundante son autofixes de ruff, así que van en un commit chore que no cuenta como refactor. Divido "constantes y renombrados" en dos commits para que cada diff sea revisable. Agrego type hints, que el README marca como refactor válido y el plan de Claude no incluía.

### 3.5 Plan final

Plan ajustado: C0 chore (20 → 13) · R1 with + hay_archivo · R2 código muerto · R3 constantes · R4 renombrados · R5 reportes · R6 precios comunes + VIP · R7 dividir registrar_venta · R8 dividir menu · R9 type hints.

### 3.6 Observaciones del proceso

Al terminar, el modo Plan pidió aprobar y ejecutar todo el plan. No lo acepté: cada refactor se ejecuta por separado, con su propio prompt y su verificación.

- Detecté que plan-refactor.md tenía la numeración original de Claude y no coincidía con mis prompts. Agregué el plan final al inicio del archivo para evitar que Claude confundiera los refactors.

## 4. Resumen

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | R1 — with en persistencia y hay\_archivo (ver 5. R1) | `almacen.py`: `with open(...)` en `guardar_datos`/`cargar_datos`; `hayArchivo` → `hay_archivo` con `return os.path.exists(ruta)`; `main.py` actualizado | Cierre de archivos garantizado; nombre PEP 8; quita if/else redundante. Ruff 13 → 9 (SIM115 x2, N802, SIM103) | 20 passed |
| 2  | R2 — eliminar código muerto (ver 5. R2) | `gestor.py`: eliminados `MODO_DEBUG`, `calcular_descuento_viejo` y el bloque comentado `exportar_txt`; `reportes.py`: eliminada `reporteViejoCSV` | Código sin referencias en `src/` ni `tests/` (verificado con búsqueda); menos ruido y mantenimiento. Ruff 9 → 7 (N802, SIM115) | 20 passed |
| 3  | R3 — constantes con nombre (ver 5. R3) | `gestor.py`: constantes `UMBRAL_DESCUENTO_ALTO/MEDIO`, `TASA_DESCUENTO_ALTO/MEDIO`, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_EXTRA_VIP`, `TASA_IVA` en `registrar_venta` y `cotizar`; `reportes.py`: `STOCK_MINIMO` en `productos_stock_bajo` y `reporte_inventario` | Reglas de negocio con nombre y en un solo lugar; mismos valores numéricos. Ruff 7 → 7 (no hay regla activa para números mágicos) | 20 passed |
| 4  | R4 — renombrados claros (ver 5. R4) | `gestor.py`: `contadorVentas` → `contador_ventas` y locales (`x`, `aux`, `temp2`, `desc`, `t`, `k`) con nombres descriptivos; `reportes.py`: `hacer_cosa` → `formatear_dinero` y locales (`s`, `t`, `aux`, `temp`, `p`, `k`, `v`); `almacen.py`: referencias a `contador_ventas` y locales (`d`, `f`, `k`, `v`) | Nombres que dicen qué guardan; `contador_ventas` sigue PEP 8. Claves de dicts/JSON intactas. Ruff 7 → 5 (N816; SIM108 deja de reportarse porque el ternario ya no cabe en 88 caracteres) | 20 passed |
| 5  |              |                  |               |          |

> Agrega más filas si realizas más de 5 refactorizaciones.

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

**Mi observacion** Claude revisó el diff con --fix --diff antes de aplicar y no usó --unsafe-fixes. Los 7 arreglos no tocan la lógica. Lo acepto. Nota: el commit incluyó también mis cambios previos a la bitácora (secciones 2 a 3.6)

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


**Mi observacion** Claude propuso type hints fuera de alcance; los rechacé para mantener el refactor atómico, porque van en R9. También detectó la doble numeración en plan-refactor.md y eligió la del plan final.

Sin type hints, como pedí. Claude verificó a mano los casos de archivo corrupto e inexistente, que no tienen test; ambos devuelven lo mismo que antes. Lo acepto.

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

**Mi observacion** Claude confirmó con búsqueda que no había referencias antes y después de borrar. Se saltó el plan previo de CLAUDE.md por interpretar mi autorización como aprobación. Lo acepto, y aclaro la regla en CLAUDE.md v3.

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

**Justificación:** los literales 1000, 0.10, 500, 0.05, 200, 0.02, 0.16 y 5 son reglas de negocio sin nombre y estaban duplicados entre `registrar_venta`/`cotizar` y entre dos funciones de `reportes.py`; si cambiara el IVA o un umbral habría que encontrar cada copia. Con constantes, la regla se lee por su nombre y se cambia en un solo lugar. Los valores son exactamente los mismos (mismos `float`), así que los cálculos y redondeos no cambian. `PREFIJO_VIP` con `len(PREFIJO_VIP)` = 3 conserva la comprobación original. Además, deja listas las constantes que usará la función común de precios (R6).

**pytest:** 20 passed.
**ruff check src:** 7 → 7 (sin cambio esperado: los números mágicos no tienen regla activa en la configuración de ruff; quedan N816, C901 x2, SIM108, SIM102 x3).

**Mi observacion** 

"Comparación de variantes":

- Variante A (Prompt de 1 línea "Reemplaza los números mágicos por constantes."): Claude hizo el ciclo completo (tests, ruff, bitácora y commit "R3: constantes con nombre"), tocando gestor.py y reportes.py. Lo atribuyo al contexto persistente: CLAUDE.md, plan-refactor.md y el historial de commits.

Variante B (Prompt estructurado): Nuevamente Claude hizo el ciclo completo de acuerdo a la estructura del Prompt
Conclusión: En defitiva creo que en la variante A Claude toma el conocimiento del contexto en cada prompt solo he limpieado la pantalla con /clear no he abierto otro chat. 
Hice un git reset --hard y el commit se queda con la variante B y en logs de evidencia se encuentra el commit de la variante A (6cc4585)

- Mismos valores en las constantes; cotizar sigue sin VIP. El helper de S7 quedó pendiente porque Claude usó la numeración original del plan; lo muevo a R7.

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



## 6. Ajustes a CLAUDE.md

/init

Ejecutado 4 comandos, creado CLAUDE.md
Creé CLAUDE.md, en español como el resto del proyecto. Antes de escribirlo corrí las pruebas y el linter: los 20 tests pasan y ruff check src reporta 20 errores.

Qué contiene:

Comandos: usan tu venv/ (no el .venv que dice el README) e incluyen cómo correr un solo test.
Reglas del reto:
No tocar tests/ ni pyproject.toml.
El comportamiento debe quedar idéntico.
Se conservan los nombres agregarProducto y buscarProducto.
Un commit por refactorización, cada uno documentado en docs/bitacora.md.
docs/logs/ no se lee.
Arquitectura: gestor.py guarda el estado global, y almacen.py y reportes.py lo modifican a través de gestor.X. Por eso, si renombras contadorVentas para corregir el error N816 de ruff, también hay que cambiar almacen.py.
Comportamientos fáciles de romper:
El descuento VIP solo se aplica en registrar_venta, no en cotizar.
Los redondeos de una venta y de una cotización deben dar el mismo total.
El orden de las validaciones decide qué mensaje queda en ultimo_error.
Al reemplazar el ordenamiento de burbuja con sorted, los empates deben seguir en el mismo orden.
Los reportes imprimen el texto y además lo devuelven.
Código muerto ya identificado: calcular_descuento_viejo, el bloque comentado exportar_txt y reporteViejoCSV.
Un dato para la bitácora: tu sección 2.3 dice 23 errores de ruff, pero hoy da 20. Conviene revisar cuál es el número correcto de la línea base.

1er. Prompt: 

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
<verificacion>Al terminar, indica qué tomaste de README.md y de pyproject.toml.</verificacion>"
```

Problemas identificados con este Prompt: "Perdio parte del contexto de importancia de la primer versión de CLAUDE.md, como es; arquitectura, detalles de comportamiento fáciles de romper y código muerto ya identificado", esto fue debido a que en la instrucción del prompt dice "reescribe" en lugar de decirle "integra". Realizare otro prompt para pedirle que recupere lo perdido.

El siguiente es el Prompt para tratar de resolver la perdida anterior:

```
<tarea>Reincorpora a CLAUDE.md, Arquitectura, Detalles de comportamiento fáciles de romper y Código muerto del archivo [docs\logs\claude-md-v0.md] que fueron reemplazados en el prompt anterior</tarea>
<restricciones> 
- No elimines secciones existentes
- Solo edita CLAUDE.md, máximo ~80 líneas.
</restricciones>
<verificacion>Al terminar, indica qué tomaste de [docs\logs\claude-md-v0.md]</verificacion>"
```

Sin embargo hay propiamente restricciones de lectura, por consiguiente no se podria ejecutar. 

El siguiente Prompt es el que mande para la corrección con fix con ayuda de Claude. 

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

Respuesta después del Prompt:

"Integré las tres secciones en CLAUDE.md, entre "Convenciones" y "Restricciones". El archivo quedó en 115 líneas y solo edité ese archivo.

Qué incluí:

Arquitectura: cómo se importan los módulos y quién es dueño del estado global. También que almacen.py reasigna contadorVentas y ultimo_error, y qué nombres y claves de diccionarios usan los tests.
Detalles de comportamiento fáciles de romper: los siete puntos de la fuente (precios, VIP, redondeo, orden de validación, línea "Descuento" del ticket, orden estable de mas_vendidos, reportes que imprimen y devuelven el texto).
Código muerto ya identificado: los cuatro elementos de la fuente, más la nota "No eliminar hasta que se solicite en un refactor específico." en negritas.

Qué condensé: solo la redacción, sin perder datos. Por ejemplo:

"importan de forma plana" → "importados de forma plana".
"leen y escriben ese estado a través de gestor.X" → "leen/escriben ese estado vía gestor.X".
"Hay un test que exige" → "Un test exige".
"determina qué mensaje queda en" → "fija el mensaje de".

Todos los nombres, porcentajes, umbrales, fórmulas y claves de diccionario quedaron igual.

Restricciones quedó idéntica: la imprimí completa después de editar y coincide palabra por palabra con la versión anterior. Propósito, Comandos, Convenciones, Flujo de verificación y Formato de respuesta tampoco cambiaron, porque la única edición fue insertar texto justo antes del título ## Restricciones.

Ahora hay información repetida: los dos últimos puntos de "Restricciones" repiten datos que ya están en "Arquitectura" y en "Detalles". No los toqué porque pediste no modificar las secciones existentes."

Esta identificando que hay información repetida por la solicitud de no modificar lo que ya existe.

**Validación** La variante B de R3 quedó bien, y además confirma que CLAUDE.md v3 funcionó: Claude clasificó R3 como de riesgo bajo, mostró el plan y lo aplicó sin esperar, tal como define la nueva regla


## Reflexión final (10-15 líneas)
Ver [reflexion.md]