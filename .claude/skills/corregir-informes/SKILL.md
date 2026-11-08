---
name: corregir-informes
description: Corrige tandas de informes de laboratorio en PDF que el profesor sube al chat, con la rúbrica y la práctica de la biblioteca, y entrega el Excel de notas. Úsala cuando el profesor suba informes, un guion o una rúbrica, pida corregir, cambiar una rúbrica o una práctica, o pida feedback de un alumno.
---

# Corregir informes de laboratorio

El profesor sube los archivos al chat y tú corriges. No hay aplicación ni API: lees los PDF,
puntúas y `herramientas.py` valida tu trabajo y monta el Excel. Ejecuta todo desde la raíz del
proyecto. Si falta alguna librería: `pip install -r requirements.txt`.

Los archivos que sube el profesor aparecen en la carpeta de subidas de la sesión
(p. ej. `/root/.claude/uploads/<sesión>/`), con un prefijo aleatorio en el nombre.

## 1. Identificar práctica y rúbrica

- `python3 herramientas.py biblioteca` lista rúbricas y prácticas (con sus errores frecuentes y tandas).
- Deduce la práctica de los informes o del guion y **confírmala con el profesor** si hay dudas.
- **Rúbrica nueva desde el Excel**: `python3 herramientas.py importar-rubrica <excel>` muestra las
  pestañas; pregunta cuál usar y con qué bloque (normalmente solo «Informe»), y luego
  `python3 herramientas.py importar-rubrica <excel> --hoja "<pestaña>" --bloques Informe --nombre "<nombre>"`.
  Pregunta también cómo quiere la nota total si no es la suma de pesos.
- **Cambios en una rúbrica** (pesos, descriptores, indicaciones): edita `biblioteca/rubricas/<id>.json`
  (campo `indicaciones` para reglas fijas). El total se recalcula con `core.guardar_rubrica`.
- **Práctica nueva desde un guion**: lee el guion completo (si es un escaneo, como imágenes), localiza
  la práctica y crea `biblioteca/practicas/<id>/practica.json` con: `id`, `titulo`, `rubrica_id`,
  `indicaciones` (reglas del profesor para esta práctica), `objetivo`, `fundamento`, `procedimiento`,
  `formulas` (lista, formato lineal), `valores_referencia` (lista de {magnitud, valor, unidad,
  tolerancia_o_comentario}), `apartados_exigidos`, `pautas_correccion` (transcribe la pauta del
  profesor si la hay; es prioritaria), `datos_experimentales_referencia`, `errores_frecuentes`
  (lista de {error, criterio, como_puntuar}), `notas` y `guion` (`practicas/<id>/guion.pdf`: copia ahí
  el guion). No inventes valores de referencia. Propón errores frecuentes solo si se deducen del
  guion o la pauta, y díselo al profesor para que los revise.
- Si el profesor indica algo para una práctica («las cuestiones no se evalúan», «este error vale
  nivel 1»…), guárdalo en `indicaciones` o en `errores_frecuentes` de la práctica para las siguientes tandas.

## 2. Preparar la tanda

Crea `biblioteca/practicas/<id>/tandas/<AAAA-MM-DD_HHMM>/informes/` y copia los PDF quitando el prefijo
aleatorio, con nombres sin espacios ni tildes (APELLIDOS_NOMBRE.pdf).

## 3. Instrucciones exactas

```bash
python3 herramientas.py instrucciones --practica <id> [--rubrica <id>] --modulo <módulo>
```

Son las reglas de corrección, la rúbrica con descriptores, la práctica con su pauta, indicaciones y
errores frecuentes, y el esquema JSON. **Síguelas al pie de la letra.**

## 4. Corregir cada informe

Para cada PDF:
1. Léelo entero, también tablas, gráficas e imágenes (Read con `pages`).
2. Rehaz los cálculos con los datos del alumno **ejecutando Python**; no calcules de cabeza.
   Clasifica cada discrepancia en error de cálculo, de datos o de método.
3. Compara con los valores de referencia y la pauta. Comprueba uno a uno los `errores_frecuentes`
   y, si aparecen, puntúalos exactamente como indican.
4. Nivel por criterio (0, 0.5, 1, 1.5, 2, 2.5 o 3); los puntos los calcula el script (peso · nivel / 3).
   Comentario de 1-3 frases: qué falta o qué está mal y dónde (página o apartado); con nivel 3,
   «Completo.». Si algo no se puede leer o es dudoso: `"revisar": true` y explica por qué.
5. Escribe `detalle/<nombre_del_pdf_sin_extension>.json` con el esquema del paso 3. Opcional:
   `"avisos_extra": ["..."]` (p. ej. datos compartidos entre alumnos).

Con muchos informes puedes repartir la lectura entre subagentes, pero la revisión del paso 4b la haces tú.

## 4b. Revisión de coherencia (obligatoria si hay 2 o más informes)

```bash
python3 herramientas.py resumen biblioteca/practicas/<id>/tandas/<fecha> --practica <id> [--rubrica <id>]
```

Revisa todas las correcciones juntas: mismo error → mismo nivel, ningún informe mejor con menos nivel,
sin dobles penalizaciones; resuelve los REVISAR que queden claros (los que sigan siendo decisión del
profesor se quedan). Ajusta los JSON y deja constancia en cada uno con `"ajustes_coherencia":
[{"criterio", "nivel_anterior", "nivel_nuevo", "revisar_anterior", "revisar_nuevo", "motivo"}]`.
Anota los errores repetidos que no estén en `errores_frecuentes`.

## 5. Generar el Excel y entregarlo

```bash
python3 herramientas.py excel biblioteca/practicas/<id>/tandas/<fecha> --practica <id> [--rubrica <id>] [--sobre <nota>]
```

Si da errores de validación, corrige los JSON y repite. Envía el Excel al profesor con SendUserFile.

## 6. Respuesta al profesor

Di **solo** cuántos informes has corregido y cuáles tienen celdas en REVISAR. No repitas la tabla.
Si la revisión de coherencia encontró errores repetidos nuevos, añade una lista breve
(error · criterio · cómo lo puntuaste) y pregunta si los guardas en la práctica; no los guardes sin
su confirmación. Si pide feedback individual de un alumno, sácalo de su JSON en `detalle/`.

## 7. Guardar en GitHub (solo reglas, nunca datos de alumnos)

El repositorio es privado pero **no debe contener datos del alumnado**. `.gitignore` excluye las tandas
(informes, correcciones, Excel) y todos los PDF y Word (los guiones pueden llevar nombres a mano).
Lo que se guarda: procedimiento, scripts, rúbricas y `practica.json` (pauta, indicaciones, errores
frecuentes). Antes de cada commit:
1. `git status` y comprueba que no aparece nada de `tandas/`, ningún PDF ni Excel de notas.
2. Comprueba que `practica.json`, rúbricas e indicaciones **no contienen nombres de alumnos**: escribe
   las reglas en anónimo («si calcula s = [OH⁻]…»), nunca con el nombre de un alumno.
3. Commit con un mensaje que diga qué regla o práctica cambia, y push a la rama principal.

Las tandas solo viven durante la sesión: el feedback individual de un alumno se pide en la misma
sesión de la corrección. Avisa de ello al entregar el Excel.

Cuando el profesor resuelva un REVISAR o cambie una nota, corrige el JSON, regenera el Excel y
pregunta si convierte esa decisión en regla de la práctica (`errores_frecuentes` o `indicaciones`).
