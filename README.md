# ¿Quién Quiere Ser Sexperto? · Afectividad y Sexualidad

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
2. Elige qué tan larga es la escala: 15 preguntas (el formato original), 10 (la recomendada para 30 a 40 minutos) o 7. Elige también el tiempo por pregunta.
3. Los equipos pasan por turnos. Eligen una opción y el moderador confirma con “¿Es su última palabra?”. En lugar de dinero suben por la **escala sexual** 🌡️: 👀 Contacto visual, 😏 Sonrisa coqueta, 🌮 Cita en los tacos, 🤝 De la manita, 💋 Primer beso, 🍿 Faje en el cine, 💬 “¿Qué somos?”, 👵 Conocer a la suegra, 🛡️ Con condón, siempre, 🛏️ Se quedó a dormir, 🎆 Clímax académico… hasta 👑 **SEXPERTO**. Cada escalón da puntos. Los niveles seguros son 🤝 De la manita y 🛡️ Con condón, siempre. **Si un equipo llega a SEXPERTO, el juego termina** y ese equipo gana. Si fallan, se quedan en el último nivel seguro (o en la friendzone 🙈). También pueden plantarse.
4. Cada equipo tiene estos comodines: 50:50, llamada a alguien de otro equipo, ayuda del público (el grupo vota a mano alzada) y cambio de pregunta.
5. **¡Robo!** Si un equipo falla, antes de revelar la respuesta otro equipo puede intentar robarla. El primero que levante la mano elige entre las opciones que quedan y, si acierta, gana un bono de la mitad de los puntos de esa pregunta.
6. Arriba siempre se ve el marcador de todos los equipos, cada uno con su avatar de doble sentido (🍆 🍑 🌶️ 🍒 🌮 🍌 🥥 💦). Al terminar aparece la tabla de posiciones (puntos de la escala más bonos de robo, con empates incluidos) y se le da su premio al equipo que gane.

Los comodines de llamada y público se abren en un panel al lado de la pregunta para que las opciones sigan visibles. En celular el panel aparece arriba de la pregunta.

Para que no se repitan patrones, **las opciones se revuelven cada vez que sale una pregunta** (la letra correcta cambia en cada partida) y las preguntas se eligen al azar sin repetirse en la misma computadora hasta agotar el banco. Por eso las letras de la guía en PDF pueden no coincidir con las del juego.

El juego tiene **música de fondo original estilo EDM de cuenta regresiva**, en tres pistas que se repiten sin cortes: en las preguntas fáciles suena una intro tranquila (120 BPM), en las intermedias entra el bombo y las palmas (128 BPM) y en las difíciles viene el drop con melodía, redobles y platillos (138 BPM). Al cambiar de dificultad hace un fundido, y durante la revelación de la respuesta baja de volumen. Las pistas se generan con `herramientas/musica.py` y `build.py` las mete dentro de `index.html`.

Atajos de teclado para el moderador: las teclas **A** a **D** eligen una opción, **Enter** confirma la última palabra, **Esc** la cancela, **M** silencia los efectos y **N** apaga o prende la música.

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
