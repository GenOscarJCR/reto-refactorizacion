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
- ruff check src: 23 errores (UP009 x4, SIM102 x3, SIM115 x3, C901 x2, N802 x2,
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
'{
  "permissions": {
    "deny": [
      "Read(./venv/**)", "Read(./.venv/**)",
      "Read(./**/__pycache__/**)", "Read(./.pytest_cache/**)",
      "Read(./.ruff_cache/**)", "Read(./docs/logs/**)",
      "Read(./src/datos_ejemplo.json)",
      "Edit(./tests/**)", "Edit(./pyproject.toml)"
    ]
  }
}'

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

## 4. Resumen


| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  |              |                  |               |          |
| 2  |              |                  |               |          |
| 3  |              |                  |               |          |
| 4  |              |                  |               |          |
| 5  |              |                  |               |          |

> Agrega más filas si realizas más de 5 refactorizaciones.

## 5. Detalle por refactor

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

"<contexto>Reto: refactorizar este proyecto sin cambiar su comportamiento observable.</contexto>
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

Problemas identificados con este Prompt: "Perdio parte del contexto de importancia de la primer versión de CLAUDE.md, como es; arquitectura, detalles de comportamiento fáciles de romper y código muerto ya identificado", esto fue debido a que en la instrucción del prompt dice "reescribe" en lugar de decirle "integra". Realizare otro prompt para pedirle que recupere lo perdido.

El siguiente es el Prompt para tratar de resolver la perdida anterior:

"<tarea>Reincorpora a CLAUDE.md, Arquitectura, Detalles de comportamiento fáciles de romper y Código muerto del archivo [docs\logs\claude-md-v0.md] que fueron reemplazados en el prompt anterior</tarea>
<restricciones> 
- No elimines secciones existentes
- Solo edita CLAUDE.md, máximo ~80 líneas.
</restricciones>
<verificacion>Al terminar, indica qué tomaste de [docs\logs\claude-md-v0.md]</verificacion>"

Sin embargo hay propiamente restricciones de lectura, por consiguiente no se podria ejecutar. 

El siguiente Prompt es el que mande para la corrección con fix con ayuda de Claude. 

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
"
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



## Reflexión final (10-15 líneas)
Ver [reflexion.md]