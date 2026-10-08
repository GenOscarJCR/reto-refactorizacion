\# PLAN FINAL VIGENTE (usar esta numeración)

La sección "Refactors atómicos" más abajo es la propuesta original de Claude: NO usar su numeración.



| ID | Refactor | Smells | Equivale en propuesta original |

|---|---|---|---|

| chore | Autofixes de ruff (no cuenta) | S21, S22, S23, UP015 | R1 + UP015 de R2 |

| R1 | with en persistencia + hay\_archivo | S15, S18, S19 | R2 |

| R2 | Eliminar código muerto | S16, S20 | R3 |

| R3 | Constantes con nombre | S7, S10, S11 | parte de R4 y R5 |

| R4 | Renombrados claros | S12, S13, S14 | parte de R4 |

| R5 | Cálculo de precios común + VIP | S4, S5, S6 | R6 |

| R6 | Dividir registrar\_venta | S1, S3, S9, S26 | R7 |

| R7 | Simplificar reportes | S8, S25 | parte de R5 |

| R8 | Dividir menu | S2 | R8 |

| R9 | Type hints | — | nuevo |



\---



Inventario de code smells — "La Esquina" (fase de exploración)
Contexto

Fase de diagnóstico del reto: inventariar los smells de src/ (leídos junto con tests/), mapearlos a la línea base de ruff (20 errores) y proponer una secuencia de refactors atómicos. No se modificó ningún archivo ni se ejecutó ningún comando.

Tabla de smells
ID	Categoría	Archivo:función	Evidencia	Ruff	Refactor propuesto	Riesgo / frágiles
S1	Función gigante	gestor.py:registrar\_venta (86-161)	Valida, calcula precios, mueve stock, crea folio, arma ticket y guarda: \~75 líneas	C901	Extraer \_validar\_venta, \_calcular\_precios, \_armar\_ticket; dejar orquestador	Alto: orden de validación fija ultimo\_error; venta fallida no toca stock/VENTAS; ticket con "Descuento" solo si > 0
S2	Función gigante	main.py:menu (21-82)	if/elif de 8 opciones + I/O y lógica en un solo bloque	C901	Un handler por opción + dict de despacho	Medio-alto: sin tests; textos de consola deben quedar idénticos (verificación manual)
S3	Anidamiento excesivo	gestor.py:registrar\_venta (96-112)	Pirámide de 4 if/else para validar	—	Guard clauses con return None temprano en el mismo orden	Alto: mismo orden de mensajes (vacío → no existe → cantidad → stock)
S4	Anidamiento excesivo	gestor.py:registrar\_venta (126-130)	4 if anidados para VIP	SIM102 x3	cliente and cliente.startswith("VIP") and base > UMBRAL\_VIP	Medio: VIP compara monto ya con descuento > 200 y suma 2 % del subtotal; None/"" no deben fallar
S5	Anidamiento / simplificable	gestor.py:registrar\_venta (117-123) y cotizar (175-179)	else: if aux >= 500 + else: desc = 0 redundante	SIM108 (l.120)	if/elif/else en función de descuento única	Bajo-medio: límites >= 1000 / 500
S6	Duplicación	gestor.py:registrar\_venta / cotizar	Mismo cálculo de descuento por volumen e IVA copiado	—	\_calcular\_montos(subtotal, cliente=None, aplica\_vip=False) común	Alto: cotizar NO aplica VIP; redondeos: venta redondea subtotal/desc/IVA por separado y total=round(base+imp,2); test exige cotizar == total
S7	Duplicación	reportes.py:productos\_stock\_bajo / reporte\_inventario	stock < 5 repetido	—	Constante STOCK\_MINIMO + helper \_es\_stock\_bajo(p)	Bajo
S8	Duplicación	reportes.py:resumen\_ventas vs total\_vendido	Ambas suman v\["total"]	—	Reutilizar total\_vendido()	Bajo: hacer\_cosa vuelve a redondear (resultado idéntico)
S9	Duplicación	gestor.py (5 funciones)	ultimo\_error = "..."; return False/None repetido con global	—	Helper \_fallar(msg, valor)	Medio: mismos textos de error
S10	Números mágicos	gestor.py:registrar\_venta, cotizar	1000, 0.10, 500, 0.05, 200, 0.02, 0.16, 3, "VIP"	—	Constantes UMBRAL\_DESCUENTO\_ALTO, TASA\_IVA, PREFIJO\_VIP, etc.	Bajo: mismos valores float
S11	Números mágicos	reportes.py:productos\_stock\_bajo, reporte\_inventario	< 5	—	STOCK\_MINIMO = 5 (ver S7)	Bajo
S12	Nombres crípticos	gestor.py, reportes.py, almacen.py, main.py	x, aux, temp2, desc, t, d, f, k, s, p, c, n, cant, cli, op	—	Nombres descriptivos (producto, subtotal, resultados, datos…)	Bajo (locales); no tocar claves de dicts
S13	Nombres crípticos	reportes.py:hacer\_cosa	Nombre no dice que formatea dinero	—	formatear\_dinero (sin uso en tests)	Bajo
S14	Nombrado mixto	gestor.py global contadorVentas	camelCase en módulo snake\_case	N816	contador\_ventas; actualizar almacen.guardar/cargar\_datos	Medio: almacen lo reasigna desde fuera; clave JSON "contador" no cambia
S15	Nombrado mixto	almacen.py:hayArchivo	camelCase	N802	hay\_archivo + actualizar main.py	Bajo (sin tests)
S16	Nombrado mixto	reportes.py:reporteViejoCSV	camelCase	N802	Se resuelve eliminándola (S20)	Bajo
S17	Nombrado mixto (tolerado)	gestor.py:agregarProducto, buscarProducto	camelCase	(ignorados en pyproject)	Conservar: API de tests	—
S18	Simplificable	almacen.py:hayArchivo	if …: return True else: return False	SIM103	return os.path.exists(ruta)	Bajo
S19	Recursos sin with	almacen.py:guardar\_datos, cargar\_datos; reportes.py:reporteViejoCSV	f = open(...) + f.close() manual (2 en cargar)	SIM115 x3, UP015 ("r" redundante)	with open(ruta, encoding="utf-8") as f:	Bajo-medio: cargar\_datos debe seguir devolviendo False + "archivo corrupto"; mantener except Exception (no estrechar)
S20	Código muerto	gestor.py:calcular\_descuento\_viejo, comentario exportar\_txt; reportes.py:reporteViejoCSV; gestor.MODO\_DEBUG (sin uso)	"ya nadie la llama pero la dejamos"	(N802, SIM115 de reporteViejoCSV)	Eliminar — solo cuando se solicite (CLAUDE.md)	Bajo: sin referencias en src/ ni tests/ (verificado)
S21	Imports	reportes.py	import os sin uso	F401	Eliminar	Nulo
S22	Imports	main.py	gestor, almacen, reportes sin ordenar	I001	almacen, gestor, reportes	Nulo
S23	Sintaxis obsoleta	4 archivos de src/	# -*- coding: utf-8 -*-	UP009 x4	Eliminar cabecera	Nulo
S24	Estado global	gestor.py (módulo)	INVENTARIO, VENTAS, contadorVentas, ultimo\_error + global en 5 funciones; almacen escribe estado ajeno	—	Mitigar, no eliminar: helper de error (S9) y encapsular escritura del contador; una clase rompería la API de tests	Alto si se rediseña: tests leen gestor.INVENTARIO/VENTAS y llaman reiniciar\_sistema
S25	Ordenamiento manual	reportes.py:mas\_vendidos	Burbuja + acumulación manual en dict	—	dict.get + sorted(..., key=itemgetter(1), reverse=True)	Medio: estabilidad de empates (sorted reverse la conserva); tuplas (codigo, unidades)
S26	Construcción verbosa	gestor.py:agregarProducto, registrar\_venta; almacen.guardar\_datos	x = {}; x\["codigo"] = … y t = t + …	—	Literales de dict y f-strings / "".join	Bajo-medio: orden de claves en JSON y texto exacto del ticket
S27	Excepción amplia	almacen.py:cargar\_datos	except Exception:	(BLE no seleccionado)	Documentar; no estrechar sin pedirlo (UnicodeDecodeError es ValueError, pero OSError no)	Medio si se cambia
Cobertura de categorías del README
Funciones gigantes: sí (S1, S2).
Duplicación: sí (S6, S7, S8, S9).
Nombres crípticos: sí (S12, S13).
Números mágicos: sí (S10, S11).
Estado global: sí (S24).
Código muerto: sí (S20, S21).
Anidamiento excesivo: sí (S3, S4, S5).
Nombrado mixto: sí (S14–S17).
Mapeo de la línea base ruff (20)

UP009 x4 → S23 · SIM102 x3 → S4 · SIM115 x3 → S19 · C901 x2 → S1, S2 · N802 x2 → S15, S16 · SIM108 → S5 · N816 → S14 · SIM103 → S18 · UP015 → S19 · I001 → S22 · F401 → S21. Códigos sin mapear: ninguno.

Refactors atómicos (menor → mayor riesgo)

# Refactor	Smells	Ruff resueltos	Archivos	Riesgo

R1	Higiene de módulos: quitar coding, import os sin uso, ordenar imports	S21, S22, S23	UP009 x4, F401, I001 (6)	los 4 de src/	Nulo
R2	Context managers en persistencia + hay\_archivo simplificado	S15, S18, S19 (almacen)	SIM115 x2, UP015, N802, SIM103 (5)	almacen.py, main.py	Bajo
R3	Eliminar código muerto (requiere tu solicitud explícita)	S16, S20	N802, SIM115 (2)	gestor.py, reportes.py	Bajo
R4	Constantes con nombre + renombrar contador\_ventas, formatear\_dinero y locales crípticos	S10–S14	N816 (1)	gestor.py, reportes.py, almacen.py	Bajo-medio
R5	Simplificar reportes: helper de stock bajo, sorted estable, reutilizar total\_vendido	S7, S8, S25	—	reportes.py	Medio
R6	Extraer cálculo de precios común (VIP como opción explícita) y aplanar ifs del VIP	S4, S5, S6	SIM102 x3, SIM108 (4)	gestor.py	Medio-alto
R7	Dividir registrar\_venta: guard clauses, \_armar\_ticket, helper de error	S1, S3, S9, S26, S24 (mitigación)	C901 (1)	gestor.py	Alto
R8	Dividir menu en handlers + despacho	S2	C901 (1)	main.py	Alto (sin tests)

Total: 6+5+2+1+0+4+1+1 = 20 → ruff check src en 0.

Justificación del orden
R1–R2 son mecánicos y con cobertura (tests de almacen) o sin efecto en ejecución: bajan 11 errores sin tocar lógica.
R3 es trivial pero va aparte porque CLAUDE.md exige pedirlo explícitamente; si no se aprueba, R1–R8 siguen siendo válidos (quedarían N802 + SIM115 de reporteViejoCSV).
R4 antes que R6/R7: las constantes y nombres claros hacen que la extracción posterior sea legible y que el diff de R6/R7 muestre solo cambios de estructura, no de nombres. El rename de contadorVentas cruza módulos (almacen), por eso es medio.
R5 cambia algoritmos (burbuja → sorted) pero en un módulo aislado y con tests directos.
R6 toca la regla de negocio más frágil (VIP solo en venta, redondeos, cotizar == total); se hace antes de R7 para que el split de registrar\_venta ya parta de un cálculo correcto y testeado.
R7 reestructura el flujo con efectos (stock, folio, VENTAS, ultimo\_error).
R8 al final: no hay tests de main.py, así que requiere verificación manual de la consola.
Verificación (por cada refactor)
pytest → 20 passed.
ruff check src → conteo no sube (esperado: 20 → 14 → 9 → 7 → 6 → 6 → 2 → 1 → 0).
R8 (y R2 por hay\_archivo): ejecutar cd src \&\& python main.py y comparar salida de cada opción con la línea base.
Commit atómico en refactorizacion + fila en docs/bitacora.md.

=======================================================================================================================================================================
Respuesta directa de Claude Code:

Terminé de leer src/, tests/, README.md y pyproject.toml sin modificar nada. El inventario completo está en el archivo del plan; aquí va un resumen.

Resultado

Encontré 27 smells (S1–S27). Las 8 categorías del README aparecen en el código: funciones gigantes, duplicación, nombres crípticos, números mágicos, estado global, código muerto, anidamiento excesivo y nombrado mixto.
Los 20 errores de la línea base de ruff corresponden a smells concretos. No quedó ningún código sin mapear:
UP009 ×4: cabeceras coding de los 4 archivos.
SIM102 ×3: los if anidados del VIP en registrar\_venta.
SIM108: gestor.py:120.
SIM115 ×3: dos en almacen.py y uno en reporteViejoCSV.
C901 ×2: registrar\_venta y menu.
N802 ×2: hayArchivo y reporteViejoCSV.
N816: contadorVentas.
SIM103: hayArchivo.
UP015: el "r" redundante en cargar\_datos.
I001: el orden de imports en main.py.
F401: import os en reportes.py.
Hay smells que ruff no detecta: el cálculo de precios duplicado, el umbral < 5 repetido, el ordenamiento de burbuja, los locales crípticos, MODO\_DEBUG sin uso y el except Exception demasiado amplio.

Refactors atómicos, de menor a mayor riesgo (en cada paso, pytest debe dar 20 passed)

# Refactor	Errores de ruff que quita

R1	Cabeceras e imports	6
R2	with en almacen.py y hay\_archivo	5
R3	Eliminar código muerto	2
R4	Constantes y renombrados (contador\_ventas, formatear\_dinero)	1
R5	Simplificar reportes.py (sorted estable, helper de stock bajo)	0
R6	Función de precios común con VIP explícito	4
R7	Dividir registrar\_venta	1
R8	Dividir menu	1

Con los ocho, ruff baja de 20 a 0.

R3 solo se aplica si lo pides explícitamente, como exige CLAUDE.md.
R6 y R7 tocan las reglas más frágiles: el VIP que solo aplica a ventas, los redondeos, que cotizar coincida con el total de la venta y el orden de los mensajes de ultimo\_error.
R8 va al final porque main.py no tiene tests; habrá que comparar la salida de la consola a mano.

El estado global (S24) se puede mitigar, pero no eliminar sin romper la API que usan los tests.

=======================================================================================================================================================================
Observación: Al terminar la propuesta Claude Code dice "Claude propuso un plan" y espera respuesta, lo que me esta pidiendo es cambiar a modo Automático.

