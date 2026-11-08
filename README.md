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

## Cómo se corrige

1. Claude lee cada informe, rehace los cálculos con Python y puntúa cada criterio (niveles 0–3 con
   medios niveles; puntos = peso · nivel / 3), aplicando la pauta y los errores frecuentes.
2. **Revisión de coherencia**: compara a todos los alumnos de la tanda (mismo error → mismo nivel,
   sin dobles penalizaciones) y te propone añadir los errores repetidos nuevos a la práctica.
3. Genera el Excel y te dice cuántos informes ha corregido y cuáles tienen REVISAR.
