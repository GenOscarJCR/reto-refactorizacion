# Bitácora de refactorización

**Nombre:*OSCAR JOSUÉ CORONILLA RANGEL*
**Matrícula:*ocoronilla@gasen.mx*
**Fecha:*05-Octubre-2026*

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
# Entornos virtuales
venv/   <se ignoran estas carpetas para limitar el tamaño y además las dependencias se colocan en el archivo requeriments.txt>
.venv/

# Archivos de caché de Python y pruebas
__pycache__/         <Son archivos autogenerados que sirven solo en la cmpilación local para que incie más rápido>
.pytest_cache/
.ruff_cache/
src/datos_ejemplo.json  <Archivo generado al correr el main.py dentro de src>

# Archivos del sistema operativo (macOS)
.DS_Store    <Archivos basura que venian en el zip de descarga>
__MACOSX/


### 2.6 .claudeignore
| Entrada | Por qué |
|---|---|
| venv/, .venv/
| __pycache__/, *.pyc, .pytest_cache/, .ruff_cache/ 
| __MACOSX/, .DS_Store 
| docs/logs/ 
| src/datos_ejemplo.json 

<La o las razones principales, es que si se cargan esos archivos consumen token's en el contexto que no sirve de nada y la otra razón es que algunos archivos pueden contener KEY's relevantes o usuarios y contraseñas.>

- Decisión: NO excluyo tests/, porque Claude debe leerlos como contrato de comportamiento.
- Pendiente: verificar en la documentación si Claude Code respeta .claudeignore de forma nativa.

### 2.7 Decisiones de entrega
- La bitácora va en docs/bitacora.md (el formato de entrega manda sobre el README, que dice BITACORA.md).



Registra aquí **cada refactorización** que realices con Claude Code. Copia el
prompt tal cual lo escribiste (o un resumen fiel si fue una conversación larga),
describe el cambio que se aplicó al código y justifica por qué mejora la calidad.
Después de cada cambio ejecuta `pytest` y anota el resultado.

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  |              |                  |               |          |
| 2  |              |                  |               |          |
| 3  |              |                  |               |          |
| 4  |              |                  |               |          |
| 5  |              |                  |               |          |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

*(Escribe aquí tu reflexión)*
