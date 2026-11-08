# Corrector de informes de laboratorio (CFGS LACQ)

Se usa desde el chat de Claude Code: subes el guion, la rúbrica (Excel) y los informes en PDF, y
Claude los corrige con tu rúbrica y te devuelve el Excel de notas (una fila por alumno, comentarios
en las celdas por debajo del máximo, REVISAR en los casos dudosos, total con fórmula, feedback
general y avisos).

## Qué hay en la carpeta

- `biblioteca/rubricas/` — rúbricas (importadas de tu Excel; se pueden cambiar pidiéndoselo a Claude).
- `biblioteca/practicas/<práctica>/` — guion, pauta, valores de referencia, indicaciones y
  **errores frecuentes** (cómo puntuar cada error típico, para que siempre se puntúe igual).
- `biblioteca/practicas/<práctica>/tandas/<fecha>/` — cada corrección: informes, corrección de
  cada alumno (`detalle/`) y el Excel.
- `.claude/skills/corregir-informes/` — el procedimiento que sigue Claude.
- `herramientas.py`, `corrector_lab.py` — validan las correcciones y generan el Excel.

## Ejemplo: la primera rúbrica («Rúbrica_Todo - Informe»)

Es la rúbrica que se usó en la P2. Se importó de la pestaña **Rúbrica_Todo** del Excel `biblioteca/Rubricas_Informes.xlsx`, solo con el bloque **Informe** (el bloque Cuaderno se evalúa aparte). Está en `biblioteca/rubricas/rubrica-todo-informe.json`. **Total: 75 puntos.**

### Criterios, pesos y puntos por nivel

Cada criterio recibe un nivel de 0 a 3 (se admiten medios niveles) y sus puntos son **peso · nivel / 3**.

| Criterio | Peso | Sobresaliente (3) | Bien (2) | Suficiente (1) | Insuficiente (0) |
|---|---:|---:|---:|---:|---:|
| Presentación | 5 | 5 | 3,33 | 1,67 | 0 |
| Objetivo y esquema | 15 | 15 | 10 | 5 | 0 |
| Datos | 10 | 10 | 6,67 | 3,33 | 0 |
| Cálculos | 20 | 20 | 13,33 | 6,67 | 0 |
| Resultados | 10 | 10 | 6,67 | 3,33 | 0 |
| Conclusiones y cuestiones | 15 | 15 | 10 | 5 | 0 |

Ejemplo de medio nivel: Cálculos con nivel 2,5 → 20 · 2,5 / 3 = **16,67 puntos**.

**Indicación fija de esta rúbrica:** Lo que se evalúa en el cuaderno de laboratorio (cálculos previos como el pH teórico o la preparación de disoluciones, códigos de equipos, condiciones registradas) no puntúa en el informe.

### Descriptores

<details><summary><b>Presentación</b> (5 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | Se incluye título, autores, fecha y grupo. El informe está libre de errores y su formato es uniforme y acorde a las indicaciones dadas. Usa un lenguaje científico adecuado. |
| Bien (2) | El aspecto es uniforme, con lógica y coherencia. No presenta errores ortográficos o tipográficos, pero tiene algún pequeño error. |
| Suficiente (1) | Está incompleta o el aspecto es uniforme pero presenta faltas de ortografía y expresiones en lenguaje poco científico, o alguna incoherencia. |
| Insuficiente (0) | No hay título/portada, o el texto contiene muchas faltas de ortografía y errores tipográficos y carece de uniformidad y coherencia. Su aspecto dificulta la lectura. |

</details>

<details><summary><b>Objetivo y esquema</b> (15 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | Presenta un objetivo breve (2-3 líneas), claro y concreto.<br>El diagrama de flujo es muy completo, lógico y fácil de seguir. Incluye las reacciones ajustadas. |
| Bien (2) | Presenta el objetivo correcto, pero algo extenso o impreciso.<br>El diagrama no tiene errores, pero tiene omisiones menores. Incluye las reacciones sin ajustar. |
| Suficiente (1) | Presenta el objetivo, pero con algunos errores o vago.<br>El diagrama es incompleto o poco claro. Incluye las reacciones con errores. |
| Insuficiente (0) | El objetivo está ausente o con errores graves.<br>El diagrama está ausente o es incoherente con el procedimiento. No incluye las reacciones. |

</details>

<details><summary><b>Datos</b> (10 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | Los datos y resultados están en tablas ya procesadas, con sus unidades y rotulación clara.<br>Las gráficas (si aplican) son del tipo adecuado, con ejes rotulados, unidades y título. |
| Bien (2) | Presenta los datos en tablas y realiza correctamente las gráficas, pero con pequeños errores de unidades o de cifras significativas. |
| Suficiente (1) | Presenta algunos datos, las tablas y/o las gráficas, pero de un modo incorrecto (datos sin procesar, faltan ejes o títulos) o con errores de unidades. |
| Insuficiente (0) | Presenta pocos datos experimentales. No utiliza tablas ni gráficas, y hay errores graves de unidades y/o de datos. |

</details>

<details><summary><b>Cálculos</b> (20 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | Aparece un cálculo representativo perfectamente detallado con sus unidades. El tratamiento estadístico (media, s, CV e I) está completo y bien calculado. |
| Bien (2) | Aparecen los cálculos con algún error pequeño, o una unidad mal expresada. Al tratamiento estadístico le falta algún parámetro menor o tiene un error de expresión. |
| Suficiente (1) | Aparecen los cálculos incompletos o con fallos graves, con errores de unidades. El tratamiento estadístico es incompleto o tiene errores de concepto. |
| Insuficiente (0) | Aparecen los cálculos con muchos errores, o tienen muchos errores de unidades. No hay tratamiento estadístico. |

</details>

<details><summary><b>Resultados</b> (10 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | El resultado obtenido es correcto y está expresado como X̄ ± I (95 % de confianza) con sus unidades correctamente. |
| Bien (2) | El resultado obtenido es correcto, con algún pequeño error de unidades o de expresión de la incertidumbre (no muy grave). |
| Suficiente (1) | El resultado es incorrecto, aunque tiene lógica y coherencia (error de calculadora), y/o presenta algunas unidades incorrectas, o no incluye la incertidumbre. |
| Insuficiente (0) | Hay un resultado, pero es incorrecto, incoherente y/o sin unidades. |

</details>

<details><summary><b>Conclusiones y cuestiones</b> (15 puntos)</summary>

| Nivel | Descriptor |
|---|---|
| Sobresaliente (3) | Compara con el valor teórico/esperado, calcula el error y razona sus posibles causas.<br>Valora la precisión (CV), propone mejoras y justifica ampliando con datos bibliográficos o legislativos.<br>Las cuestiones están bien resueltas. |
| Bien (2) | Compara y razona con una justificación breve pero adecuada al problema planteado.<br>Las cuestiones están respondidas, con algún fallo menor. |
| Suficiente (1) | Aparecen, pero son muy breves, solo descriptivas o sin demasiada lógica con el problema planteado.<br>Las cuestiones están parcialmente respondidas. |
| Insuficiente (0) | La discusión y las conclusiones no están presentes, o no hay relación con el problema planteado.<br>Las cuestiones están sin responder. |

</details>

### Cómo se aplicó en la P2

La práctica P2 añade sus propias reglas (en `biblioteca/practicas/p2-kps-hidroxido-metalico/practica.json`):

- En «Conclusiones y cuestiones» solo se evalúan las conclusiones: las cuestiones no cuentan.
- 13 **errores frecuentes** con su puntuación fija. Por ejemplo: calcular s = [OH⁻] sin dividir entre 2 → error de método, Cálculos nivel 1 como máximo; falta solo el CV → Cálculos nivel 2,5; resultado sin X̄ ± I → Resultados nivel 1.

Para usar otra pestaña del Excel (por ejemplo `Rubrica_Informe`, sobre 100), basta con pedírselo a Claude en el chat: la importa y la guarda junto a esta.

## Cómo se corrige

1. Claude lee cada informe, rehace los cálculos con Python y puntúa cada criterio (niveles 0–3 con
   medios niveles; puntos = peso · nivel / 3), aplicando la pauta y los errores frecuentes.
2. **Revisión de coherencia**: compara a todos los alumnos de la tanda (mismo error → mismo nivel,
   sin dobles penalizaciones) y te propone añadir los errores repetidos nuevos a la práctica.
3. Genera el Excel y te dice cuántos informes ha corregido y cuáles tienen REVISAR.
