"""
modules/contexto/secuencia_conversacion.py
==========================================
Regla interna CX — secuencia de tramos, multi-O y O global de mapa.

Anclas: CX-A19…A27, CX-L8…L11, CX-T14…T17, CX-C14…C18,
        CX-A8, CX-A14, CX-C8, Def-5.3.1

No calcula Tru. No asigna C, L, K numéricos.
Clasifica una conversación / sesión como familia de registros micro
y, si procede, un O global de mapa (CX-D17, CX-L10, CX-A25, CX-T15).
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

REGLA = {
    "id": "CX-R-SECUENCIA-CONV",
    "nombre": "secuencia_conversacion",
    "version": "1.0",
    "descripcion": (
        "Parte una conversación o lista de tramos en registros O micro; "
        "detecta cambio de marco solo con frontera o declaración explícita; "
        "opcionalmente arma O global de mapa sin colapsar los micro."
    ),
    "anclas_cx": [
        "CX-A19", "CX-A22", "CX-A23", "CX-A25", "CX-A27",
        "CX-L9", "CX-L10", "CX-T14", "CX-T15", "CX-T17", "CX-C18",
    ],
}


def validar() -> Dict[str, Any]:
    return {
        "ok": True,
        "regla": REGLA["id"],
        "exige": ["tramos o texto_conversacion o criterios"],
        "produce": ["tramos_clasificados", "O_global_opcional"],
        "prohibe": [
            "inferir cambio de O en silencio",
            "promediar K de micro en el global",
            "un solo Tru_total del discurso sin regla de agregacion",
        ],
    }


def _oid(texto: str, prefijo: str = "O_tramo") -> str:
    digest = hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()[:12]
    return f"{prefijo}_{digest}"


def _norm_tramo(raw: Any, idx: int) -> Dict[str, Any]:
    """
    Acepta:
      - str
      - dict con texto/contexto/enunciado_O/O_id/estado/evento/...
    """
    if isinstance(raw, str):
        texto = raw.strip()
        return {
            "tramo_id": f"T{idx}",
            "texto": texto,
            "O_id": None,
            "enunciado_O": texto or None,
            "estado_decl": None,
            "evento_decl": None,
            "cambio_declarado": False,
        }
    if not isinstance(raw, dict):
        return {
            "tramo_id": f"T{idx}",
            "texto": "",
            "O_id": None,
            "enunciado_O": None,
            "estado_decl": None,
            "evento_decl": None,
            "cambio_declarado": False,
            "error": f"tramo[{idx}] no es str ni dict",
        }

    texto = (
        raw.get("texto")
        or raw.get("contenido")
        or raw.get("enunciado")
        or raw.get("enunciado_O")
        or raw.get("contexto")
        or raw.get("O_context")
        or ""
    )
    texto = str(texto).strip()
    cambio = bool(
        raw.get("cambio_declarado")
        or raw.get("nuevo_contexto")
        or (str(raw.get("evento", "")).lower() == "cambio")
        or (str(raw.get("estado", "")).lower() == "cambio")
    )
    return {
        "tramo_id": str(raw.get("tramo_id") or raw.get("id") or f"T{idx}"),
        "texto": texto,
        "O_id": raw.get("O_id") or raw.get("o_id"),
        "enunciado_O": (raw.get("enunciado_O") or texto or None),
        "estado_decl": raw.get("estado"),
        "evento_decl": raw.get("evento"),
        "cambio_declarado": cambio,
        "modalidad": raw.get("modalidad") or raw.get("lengua") or raw.get("idioma"),
        "meta": bool(raw.get("meta")),
    }


def _extraer_tramos(peticion: Dict[str, Any]) -> List[Any]:
    if isinstance(peticion.get("tramos"), list) and peticion["tramos"]:
        return list(peticion["tramos"])
    if isinstance(peticion.get("turnos"), list) and peticion["turnos"]:
        return list(peticion["turnos"])
    if isinstance(peticion.get("criterios"), list) and peticion["criterios"]:
        # Lista de criterios = un solo O (CX-A22); se expone como un tramo lógico
        # salvo que pidan particion_explicita
        if peticion.get("particion_explicita"):
            return list(peticion["criterios"])
        return [" | ".join(str(c) for c in peticion["criterios"] if str(c).strip())]
    for k in ("texto_conversacion", "conversacion", "dialogo", "texto"):
        v = peticion.get(k)
        if isinstance(v, str) and v.strip():
            # Partir por líneas no vacías si parecen turnos "Nombre:"
            lineas = [ln.strip() for ln in v.splitlines() if ln.strip()]
            if len(lineas) >= 2:
                return lineas
            return [v.strip()]
    # Un solo bloque desde casilla
    for k in ("casilla_contexto", "contexto", "O_context", "enunciado_O"):
        v = peticion.get(k)
        if isinstance(v, str) and v.strip():
            return [v.strip()]
    return []


def clasificar(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada típica:
      {
        "tramos": [
          "Carlos: yo no tomé el dinero",
          {"texto": "ahora hablemos del clima", "cambio_declarado": true},
          "hace calor",
        ],
        "armar_o_global": true,
        "sesion_id": "S1",
      }

      # o criterios (un O):
      { "criterios": ["evaluar si es razonable", "si Carlos dijo la verdad", "..."] }

    Salida:
      tramos_clasificados[], O_global?, permite_k_sugerido (solo si hay al menos
      un micro estable), mensajes, ids_cx
    """
    peticion = dict(peticion or {})
    crudos = _extraer_tramos(peticion)
    mensajes: List[str] = []
    ids_cx: List[str] = ["CX-A19", "CX-T15"]

    if not crudos:
        mensajes.append(
            "sin tramos ni texto recuperable → secuencia indefinida "
            "(CX-A21, CX-A10)"
        )
        return {
            "ok": True,
            "estado": "indefinido",
            "evento": "indefinido",
            "tramos_clasificados": [],
            "O_global": None,
            "permite_k_sugerido": False,
            "mensajes": mensajes,
            "ids_cx": ids_cx + ["CX-A21", "CX-A10", "Def-5.3.1"],
            "armado": "secuencia_vacia",
        }

    tramos_out: List[Dict[str, Any]] = []
    o_vigente: Optional[str] = None
    enunciado_vigente: Optional[str] = None
    n_cambio = 0
    n_estable = 0
    n_indef = 0

    for i, raw in enumerate(crudos, start=1):
        t = _norm_tramo(raw, i)
        if t.get("error"):
            mensajes.append(t["error"])
            tramos_out.append({
                "tramo_id": t["tramo_id"],
                "estado": "indefinido",
                "evento": "indefinido",
                "O_id": None,
                "enunciado_O": None,
                "permite_k_sugerido": False,
                "error": t["error"],
            })
            n_indef += 1
            continue

        texto = t["texto"]
        if not texto:
            n_indef += 1
            tramos_out.append({
                "tramo_id": t["tramo_id"],
                "estado": "indefinido",
                "evento": "indefinido",
                "O_id": None,
                "enunciado_O": None,
                "permite_k_sugerido": False,
                "mensajes": ["tramo vacío"],
            })
            continue

        # Meta / indefinido declarado en el tramo
        if t.get("meta") or (t.get("estado_decl") == "indefinido"):
            n_indef += 1
            oid = t["O_id"] or _oid(texto, "O_meta")
            tramos_out.append({
                "tramo_id": t["tramo_id"],
                "estado": "indefinido",
                "evento": "indefinido",
                "O_id": oid,
                "enunciado_O": texto,
                "permite_k_sugerido": False,
                "meta": True,
                "modalidad": t.get("modalidad"),
            })
            ids_cx.append("CX-C15")
            continue

        # Cambio explícito (CX-A23): nuevo O; no inferencia silenciosa
        if t["cambio_declarado"] or t.get("estado_decl") == "cambio":
            n_cambio += 1
            oid = t["O_id"] or _oid(texto, "O_cambio")
            o_vigente = oid
            enunciado_vigente = t["enunciado_O"] or texto
            tramos_out.append({
                "tramo_id": t["tramo_id"],
                "estado": "cambio",
                "evento": "cambio",
                "O_id": oid,
                "enunciado_O": enunciado_vigente,
                "permite_k_sugerido": True,
                "modalidad": t.get("modalidad"),
                "mensajes": [
                    "cambio de O por frontera/declaracion (CX-A23); "
                    "cierra marco anterior y abre este"
                ],
            })
            ids_cx.extend(["CX-A23", "CX-T6"])
            continue

        # Continuación bajo O vigente o primer tramo (mismo_O / estable)
        if t["O_id"]:
            oid = str(t["O_id"])
            # Si el caller pone otro O_id sin marcar cambio → se respeta como
            # frontera explícita de identidad (no silencio: el id distinto es frontera)
            if o_vigente and oid != o_vigente:
                n_cambio += 1
                evento = "cambio"
                estado = "cambio"
                mensajes.append(
                    f"{t['tramo_id']}: O_id distinto al vigente sin flag; "
                    "tratado como frontera explícita de O (CX-A23)"
                )
                ids_cx.append("CX-A23")
            else:
                evento = "mismo_O" if o_vigente else "mismo_O"
                estado = "estable"
                n_estable += 1
            o_vigente = oid
            enunciado_vigente = t["enunciado_O"] or texto
        else:
            if o_vigente is None:
                oid = _oid(texto, "O_sesion")
                o_vigente = oid
                enunciado_vigente = t["enunciado_O"] or texto
                evento = "mismo_O"
                estado = "estable"
                n_estable += 1
                mensajes.append(
                    f"{t['tramo_id']}: primer marco de secuencia; O interno asignado"
                )
            else:
                # Misma sesión: expansión / mismo O (CX-T4); no se inventa cambio
                oid = o_vigente
                evento = "expansion"
                estado = "estable"
                n_estable += 1
                # enunciado del tramo es contenido bajo O vigente, no nuevo O
                enunciado_vigente = enunciado_vigente or texto

        # Modalidad (CX-A26): se registra; no fuerza cambio
        if t.get("modalidad"):
            ids_cx.append("CX-A26")

        tramos_out.append({
            "tramo_id": t["tramo_id"],
            "estado": estado,
            "evento": evento,
            "O_id": oid,
            "enunciado_O": (
                enunciado_vigente if evento in ("mismo_O", "expansion")
                else (t["enunciado_O"] or texto)
            ),
            "texto_tramo": texto,
            "permite_k_sugerido": estado == "estable" or estado == "cambio",
            "modalidad": t.get("modalidad"),
        })
        ids_cx.extend(["CX-A14", "CX-T14"])

    # --- O global de mapa (opcional, CX-L10 / CX-A25 / CX-C18) ---
    armar_global = bool(
        peticion.get("armar_o_global", True)
        and len(tramos_out) >= 1
    )
    o_global = None
    if armar_global:
        partes = []
        for tr in tramos_out:
            partes.append(
                f"{tr.get('tramo_id')}:{tr.get('estado')}:{tr.get('O_id')}"
            )
        mapa = (
            "Mapa conversacional — tramos: "
            + "; ".join(
                f"{tr.get('tramo_id')}[{tr.get('evento')}] "
                f"O={tr.get('O_id')} «{(tr.get('texto_tramo') or tr.get('enunciado_O') or '')[:60]}»"
                for tr in tramos_out
            )
        )
        o_global = {
            "O_id": _oid(mapa, "O_global"),
            "enunciado_O": mapa,
            "estado": "estable" if tramos_out else "indefinido",
            "evento": "mapa",
            "tipo": "O_global",
            "n_tramos": len(tramos_out),
            "n_estable": n_estable,
            "n_cambio": n_cambio,
            "n_indefinido": n_indef,
            "O_micro_ids": sorted({
                tr["O_id"] for tr in tramos_out if tr.get("O_id")
            }),
            "permite_k_sugerido": bool(tramos_out),
            "nota": (
                "K de este O mide el mapa, no cada micro (CX-C18, CX-A25). "
                "No promedia Tru de los tramos."
            ),
        }
        ids_cx.extend(["CX-L10", "CX-A25", "CX-C18"])
        mensajes.append(
            "O global de mapa armado; no colapsa O micro ni agrega K local"
        )

    # Criterios bajo un O (CX-A22 / L9) si vino lista sin particion
    if (
        isinstance(peticion.get("criterios"), list)
        and len(peticion["criterios"]) >= 2
        and not peticion.get("particion_explicita")
    ):
        ids_cx.extend(["CX-A22", "CX-L9"])
        mensajes.append(
            "criterios tratados como un solo O (no multi-O por defecto)"
        )

    hay_micro_util = any(
        tr.get("permite_k_sugerido") for tr in tramos_out
    )

    return {
        "ok": True,
        "estado": (
            "estable" if n_estable and not n_cambio and not n_indef
            else "mixto" if tramos_out else "indefinido"
        ),
        "evento": "secuencia",
        "tramos_clasificados": tramos_out,
        "O_global": o_global,
        "resumen": {
            "n_tramos": len(tramos_out),
            "n_estable": n_estable,
            "n_cambio": n_cambio,
            "n_indefinido": n_indef,
            "O_distintos": sorted({
                tr["O_id"] for tr in tramos_out if tr.get("O_id")
            }),
        },
        "permite_k_sugerido": hay_micro_util,
        "mensajes": mensajes,
        "ids_cx": sorted(set(ids_cx)),
        "armado": "secuencia_conversacion",
        "nota_evaluacion": (
            "Evaluar por tramo (familia de resultados). "
            "Sin regla de agregacion declarada no hay un solo Tru_total "
            "del discurso (CX-T15, CX-T17)."
        ),
    }
