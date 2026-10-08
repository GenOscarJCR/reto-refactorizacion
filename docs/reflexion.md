# Reflexión final

Claude Code me resultó muy útil: levantó un inventario de 27 smells, verificó cada cambio
comparando las salidas y acompañó la bajada de ruff de 20 errores a 0. También me señaló
cosas que yo no había notado, como el SIM108 que "desapareció" por la longitud de línea,
la diferencia entre un descuento 0 entero y 0.0, y la duplicación dentro del propio CLAUDE.md.
No todo lo acepté tal cual. Corregí los type hints que metió en R1 fuera de alcance, la
numeración del plan y el plan que ejecutó de golpe estando en modo Plan. También rechacé la
v1 de CLAUDE.md porque perdió secciones, aunque eso se debió a la estructura del prompt que
le envié. De todo esto me llevo varios aprendizajes. La variante A de R3 me mostró que un
buen CLAUDE.md es lo que hace funcionar los prompts cortos. Comprobé que .claudeignore no
funciona y que deny sí, pero con huecos. Entendí el valor de calibrar la aprobación según
el riesgo de cada cambio. Y, sobre todo, que yo defino los casos límite y la IA los ejecuta.
