# Corrector de informes de laboratorio

Corrige informes de prácticas de laboratorio en PDF desde el chat de Claude Code. Subes el guion
de la práctica, la rúbrica (Excel) y los informes de los alumnos, y Claude los corrige con tu rúbrica
y te devuelve un Excel de notas: una fila por alumno, comentarios en las celdas por debajo del
máximo, REVISAR en los casos dudosos, total con fórmula, feedback general y avisos.

## Cómo utilizarlo

### Qué necesitas
- Una suscripción a Claude que incluya **Claude Code** (Pro o Max). No hace falta clave de API.
- Una cuenta de **GitHub** (gratis).

### La primera vez
1. Crea tu propia copia: en esta página, **Use this template → Create a new repository**, y márcala
   como **Private**. (Si no aparece el botón: **Code → Download ZIP** y sube el contenido a un
   repositorio privado tuyo.)
2. Da acceso a Claude a tu copia en **https://claude.ai/connect-github**.
3. Abre **Claude Code** (app de Claude → Code, o claude.ai/code) e inicia una sesión con tu
   repositorio seleccionado.
4. Si tu rúbrica es otra, sube tu Excel y dile qué pestaña usar. Formato esperado de la pestaña:
   `Bloque | Criterio | Peso | Sobresaliente (3) | Bien (2) | Suficiente (1) | Insuficiente (0)`,
   como la tabla del final.

### Cada vez que corrijas
1. Inicia una **sesión nueva** con tu repositorio seleccionado (una práctica por sesión).
2. Sube los **informes en PDF** y, si la práctica es nueva, el **guion** (vale escaneado; si lleva
   tu pauta de corrección escrita, mejor).
3. Pídelo con tus palabras, por ejemplo:
   > Corrige estos informes de la práctica 3 con la rúbrica Rúbrica_Todo - Informe. Módulo AIN.
4. Claude te pregunta lo que no tenga claro (qué práctica es, qué no se evalúa…), corrige y te
   entrega el **Excel**. Te dice cuántos informes ha corregido y cuáles tienen celdas en REVISAR.
5. Revisa el Excel. Si cambias un criterio («este error vale nivel 1», «las cuestiones no se
   evalúan»), díselo: lo guarda como regla de la práctica para las siguientes tandas.
6. Si quieres feedback individual de un alumno, pídelo **en la misma sesión**.

### Privacidad
Los informes, las correcciones y los Excel de notas **no se suben nunca al repositorio** (los excluye
`.gitignore`, y Claude lo comprueba antes de cada guardado). Solo se guardan las instrucciones, las
rúbricas y las reglas de cada práctica, en anónimo. Los guiones en PDF tampoco se suben.

## Qué hay en la carpeta

- `biblioteca/rubricas/` — rúbricas importadas del Excel.
- `biblioteca/practicas/<práctica>/practica.json` — pauta, valores de referencia, indicaciones y
  **errores frecuentes** (cómo puntuar cada error típico, para que siempre se puntúe igual).
- `.claude/skills/corregir-informes/` — el procedimiento que sigue Claude.
- `herramientas.py`, `corrector_lab.py` — validan las correcciones y generan el Excel.

## Cómo se corrige

1. Claude lee cada informe, rehace los cálculos con Python y puntúa cada criterio (niveles 0–3 con
   medios niveles; puntos = peso · nivel / 3), aplicando la pauta y los errores frecuentes.
2. **Revisión de coherencia**: compara a todos los alumnos de la tanda (mismo error → mismo nivel,
   sin dobles penalizaciones) y te propone añadir los errores repetidos nuevos a la práctica.
3. Genera el Excel y te dice cuántos informes ha corregido y cuáles tienen REVISAR.

## Rúbrica de evaluación (Excel, pestaña «Rúbrica_Todo»)

| Bloque | Criterio | Peso (%) | Sobresaliente (3) | Bien (2) | Suficiente (1) | Insuficiente (0) |
|---|---|---|---|---|---|---|
| Cuaderno | Diagrama de trabajo | 5 | Diagrama completo, ordenado, claro y adaptado a toda la práctica. | Diagrama correcto con pequeños errores u omisiones. | Diagrama con errores u omisiones relevantes o poco adaptado a la práctica. | Diagrama inadecuado o no presenta diagrama. |
| Cuaderno | Datos de seguridad de reactivos | 3 | Identifica todos los peligros, pictogramas y medidas de seguridad. | Identifica la mayoría de los riesgos y medidas. | Información parcial o con errores relevantes. | No identifica correctamente los riesgos o no presenta los datos de seguridad de los reactivos. |
| Cuaderno | Cálculos previos | 10 | Todos los cálculos correctos, justificados y bien presentados. | Pequeños errores que no afectan al procedimiento. | Varios errores conceptuales o de cálculo. | Cálculos incorrectos o ausentes. |
| Cuaderno | Registro en el cuaderno durante la práctica | 3 | Anota en el momento lo realmente hecho: fecha y condiciones (T y %H), nº de equipos, datos primarios en tablas con unidades SI y desviaciones del procedimiento. Sin borrones. | Registro completo con pequeñas omisiones (alguna unidad, equipo o desviación sin anotar). | Registro incompleto o poco claro: faltan datos primarios o desviaciones relevantes, o hay borrados o lápiz. | No registra los datos durante la práctica o el cuaderno no permitiría repetir el experimento. |
| Cuaderno | Seguridad, orden y manejo de equipos | 4 | Aplica siempre las normas de seguridad, mantiene el puesto ordenado y limpio y usa correctamente los equipos. | Aplica las normas con alguna incidencia menor y usa los equipos con ayuda mínima. | Necesita recordatorios frecuentes de seguridad u orden, o tiene dificultades con los equipos. | No cumple las normas de seguridad, deja el puesto desordenado o inseguro, usa mal los equipos o no se puede evaluar por ausencia. |
| Informe | Presentación | 5 | Se incluye título, autores, fecha y grupo. El informe está libre de errores y su formato es uniforme y acorde a las indicaciones dadas. Usa un lenguaje científico adecuado. | El aspecto es uniforme, con lógica y coherencia. No presenta errores ortográficos o tipográficos, pero tiene algún pequeño error. | Está incompleta o el aspecto es uniforme pero presenta faltas de ortografía y expresiones en lenguaje poco científico, o alguna incoherencia. | No hay título/portada, o el texto contiene muchas faltas de ortografía y errores tipográficos y carece de uniformidad y coherencia. Su aspecto dificulta la lectura. |
| Informe | Objetivo y esquema | 15 | Presenta un objetivo breve (2-3 líneas), claro y concreto.<br>El diagrama de flujo es muy completo, lógico y fácil de seguir. Incluye las reacciones ajustadas. | Presenta el objetivo correcto, pero algo extenso o impreciso.<br>El diagrama no tiene errores, pero tiene omisiones menores. Incluye las reacciones sin ajustar. | Presenta el objetivo, pero con algunos errores o vago.<br>El diagrama es incompleto o poco claro. Incluye las reacciones con errores. | El objetivo está ausente o con errores graves.<br>El diagrama está ausente o es incoherente con el procedimiento. No incluye las reacciones. |
| Informe | Datos | 10 | Los datos y resultados están en tablas ya procesadas, con sus unidades y rotulación clara.<br>Las gráficas (si aplican) son del tipo adecuado, con ejes rotulados, unidades y título. | Presenta los datos en tablas y realiza correctamente las gráficas, pero con pequeños errores de unidades o de cifras significativas. | Presenta algunos datos, las tablas y/o las gráficas, pero de un modo incorrecto (datos sin procesar, faltan ejes o títulos) o con errores de unidades. | Presenta pocos datos experimentales. No utiliza tablas ni gráficas, y hay errores graves de unidades y/o de datos. |
| Informe | Cálculos | 20 | Aparece un cálculo representativo perfectamente detallado con sus unidades. El tratamiento estadístico (media, s, CV e I) está completo y bien calculado. | Aparecen los cálculos con algún error pequeño, o una unidad mal expresada. Al tratamiento estadístico le falta algún parámetro menor o tiene un error de expresión. | Aparecen los cálculos incompletos o con fallos graves, con errores de unidades. El tratamiento estadístico es incompleto o tiene errores de concepto. | Aparecen los cálculos con muchos errores, o tienen muchos errores de unidades. No hay tratamiento estadístico. |
| Informe | Resultados | 10 | El resultado obtenido es correcto y está expresado como X̄ ± I (95 % de confianza) con sus unidades correctamente. | El resultado obtenido es correcto, con algún pequeño error de unidades o de expresión de la incertidumbre (no muy grave). | El resultado es incorrecto, aunque tiene lógica y coherencia (error de calculadora), y/o presenta algunas unidades incorrectas, o no incluye la incertidumbre. | Hay un resultado, pero es incorrecto, incoherente y/o sin unidades. |
| Informe | Conclusiones y cuestiones | 15 | Compara con el valor teórico/esperado, calcula el error y razona sus posibles causas.<br>Valora la precisión (CV), propone mejoras y justifica ampliando con datos bibliográficos o legislativos.<br>Las cuestiones están bien resueltas. | Compara y razona con una justificación breve pero adecuada al problema planteado.<br>Las cuestiones están respondidas, con algún fallo menor. | Aparecen, pero son muy breves, solo descriptivas o sin demasiada lógica con el problema planteado.<br>Las cuestiones están parcialmente respondidas. | La discusión y las conclusiones no están presentes, o no hay relación con el problema planteado.<br>Las cuestiones están sin responder. |
|  | Cuaderno | 25 |  |  |  |  |
|  | Informe | 75 |  |  |  |  |
|  | TOTAL | 100 |  |  |  |  |
