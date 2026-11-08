#!/usr/bin/env python3
"""Corrector de informes de laboratorio (CFGS LACQ): biblioteca, reglas de corrección y Excel.

Claude corrige los informes en la conversación (skill corregir-informes) y `herramientas.py`
usa este módulo para validar las correcciones y generar el Excel. No usa ninguna API.

Biblioteca en ./biblioteca:
  rubricas/<id>.json                 rúbricas
  practicas/<id>/practica.json       práctica (guion, pauta, valores de referencia, errores frecuentes)
  practicas/<id>/tandas/<fecha>/     cada corrección: informes, detalle JSON por alumno y Excel
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path


NIVELES = [0, 0.5, 1, 1.5, 2, 2.5, 3]  # 3 = Sobresaliente ... 0 = Insuficiente; se admiten medios niveles
UMBRAL_SIMILITUD = 0.30  # Jaccard de 6-gramas de palabras, descontando el texto del guion


class ErrorAgente(Exception):
    pass


def texto_docx(ruta: Path) -> str:
    import docx

    d = docx.Document(str(ruta))
    partes = [p.text for p in d.paragraphs]
    for t in d.tables:
        for fila in t.rows:
            partes.append(" | ".join(c.text.strip() for c in fila.cells))
    return "\n".join(partes)


def texto_pdf(ruta: Path) -> str:
    from pypdf import PdfReader

    try:
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(ruta)).pages)
    except Exception:
        return ""


def obj(props: dict, **extra) -> dict:
    return {"type": "object", "properties": props, "required": list(props),
            "additionalProperties": False, **extra}


S = {"type": "string"}
N = {"type": "number"}
B = {"type": "boolean"}


def arr(items: dict) -> dict:
    return {"type": "array", "items": items}


# ==========================================================================
# Reglas de corrección
# ==========================================================================

INSTRUCCIONES = """Eres profesor/a de un ciclo formativo de grado superior de Laboratorio de \
Análisis y Control de Calidad (LACQ) y corriges informes de prácticas de laboratorio. \
Corriges con criterio de profesor: exigente pero justo y constructivo. Solo corriges el \
informe (el cuaderno de laboratorio se evalúa aparte).

PROCESO
1. Lee el informe completo antes de puntuar.
2. Verifica los cálculos rehaciéndolos con los datos del propio alumno. Clasifica cada \
discrepancia como error de cálculo, error de datos o error de método.
3. Compara los resultados con los valores de referencia de la práctica y valora si las \
conclusiones se sostienen con ellos.
   Si la práctica trae pautas_correccion del profesor, síguelas: indican qué se evalúa y qué \
no en cada apartado y tienen prioridad sobre el guion.
4. Puntúa cada criterio de la rúbrica con un nivel de 0 a 3 (3 Sobresaliente, 2 Bien, \
1 Suficiente, 0 Insuficiente; usa medios niveles si el informe está entre dos descriptores) y un \
comentario que cite o localice el pasaje del informe (apartado o página) que lo respalda. Los \
puntos se calculan como peso·nivel/3.
5. No penalices dos veces el mismo error: si un dato erróneo arrastra los cálculos, penaliza \
el origen y valora los cálculos como correctos si son coherentes con ese dato.

REGLAS
- No inventes datos ni des algo por bueno si no lo ves en el informe.
- Si la práctica trae errores_frecuentes, comprueba cada uno en el informe y, si aparece, puntúalo \
exactamente como indica «como_puntuar» (criterio y nivel). Así el mismo error recibe siempre la \
misma nota en todos los alumnos.
- Lo que se evalúa en el cuaderno de laboratorio (cálculos previos como el pH teórico o la \
preparación de disoluciones, códigos de equipos, condiciones registradas) no puntúa en el informe.
- Si la pauta del profesor dice que un apartado no se evalúa (p. ej. cuestiones o muestra), no lo \
tengas en cuenta ni para bien ni para mal, aunque el nombre del criterio lo incluya.
- Si un apartado falta, dilo. Si no se puede leer o evaluar (p. ej. gráficas o tablas mal \
extraídas del PDF, imágenes ilegibles), marca el criterio con revisar=true y explica el motivo \
en el comentario en lugar de puntuar a ciegas. Usa también revisar=true en los casos dudosos \
que deba decidir el profesor.
- Comentario de cada criterio: 1-3 frases. Si la puntuación es la máxima, basta con \
"Completo." Si es inferior, di qué falta o qué está mal y dónde aparece en el informe.
- Uso de IA en la redacción: valóralo de forma objetiva solo con indicios concretos del texto \
(redacción genérica impropia del nivel, contenido que no corresponde a lo realizado, \
referencias inexistentes, estilo incoherente con el resto). Es solo una sospecha: no afecta \
a la nota.
- Castellano, tono profesional y cercano. Fórmulas en formato lineal (ej.: C₁·V₁ = C₂·V₂).
- feedback_general: 3-6 frases dirigidas al alumno: puntos fuertes, lo más importante a \
mejorar y un consejo concreto para el próximo informe."""


def esquema_correccion(rubrica: dict) -> dict:
    nombres = [c["nombre"] for c in rubrica["criterios"]]
    return obj({
        "alumno": {**S, "description": "Nombre(s) del alumno o alumnos según la portada; vacío si no aparece"},
        "practica_coincide": {**B, "description": "El informe corresponde a la práctica indicada"},
        "apartados_no_legibles": arr(obj({"apartado": S, "motivo": S})),
        "calculos": arr(obj({
            "descripcion": S,
            "formula": S,
            "resultado_alumno": S,
            "resultado_recalculado": S,
            "tipo": {"type": "string", "enum": ["correcto", "error_calculo", "error_datos",
                                                 "error_metodo", "no_verificable"]},
            "comentario": S,
        })),
        "comparacion_referencia": S,
        "criterios": arr(obj({
            "criterio": {"type": "string", "enum": nombres},
            "nivel": {"type": "number", "enum": NIVELES,
                      "description": "3 Sobresaliente, 2 Bien, 1 Suficiente, 0 Insuficiente; medios niveles si está entre dos descriptores"},
            "revisar": B,
            "comentario": S,
        })),
        "feedback_general": S,
        "sospecha_ia": obj({"nivel": {"type": "string", "enum": ["ninguna", "baja", "media", "alta"]},
                            "indicios": S}),
    })


def instrucciones_correccion(rubrica: dict, practica: dict, modulo: str | None = None) -> str:
    rub = {"criterios": [{k: c.get(k) for k in ("nombre", "puntuacion_maxima", "niveles")}
                         for c in rubrica["criterios"]]}
    pra = {k: v for k, v in practica.items()
           if k not in ("encontrada", "candidatas", "guion", "id", "rubrica_id", "indicaciones")}
    extra = "\n".join(x for x in (rubrica.get("indicaciones", ""), practica.get("indicaciones", "")) if x.strip())
    texto = (
        INSTRUCCIONES
        + (f"\n\nMÓDULO: {modulo}" if modulo else "")
        + "\n\nRÚBRICA (da a cada criterio un nivel de 0 a 3, en este orden):\n"
        + json.dumps(rub, ensure_ascii=False, indent=1)
        + "\n\nPRÁCTICA (guion y valores de referencia):\n"
        + json.dumps(pra, ensure_ascii=False, indent=1)
        + (f"\n\nINDICACIONES DEL PROFESOR (prioritarias):\n{extra}" if extra else "")
    )
    return texto


def normalizar_resultado(res: dict, rubrica: dict) -> dict:
    """Ordena los criterios según la rúbrica y valida las puntuaciones."""
    por_nombre = {c["criterio"]: c for c in res.get("criterios", [])}
    criterios = []
    for c in rubrica["criterios"]:
        r = por_nombre.get(c["nombre"])
        maximo = c["puntuacion_maxima"]
        if r is None:
            r = {"criterio": c["nombre"], "nivel": "", "puntuacion": None, "revisar": True,
                 "comentario": "El corrector no devolvió este criterio."}
        else:
            r = {**r, "puntuacion": round(maximo * float(r["nivel"]) / 3, 2)}
        criterios.append({**r, "maximo": maximo})
    return {**res, "criterios": criterios}


# ---------- Similitud entre informes (local, sin coste) ----------

def _tokens(texto: str) -> list[str]:
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.findall(r"[a-zñ]{3,}", t)


def _shingles(texto: str, n: int = 6) -> set[str]:
    p = _tokens(texto)
    return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}


def similitudes(textos: dict[str, str], texto_guion: str) -> dict[str, list[str]]:
    """Avisos de similitud entre pares de informes, descontando frases copiadas del guion."""
    base = _shingles(texto_guion)
    sh = {k: _shingles(v) - base for k, v in textos.items()}
    avisos: dict[str, list[str]] = {k: [] for k in textos}
    claves = sorted(k for k, s in sh.items() if len(s) >= 50)  # PDFs escaneados sin texto: se omiten
    for i, a in enumerate(claves):
        for b in claves[i + 1:]:
            inter = len(sh[a] & sh[b])
            j = inter / len(sh[a] | sh[b])
            if j >= UMBRAL_SIMILITUD:
                avisos[a].append(f"{b} ({j:.0%})")
                avisos[b].append(f"{a} ({j:.0%})")
    return avisos


# ---------- Excel ----------

def _tam_comentario(texto: str, ancho_px: int = 320) -> tuple[int, int]:
    chars_por_linea = max(20, ancho_px // 7)
    lineas = sum(max(1, math.ceil(len(l) / chars_por_linea)) for l in texto.split("\n"))
    return ancho_px, 24 + lineas * 18


def escribir_excel(resultados: list[dict], errores: list[tuple[str, str]], rubrica: dict, salida: Path,
                   sobre: float | None = None) -> None:
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Corrección"
    criterios = rubrica["criterios"]
    n = len(criterios)
    total_max = rubrica["total_maximo"]
    sobre = sobre or total_max
    sobre_txt = f"{sobre:g}".replace(".", ",")

    cab = ["Alumno"] + [c["nombre"] for c in criterios] + [f"Total (/{sobre_txt})", "Feedback general", "Avisos"]
    ws.append(cab)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="305496")
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")

    amarillo = PatternFill("solid", fgColor="FFF2CC")
    col_ini, col_fin = get_column_letter(2), get_column_letter(1 + n)
    col_total = 2 + n

    def comentar(celda, texto):
        com = Comment(texto, "Corrector")
        com.width, com.height = _tam_comentario(texto)
        celda.comment = com

    for fila, r in enumerate(resultados, start=2):
        ws.cell(fila, 1, r["alumno_mostrado"])
        for j, c in enumerate(r["criterios"]):
            celda = ws.cell(fila, 2 + j)
            if c["revisar"] or c["puntuacion"] is None:
                celda.value = "REVISAR"
                celda.fill = amarillo
                comentar(celda, c["comentario"])
            else:
                celda.value = c["puntuacion"]
                if c["puntuacion"] < c["maximo"] - 1e-9:
                    comentar(celda, c["comentario"])
        rango = f"{col_ini}{fila}:{col_fin}{fila}"
        escala = "" if abs(total_max - sobre) < 1e-9 else f"*{sobre}/{total_max}"
        ws.cell(fila, col_total, f'=IF(COUNTIF({rango},"REVISAR")>0,"REVISAR",ROUND(SUM({rango}){escala},2))')
        ws.cell(fila, col_total).font = Font(bold=True)
        ws.cell(fila, col_total + 1, r["feedback_general"])
        ws.cell(fila, col_total + 2, "\n".join(r["avisos"]))

    for nombre, motivo in errores:
        fila = ws.max_row + 1
        ws.cell(fila, 1, nombre)
        for j in range(n):
            ws.cell(fila, 2 + j, "REVISAR").fill = amarillo
        comentar(ws.cell(fila, 2), f"No se pudo corregir: {motivo}")
        rango = f"{col_ini}{fila}:{col_fin}{fila}"
        ws.cell(fila, col_total, f'=IF(COUNTIF({rango},"REVISAR")>0,"REVISAR",SUM({rango}))')
        ws.cell(fila, col_total + 2, f"Error al corregir: {motivo}")

    ws.column_dimensions["A"].width = 28
    for j in range(n):
        ws.column_dimensions[get_column_letter(2 + j)].width = 14
    ws.column_dimensions[get_column_letter(col_total)].width = 11
    ws.column_dimensions[get_column_letter(col_total + 1)].width = 70
    ws.column_dimensions[get_column_letter(col_total + 2)].width = 45
    ws.row_dimensions[1].height = 45
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical="top",
                                    horizontal="left" if c.column in (1, col_total + 1, col_total + 2) else "center")
    ws.freeze_panes = "B2"
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)


def construir_avisos(r: dict, sim: list[str]) -> list[str]:
    avisos = []
    if not r.get("alumno"):
        avisos.append("Nombre no encontrado en el informe (se usa el nombre del archivo).")
    if not r.get("practica_coincide", True):
        avisos.append("REVISAR: el informe no parece corresponder a esta práctica.")
    for a in r.get("apartados_no_legibles", []):
        avisos.append(f"No legible: {a['apartado']} ({a['motivo']})")
    ia = r.get("sospecha_ia", {})
    if ia.get("nivel") not in (None, "ninguna"):
        avisos.append(f"Sospecha de uso de IA ({ia['nivel']}, no penalizado): {ia['indicios']}")
    if sim:
        avisos.append("Similitud alta con: " + ", ".join(sim) + " (solo aviso)")
    return avisos


# ==========================================================================
# Biblioteca de rúbricas y prácticas
# ==========================================================================

BIBLIOTECA = Path(__file__).resolve().parent / "biblioteca"
DIR_RUBRICAS = BIBLIOTECA / "rubricas"
DIR_PRACTICAS = BIBLIOTECA / "practicas"


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60] or "sin-nombre"


def _leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def _escribir(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- Rúbricas ----------

def listar_rubricas() -> list[dict]:
    return sorted((_leer(p) for p in DIR_RUBRICAS.glob("*.json")), key=lambda r: r["nombre"].lower())


def cargar_rubrica(rid: str) -> dict:
    return _leer(DIR_RUBRICAS / f"{rid}.json")


def guardar_rubrica(rub: dict) -> dict:
    rub = dict(rub)
    rub["id"] = rub.get("id") or slug(rub["nombre"])
    crit = [c for c in rub["criterios"] if str(c.get("nombre", "")).strip()]
    if not crit:
        raise ErrorAgente("La rúbrica no tiene criterios.")
    nombres = [c["nombre"].strip() for c in crit]
    if len(set(nombres)) != len(nombres):
        raise ErrorAgente("Hay criterios con el mismo nombre.")
    for c in crit:
        c["nombre"] = c["nombre"].strip()
        c["puntuacion_maxima"] = float(c["puntuacion_maxima"])
        if c["puntuacion_maxima"] <= 0:
            raise ErrorAgente(f"El criterio «{c['nombre']}» debe tener un peso mayor que 0.")
    rub["criterios"] = crit
    rub["total_maximo"] = round(sum(c["puntuacion_maxima"] for c in crit), 4)
    rub.setdefault("indicaciones", "")
    _escribir(DIR_RUBRICAS / f"{rub['id']}.json", rub)
    return rub


def borrar_rubrica(rid: str) -> None:
    (DIR_RUBRICAS / f"{rid}.json").unlink(missing_ok=True)


def hojas_excel(ruta: Path) -> list[str]:
    import openpyxl

    return openpyxl.load_workbook(ruta, read_only=True).sheetnames


def _filas_rubrica(ruta: Path, hoja: str):
    """Lee una hoja con formato Bloque | Criterio | Peso | Nivel (3) | Nivel (2) ... Devuelve None si no encaja."""
    import openpyxl

    ws = openpyxl.load_workbook(ruta, data_only=True)[hoja]
    filas = [[("" if v is None else str(v).strip()) for v in fila] for fila in ws.iter_rows(values_only=True)]
    for i, cab in enumerate(filas):
        low = [x.lower() for x in cab]
        if any(x.startswith("criterio") for x in low) and any(x.startswith("peso") for x in low):
            col_c = next(j for j, x in enumerate(low) if x.startswith("criterio"))
            col_p = next(j for j, x in enumerate(low) if x.startswith("peso"))
            col_b = next((j for j, x in enumerate(low) if x.startswith("bloque")), None)
            niveles = []
            for j in range(col_p + 1, len(cab)):
                if not cab[j]:
                    continue
                m = re.search(r"\(([\d.,]+)\)", cab[j])
                niveles.append((j, re.sub(r"\s*\(.*\)", "", cab[j]), float(m.group(1).replace(",", ".")) if m else None))
            datos = []
            for fila in filas[i + 1:]:
                fila = fila + [""] * (len(cab) - len(fila))
                bloque = fila[col_b] if col_b is not None else ""
                descriptores = [fila[j] for j, _, _ in niveles]
                try:
                    peso = float(fila[col_p].replace(",", "."))
                except ValueError:
                    continue
                if not fila[col_c] or not any(descriptores):  # filas de resumen (Cuaderno 25, TOTAL 100...)
                    continue
                datos.append({"bloque": bloque, "nombre": fila[col_c], "peso": peso,
                              "niveles": [{"nivel": n, "valor": v, "descriptor": fila[j]} for j, n, v in niveles]})
            return datos
    return None


def bloques_hoja(ruta: Path, hoja: str) -> list[str]:
    filas = _filas_rubrica(ruta, hoja) or []
    return list(dict.fromkeys(f["bloque"] for f in filas if f["bloque"]))


def importar_rubrica_excel(ruta: Path, hoja: str, bloques: list[str] | None = None, nombre: str | None = None) -> dict:
    """Convierte una pestaña del Excel en rúbrica. Sin API si la hoja tiene el formato habitual."""
    filas = _filas_rubrica(ruta, hoja)
    if filas:
        if bloques:
            filas = [f for f in filas if f["bloque"] in bloques]
        crit = [{"nombre": f["nombre"], "puntuacion_maxima": f["peso"], "descripcion": "", "niveles": f["niveles"]}
                for f in filas]
        origen = f"{Path(ruta).name} · {hoja}" + (f" · {', '.join(bloques)}" if bloques else "")
    else:
        raise ErrorAgente("La pestaña no tiene el formato Bloque | Criterio | Peso | niveles: "
                          "crea la rúbrica a mano (rubricas/<id>.json).")
    if not crit:
        raise ErrorAgente("No he encontrado criterios en esa pestaña.")
    return {"nombre": nombre or f"{hoja}" + (f" ({', '.join(bloques)})" if bloques else ""),
            "origen": origen, "criterios": crit, "indicaciones": "",
            "total_maximo": round(sum(c["puntuacion_maxima"] for c in crit), 4)}


# ---------- Prácticas ----------

def listar_practicas() -> list[dict]:
    return sorted((_leer(p) for p in DIR_PRACTICAS.glob("*/practica.json")), key=lambda r: r["titulo"].lower())


def cargar_practica(pid: str) -> dict:
    return _leer(DIR_PRACTICAS / pid / "practica.json")


def guardar_practica(pra: dict) -> dict:
    pra = dict(pra)
    pra["id"] = pra.get("id") or slug(pra["titulo"])
    pra.setdefault("indicaciones", "")
    _escribir(DIR_PRACTICAS / pra["id"] / "practica.json", pra)
    return pra


def borrar_practica(pid: str) -> None:
    import shutil

    shutil.rmtree(DIR_PRACTICAS / pid, ignore_errors=True)


def adjuntar_guion(pra: dict, ruta_guion: Path) -> dict:
    """Copia el guion dentro de la carpeta de la práctica (se usa para descontarlo en la similitud)."""
    import shutil

    destino = DIR_PRACTICAS / pra["id"] / f"guion{Path(ruta_guion).suffix.lower()}"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if Path(ruta_guion).resolve() != destino.resolve():
        shutil.copy(ruta_guion, destino)
    pra["guion"] = str(destino.relative_to(BIBLIOTECA))
    return pra


def _texto_guion(pra: dict) -> str:
    ruta = BIBLIOTECA / pra.get("guion", "__no__")
    if not ruta.is_file():
        return ""
    if ruta.suffix == ".pdf":
        return texto_pdf(ruta)
    if ruta.suffix == ".docx":
        return texto_docx(ruta)
    return ruta.read_text(encoding="utf-8", errors="ignore")


# ---------- Revisión de coherencia ----------


def resumen_tanda(resultados: list[dict], rubrica: dict) -> str:
    """Tabla compacta de toda la tanda para comparar criterios entre alumnos."""
    lineas = []
    for r in resultados:
        lineas.append(f"### {r.get('alumno') or r['archivo']}  (archivo: {r['archivo']})")
        for c in r["criterios"]:
            marca = " [REVISAR]" if c.get("revisar") else ""
            lineas.append(f"- {c['criterio']} (peso {c.get('maximo', '')}): nivel {c.get('nivel')}{marca} — {c.get('comentario', '')}")
        errs = [f"{x.get('descripcion', '')}: {x.get('tipo')}" for x in r.get("calculos", []) if x.get("tipo") not in ("correcto", None)]
        if errs:
            lineas.append("- Cálculos con discrepancias: " + "; ".join(errs))
        lineas.append("")
    return "\n".join(lineas)


INSTRUCCIONES_COHERENCIA = """Ya has corregido todos los informes de esta tanda uno a uno. Ahora haz \
una revisión de coherencia de la tanda completa, como haría un profesor al repasar las notas:

1. Compara criterio a criterio entre alumnos. El mismo error o la misma carencia debe tener el mismo \
nivel en todos los informes; un informe claramente mejor que otro en un criterio no puede tener menos \
nivel. Aplica los errores_frecuentes de la práctica si los hay.
2. Revisa los criterios marcados REVISAR: si con la visión de conjunto el caso queda claro, propón el \
nivel y quita la marca; si sigue siendo una decisión del profesor, déjalo en revisar=true.
3. Comprueba que ningún error se ha penalizado dos veces (origen y consecuencias).
4. Propón solo los ajustes necesarios (no repitas los criterios que no cambian). En cada ajuste da el \
comentario final de la celda y el motivo.
5. En errores_frecuentes_sugeridos, recoge errores que se repiten en varios alumnos de esta tanda y que \
no estén ya en errores_frecuentes, con el criterio y cómo los has puntuado, para que el profesor decida \
si los añade a la práctica."""


def anadir_errores_frecuentes(pid: str, nuevos: list[dict]) -> int:
    """Añade errores a la práctica sin duplicar (por el texto del error)."""
    pra = cargar_practica(pid)
    actuales = pra.setdefault("errores_frecuentes", [])
    vistos = {e["error"].strip().lower() for e in actuales}
    n = 0
    for e in nuevos:
        if e.get("error", "").strip() and e["error"].strip().lower() not in vistos:
            actuales.append({k: e.get(k, "") for k in ("error", "criterio", "como_puntuar")})
            vistos.add(e["error"].strip().lower())
            n += 1
    guardar_practica(pra)
    return n
