# El Millón del Saber · Afectividad y Sexualidad

Un juego de repaso con el formato de *¿Quién quiere ser millonario?* para el trabajo final de la materia Afectividad y Sexualidad.

**Jugar en línea:** https://damianreynoso-ai.github.io/Quien_quiere_ser_millonario_sexualidad/

## Qué hay en el repo

| Archivo | Para qué sirve |
|---|---|
| `index.html` | El juego completo en un solo archivo. Se puede abrir sin internet con doble clic. |
| `guia/Guia_de_preguntas_con_respuestas.pdf` | La guía de preguntas con respuestas que pide la rúbrica. |
| `herramientas/` | Los archivos con los que se generan el juego y la guía (ver abajo). |

## Cómo se juega

1. Abre `index.html` y escribe los nombres de los equipos.
2. Elige qué tan larga es la escalera: 15 preguntas (el formato original), 10 (la recomendada para 30 a 40 minutos) o 7. Elige también el tiempo por pregunta.
3. Los equipos pasan por turnos. Eligen una opción y el moderador confirma con “¿Es su última palabra?”. Si fallan, se quedan con el último nivel seguro. También pueden plantarse y llevarse lo que llevan.
4. Cada equipo tiene estos comodines: 50:50, llamada a alguien de otro equipo, ayuda del público (el grupo vota a mano alzada) y cambio de pregunta.
5. Al terminar aparece la tabla de posiciones y se le da su premio al equipo que gane.

Atajos de teclado para el moderador: las teclas **A** a **D** eligen una opción, **Enter** confirma y **M** silencia el sonido.

## Cómo editar las preguntas

**Forma fácil (solo el juego):** abre `index.html` en un editor de texto y busca `const PREGUNTAS`. Cada pregunta tiene esta forma:

```js
{"id": 1, "nivel": 1, "tema": "…", "pregunta": "…", "opciones": ["A", "B", "C", "D"], "c": 0, "explicacion": "…", "fuente": "…"}
```

`nivel` va de 1 (fácil) a 3 (difícil), y `c` es la posición de la respuesta correcta (0 = A, 1 = B, 2 = C, 3 = D).

**Forma completa (el juego y el PDF a la vez):** edita `herramientas/preguntas.py`. Ahí la primera opción de cada pregunta siempre es la correcta. Después corre:

```bash
cd herramientas
python3 build.py   # regenera ../index.html
node pdf.js        # regenera la guía en PDF (requiere Playwright)
```

Si solo cambias el diseño, edita `herramientas/plantilla.html` en lugar de `index.html`, porque `build.py` sobrescribe `index.html` cada vez que lo corres.
