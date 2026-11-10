# Corrector de informes de laboratorio

Corrige informes de prácticas de laboratorio en PDF desde el chat de Claude Code. Subes el guion
de la práctica, la rúbrica (Excel) y los informes de los alumnos, y Claude los corrige con tu rúbrica
y te devuelve un Excel de notas: una fila por alumno, comentarios en las celdas por debajo del
máximo, REVISAR en los casos dudosos, total con fórmula, feedback general y avisos.

## Cómo utilizarlo (en tu ordenador)

### Qué necesitas
- Una suscripción a Claude que incluya **Claude Code** (Pro o Max). No hace falta clave de API.
- **Python 3** instalado (para generar el Excel).
  - **Mac:** normalmente ya viene. Compruébalo en la Terminal con `python3 --version`.
  - **Windows:** descárgalo de python.org y, al instalar, marca **«Add python.exe to PATH»**.

### La primera vez
1. **Descarga la carpeta:** en esta página, **Code → Download ZIP**.
2. **Descomprímela** en un sitio fijo, por ejemplo en Documentos.
3. **Ábrela en Claude Code**, de una de estas dos formas:
   - **App de escritorio de Claude** (claude.ai/download) → sección **Code** → trabajar en local →
     elige la carpeta descomprimida.
   - **Terminal:** instala Claude Code (code.claude.com), entra en la carpeta y escribe `claude`.
     Inicia sesión con tu cuenta de Claude, no con una clave de API.
4. **Crea tu biblioteca:** dale tu **Excel de rúbricas** (y dile qué pestaña usar) y los
   **guiones de tus prácticas**. Claude crea la carpeta `biblioteca/` con tus rúbricas y una ficha por
   práctica (objetivo, fórmulas, valores de referencia y tu pauta). El formato esperado de la pestaña
   del Excel es `Bloque | Criterio | Peso | Sobresaliente (3) | Bien (2) | Suficiente (1) | Insuficiente (0)`,
   como la tabla del final. La primera vez instalará las librerías que necesita
   (`requirements.txt`); acepta los permisos que te pida.
5. Comprueba que está todo preguntándole: «¿Qué rúbricas y prácticas tengo?».

### Cada vez que corrijas
1. Abre la carpeta en Claude Code y empieza una **conversación nueva** (una práctica por conversación).
2. Adjunta en el chat los **informes en PDF** o indícale la carpeta donde están. Si la práctica es
   nueva, dale también el **guion**: vale escaneado y, si lleva tu pauta de corrección escrita, mejor.
3. Pídelo con tus palabras, por ejemplo:
   > Corrige los informes de la carpeta Descargas/P3 con la práctica 3 del guion Descargas/guion.pdf
   > y la rúbrica Rúbrica_Todo - Informe. Módulo AIN.
4. Claude te pregunta lo que no tenga claro (qué práctica es, qué no se evalúa…), corrige y genera el
   **Excel**. Te dice cuántos informes ha corregido y cuáles tienen celdas en REVISAR. El Excel queda
   en `biblioteca/practicas/<práctica>/tandas/<fecha>/`.
5. Revisa el Excel. Si cambias un criterio («este error vale nivel 1», «las cuestiones no se
   evalúan»), díselo: lo guarda como regla de la práctica para las siguientes tandas.
6. Para el feedback individual de un alumno, pídeselo cuando quieras: la corrección de cada alumno
   queda guardada en la carpeta de la tanda.

### Copia de seguridad y privacidad
- Tu información (rúbricas, guiones, prácticas, reglas y correcciones) se guarda en la carpeta
  `biblioteca/` de tu ordenador. **No forma parte del agente** y no se sube nunca al repositorio.
  **Haz copia de seguridad de ella** de vez en cuando; si descargas una versión nueva del agente,
  copia tu carpeta `biblioteca/` dentro de la nueva.
- Los informes y las notas se quedan en tu ordenador. Claude los lee para corregirlos, igual que
  cualquier archivo que le muestres en una conversación.
- Si compartes el agente, comparte este repositorio: no lleva nada tuyo ni de tus alumnos.

## Qué hay en la carpeta

**El agente** (este repositorio):

- `.claude/skills/corregir-informes/` — el procedimiento que sigue Claude.
- `herramientas.py`, `corrector_lab.py` — validan las correcciones y generan el Excel.

**Tu biblioteca** (`biblioteca/`, solo en tu ordenador, la crea Claude):

- `biblioteca/rubricas/` — rúbricas importadas del Excel.
- `biblioteca/practicas/<práctica>/practica.json` — pauta, valores de referencia, indicaciones y
  **errores frecuentes** (cómo puntuar cada error típico, para que siempre se puntúe igual).
- `biblioteca/practicas/<práctica>/tandas/<fecha>/` — cada corrección: informes, corrección de cada
  alumno y el Excel (solo en tu ordenador; no se sube al repositorio).

## Cómo se corrige

1. Claude lee cada informe, rehace los cálculos con Python y puntúa cada criterio (niveles 0–3 con
   solo enteros; puntos = peso · nivel / 3), aplicando la pauta y los errores frecuentes.
2. **Revisión de coherencia**: compara a todos los alumnos de la tanda (mismo error → mismo nivel,
   sin dobles penalizaciones) y te propone añadir los errores repetidos nuevos a la práctica.
3. Genera el Excel y te dice cuántos informes ha corregido y cuáles tienen REVISAR.

## Ejemplo de rúbrica (formato del Excel)

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
