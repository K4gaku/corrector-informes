#!/usr/bin/env python3
"""Herramientas de la skill corregir-informes (las usa Claude; no hace falta API).

  python3 herramientas.py biblioteca
      Lista las rúbricas y prácticas guardadas.

  python3 herramientas.py importar-rubrica <excel> [--hoja <pestaña>] [--bloques Informe] [--nombre <nombre>]
      Sin --hoja, muestra las pestañas y sus bloques. Con --hoja, importa y guarda la rúbrica.

  python3 herramientas.py instrucciones --practica <id> [--rubrica <id>] [--modulo AIN]
      Muestra las instrucciones de corrección (rúbrica + práctica + reglas) y el formato JSON
      que hay que escribir para cada informe.

  python3 herramientas.py resumen <carpeta_tanda> --practica <id> [--rubrica <id>]
      Muestra todas las correcciones de la tanda juntas (criterio a criterio) y los errores
      frecuentes de la práctica, para la revisión de coherencia.

  python3 herramientas.py excel <carpeta_tanda> --practica <id> [--rubrica <id>] [--sobre 70]
      Lee <carpeta_tanda>/detalle/*.json, los valida y genera el Excel de la tanda.
      Los PDF deben estar en <carpeta_tanda>/informes/.
"""

import argparse
import json
import sys
from pathlib import Path

import corrector_lab as core


def cargar(args):
    pra = core.cargar_practica(args.practica)
    rid = args.rubrica or pra.get("rubrica_id")
    if not rid:
        raise core.ErrorAgente("La práctica no tiene rúbrica por defecto: indica --rubrica.")
    return pra, core.cargar_rubrica(rid)


def validar(datos: dict, rub: dict, nombre: str) -> list[str]:
    errores = []
    for campo in ("alumno", "criterios", "feedback_general", "sospecha_ia"):
        if campo not in datos:
            errores.append(f"{nombre}: falta el campo «{campo}»")
    validos = {c["nombre"] for c in rub["criterios"]}
    vistos = set()
    for c in datos.get("criterios", []):
        if c.get("criterio") not in validos:
            errores.append(f"{nombre}: criterio desconocido «{c.get('criterio')}» (válidos: {', '.join(validos)})")
        if c.get("nivel") not in core.NIVELES:
            errores.append(f"{nombre}: nivel {c.get('nivel')!r} en «{c.get('criterio')}»; debe ser uno de {core.NIVELES}")
        vistos.add(c.get("criterio"))
    for falta in validos - vistos:
        errores.append(f"{nombre}: falta el criterio «{falta}»")
    return errores


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):  # consola de Windows: evita errores con tildes y ė
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("biblioteca")
    m = sub.add_parser("importar-rubrica")
    m.add_argument("excel", type=Path)
    m.add_argument("--hoja")
    m.add_argument("--bloques", nargs="*")
    m.add_argument("--nombre")
    i = sub.add_parser("instrucciones")
    i.add_argument("--practica", required=True)
    i.add_argument("--rubrica")
    i.add_argument("--modulo")
    r = sub.add_parser("resumen")
    r.add_argument("carpeta", type=Path)
    r.add_argument("--practica", required=True)
    r.add_argument("--rubrica")
    e = sub.add_parser("excel")
    e.add_argument("carpeta", type=Path)
    e.add_argument("--practica", required=True)
    e.add_argument("--rubrica")
    e.add_argument("--sobre", type=float)
    a = p.parse_args()

    try:
        if a.cmd == "biblioteca":
            print("Rúbricas:")
            for x in core.listar_rubricas():
                print(f"  {x['id']:40} {x['nombre']} (total {x['total_maximo']:g}): "
                      + ", ".join(f"{c['nombre']} {c['puntuacion_maxima']:g}" for c in x["criterios"]))
            print("Prácticas:")
            for x in core.listar_practicas():
                print(f"  {x['id']:40} {x['titulo']} [rúbrica: {x.get('rubrica_id') or '—'}; "
                      f"{len(x.get('errores_frecuentes', []))} errores frecuentes; "
                      f"{len(list((core.DIR_PRACTICAS / x['id'] / 'tandas').glob('*/')))} tandas]")
            return 0

        if a.cmd == "importar-rubrica":
            if not a.hoja:
                for h in core.hojas_excel(a.excel):
                    bl = core.bloques_hoja(a.excel, h)
                    print(f"  {h}" + (f"  (bloques: {', '.join(bl)})" if bl else ""))
                return 0
            rub = core.guardar_rubrica(core.importar_rubrica_excel(a.excel, a.hoja, a.bloques, a.nombre))
            print(f"Guardada «{rub['nombre']}» (id {rub['id']}), total {rub['total_maximo']:g}: "
                  + ", ".join(f"{c['nombre']} {c['puntuacion_maxima']:g}" for c in rub["criterios"]))
            return 0

        pra, rub = cargar(a)
        if a.cmd == "instrucciones":
            print(core.instrucciones_correccion(rub, pra, a.modulo))
            print("\n\nFORMATO: escribe un JSON por informe en <tanda>/detalle/<nombre_del_pdf_sin_extension>.json "
                  "que cumpla este esquema (nivel: 0, 0.5, 1, 1.5, 2, 2.5 o 3):\n")
            print(json.dumps(core.esquema_correccion(rub), ensure_ascii=False, indent=1))
            return 0

        if a.cmd == "resumen":
            res, errs = [], []
            for ruta in sorted((a.carpeta / "detalle").glob("*.json")):
                datos = json.loads(ruta.read_text(encoding="utf-8"))
                e = validar(datos, rub, ruta.name)
                if e:
                    errs += e
                    continue
                datos.setdefault("archivo", ruta.stem + ".pdf")
                res.append(core.normalizar_resultado(datos, rub))
            if errs:
                print("Corrige estos JSON antes:\n  " + "\n  ".join(errs))
                return 1
            print(core.INSTRUCCIONES_COHERENCIA + "\n")
            print("ERRORES FRECUENTES DE LA PRÁCTICA:")
            for x in pra.get("errores_frecuentes", []) or [{"error": "(ninguno)", "criterio": "", "como_puntuar": ""}]:
                print(f"- [{x['criterio']}] {x['error']} → {x['como_puntuar']}")
            print("\nCORRECCIONES DE LA TANDA:\n")
            print(core.resumen_tanda(res, rub))
            return 0

        carpeta = a.carpeta
        pdfs = sorted(x for x in (carpeta / "informes").glob("*") if x.suffix.lower() == ".pdf")
        detalles = {x.stem: x for x in (carpeta / "detalle").glob("*.json")}
        errores, resultados, faltan = [], [], []
        for pdf in pdfs:
            ruta = detalles.get(pdf.stem)
            if not ruta:
                faltan.append(pdf.stem)
                continue
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            errs = validar(datos, rub, ruta.name)
            if errs:
                errores += errs
                continue
            datos["archivo"] = pdf.name
            resultados.append(datos)
        if errores:
            print("Corrige estos JSON y vuelve a ejecutar:\n  " + "\n  ".join(errores))
            return 1

        sim = core.similitudes({r["archivo"]: core.texto_pdf(carpeta / "informes" / r["archivo"]) for r in resultados},
                               core._texto_guion(pra))
        ordenados = []
        for r in resultados:
            r = core.normalizar_resultado(r, rub)
            r["alumno_mostrado"] = r.get("alumno") or Path(r["archivo"]).stem
            r["avisos"] = core.construir_avisos(r, sim.get(r["archivo"], [])) + r.get("avisos_extra", [])
            (carpeta / "detalle" / f"{Path(r['archivo']).stem}.json").write_text(
                json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            ordenados.append(r)
        ordenados.sort(key=lambda r: r["alumno_mostrado"].lower())
        no_corr = [(n, "Informe sin corregir (falta su JSON en detalle/)") for n in faltan]
        salida = carpeta / f"correccion_{pra['id']}_{carpeta.name}.xlsx"
        core.escribir_excel(ordenados, no_corr, rub, salida, a.sobre)

        con_revisar = [r["alumno_mostrado"] for r in ordenados
                       if any(c["revisar"] for c in r["criterios"]) or not r.get("practica_coincide", True)] + faltan
        print(f"Informes corregidos: {len(ordenados)} de {len(pdfs)}.")
        print("Con celdas en REVISAR: " + (", ".join(con_revisar) or "ninguno") + ".")
        print(f"Excel: {salida}")
        return 0
    except FileNotFoundError as ex:
        print(f"No encontrado: {ex.filename}")
        return 1
    except core.ErrorAgente as ex:
        print(f"Error: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
