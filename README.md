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

## Cómo se corrige

1. Claude lee cada informe, rehace los cálculos con Python y puntúa cada criterio (niveles 0–3 con
   medios niveles; puntos = peso · nivel / 3), aplicando la pauta y los errores frecuentes.
2. **Revisión de coherencia**: compara a todos los alumnos de la tanda (mismo error → mismo nivel,
   sin dobles penalizaciones) y te propone añadir los errores repetidos nuevos a la práctica.
3. Genera el Excel y te dice cuántos informes ha corregido y cuáles tienen REVISAR.
