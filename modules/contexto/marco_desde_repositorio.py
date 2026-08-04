# -*- coding: utf-8 -*-
"""
modules/contexto/marco_desde_repositorio.py
===========================================

REGLA CX — Propuesta / clasificación de O a partir del repositorio
y de la conversación (o de un contexto declarado de antemano).

QUÉ ES
------
Da libertad al sistema para *armar un marco O usable* de dos modos:

  1) Contexto PREDECLARADO
     La petición ya trae O_id + enunciado_O (o contexto/O_context).
     CX lo respeta y clasifica estabilidad / evento.

  2) Contexto DESDE LA CONVERSACIÓN
     La petición trae texto/mensaje/diálogo sin O fijo.
     CX propone O_id + enunciado_O anclado a:
       - señales de dominio en el texto (filosofía, matemáticas, …)
       - foco de sujeto si aparece (p.ej. María, Carlo)
       - escala (palabra / frase / turno / conversación / repo)
       - conocimiento ya cargado del grafo (dominios AX, no invenciones)

Un mismo material puede admitir *varios* O válidos (más general, más
local, otro sujeto, otro dominio). Esta regla no afirma unicidad:
si se pide "otro contexto", marca evento de cambio/expansión y deja
preparado un nuevo marco. La verdad de *cada* O se evalúa después
bajo CA (Tru_Ri / Tru_total por marco); CX no calcula.

QUÉ NO ES
---------
No calcula Tru, C, L, K ni E.
No compara numéricamente "quién tiene más verdad" (eso es CA bajo cada O).
No emite cadena (CIT).
No orquesta el bucle (Engine).
No inventa axiomas.

FLUJO QUE PROTEGE
-----------------
  conversación y/o O previo
       → CX propone/clasifica O   (este archivo)
       → Engine orquesta
       → conteos / CA calculan bajo ese O
  Si el O estaba mal → el error se ve porque el marco quedó declarado
  *antes* de calcular (orden CX → CA).

ANCLAS
------
  CX-A1, CX-A3, CX-A8, CX-A10, CX-A14, CX-A23, CX-A25
  CX-T6, CX-T15, CX-OP-1, CX-OP-2
  Def-5.3.1, IND-D1, IND-A1, IND-A5
  TA3, TA4, TA5, EF-A4, EF-T2 (multi-O sin colapso)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# REGLA
# ---------------------------------------------------------------------------
REGLA: Dict[str, Any] = {
    "id": "CX-R-MARCO-REPO",
    "nombre": "marco_desde_repositorio",
    "version": "1.0",
    "descripcion": (
        "Propone y clasifica O_context a partir del repositorio y de la "
        "conversación, o respeta un O predeclarado. Admite varios marcos "
        "válidos sobre el mismo material (otro sujeto, otra escala, otro "
        "dominio). No calcula Tru. No asigna K numérico. No afirma que el "
        "O propuesto sea el único posible."
    ),
    "anclas_cx": [
        "CX-A1",
        "CX-A3",
        "CX-A8",
        "CX-A10",
        "CX-A14",
        "CX-A23",
        "CX-A25",
        "CX-T6",
        "CX-T15",
        "CX-OP-1",
        "CX-OP-2",
        "Def-5.3.1",
        "IND-D1",
        "IND-A1",
        "IND-A5",
        "TA3",
        "TA4",
        "TA5",
        "EF-A4",
        "EF-T2",
    ],
}

# Dominios reconocibles en prosa → etiqueta corta para O_id / enunciado
_DOMINIOS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("filosofia", (
        "filosofia", "filosofía", "ontolog", "epistemolog", "metafis",
        "etica", "ética", "philosophy", "metaphysics",
    )),
    ("matematicas", (
        "matematic", "matemátic", "ecuacion", "ecuación", "algebra",
        "álgebra", "geometr", "calculo", "cálculo", "teorema", "lema",
        "demostracion", "demostración", "math", "equation", "proof",
    )),
    ("logica", (
        "logica", "lógica", "inferencia", "contradiccion", "contradicción",
        "implicacion", "implicación", "logic", "entailment",
    )),
    ("fisica", (
        "fisica", "física", "energia", "energía", "cuantic", "cuántic",
        "relativid", "physics", "quantum",
    )),
    ("biologia", (
        "biolog", "celular", "genet", "genét", "organismo", "biology",
    )),
    ("medicina", (
        "medicin", "clinic", "clínic", "diagnost", "diagnóst", "terapia",
        "medicine", "clinical",
    )),
    ("astronomia", (
        "astronom", "cosmolog", "galaxia", "planeta", "astronomy", "cosmos",
    )),
    ("tecnologia", (
        "tecnolog", "software", "algoritmo", "comput", "codigo", "código",
        "repositorio", "modulo", "módulo", "technology", "engine",
    )),
    ("auditoria_sistema", (
        "auto auditor", "auto-auditor", "auditoria interna", "auditoría interna",
        "auditar el sistema", "auditar modulos", "auditar módulos",
        "coherencia del repo", "system audit",
    )),
    ("estabilizacion_operativa", (
        "entendimiento operativo", "bucle de correlacion", "bucle de correlación",
        "saturacion de material", "saturación de material", "fractal semant",
        "fractal semánt", "operational understanding",
    )),
    ("conversacion", (
        "conversacion", "conversación", "dialogo", "diálogo", "turno",
        "mensaje", "conversation", "dialogue",
    )),
)

_SENALES_OTRO_CONTEXTO: Tuple[str, ...] = (
    "otro contexto",
    "otro marco",
    "contexto distinto",
    "marco distinto",
    "contexto mas general",
    "contexto más general",
    "contexto mas amplio",
    "contexto más amplio",
    "contexto mas local",
    "contexto más local",
    "cambia el contexto",
    "cambiar contexto",
    "busca otro contexto",
    "genera otro contexto",
    "reescribe el contexto",
    "another context",
    "different frame",
    "broader context",
    "narrower context",
)

_SENALES_ESCALA: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("atomo", ("una palabra", "solo la palabra", "single word", "atomo", "átomo")),
    ("frase", ("una frase", "esta frase", "esta oración", "esta oracion", "one sentence")),
    ("turno", ("este turno", "este mensaje", "mi mensaje", "tu respuesta")),
    ("sujeto", (
        "de maria", "de maría", "de carlo", "de el", "de ella",
        "lo que dijo", "lo que dice", "truri de", "tru_ri de", "tru de",
    )),
    ("conversacion", (
        "toda la conversacion", "toda la conversación", "el dialogo",
        "el diálogo", "whole conversation", "entire dialogue",
    )),
    ("repositorio", (
        "todo el repo", "el repositorio", "el sistema completo",
        "whole repository", "entire system",
    )),
)

_TIPOS: List[str] = [
    "dame_O",
    "dame_normas",
    "dame_limites",
    "dame_evidencia",
    "por_que_valor",
    "dame_cadena_completa",
]

_O_ID_PREFIJO = "O_marco_repo"


def _texto_entrada(peticion: Dict[str, Any]) -> str:
    partes: List[str] = []
    for k in (
        "contexto",
        "O_context",
        "Octx",
        "enunciado_O",
        "enunciado",
        "texto",
        "descripcion",
        "objetivo",
        "tarea",
        "mensaje",
        "conversacion",
        "dialogo",
        "diálogo",
        "historial",
    ):
        v = peticion.get(k)
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            partes.extend(str(x).strip() for x in v if str(x).strip())
        else:
            s = str(v).strip()
            if s:
                partes.append(s)
    for flag in (
        "generar_contexto",
        "proponer_O",
        "otro_contexto",
        "marco_desde_repo",
    ):
        if peticion.get(flag) is True:
            partes.append(flag.replace("_", " "))
    modo = peticion.get("modo_entrada") or peticion.get("modo")
    if modo:
        partes.append(str(modo).strip())
    return " ".join(partes).lower()


def _o_predeclarado(peticion: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Modo 1: contexto ya traído por el usuario / Engine."""
    o_id = peticion.get("O_id") or peticion.get("o_id")
    enunciado = (
        peticion.get("enunciado_O")
        or peticion.get("enunciado")
        or peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("Octx")
    )
    o_id_ok = bool(o_id and str(o_id).strip()) and str(o_id).strip().lower() not in (
        "undefined", "indefinido", "none", "null", "∅",
    )
    en_ok = bool(enunciado and str(enunciado).strip()) and str(enunciado).strip().lower() not in (
        "undefined", "indefinido", "none", "null", "∅",
    )
    return (
        str(o_id).strip() if o_id_ok else None,
        str(enunciado).strip() if en_ok else None,
    )


def _detectar_dominios(texto: str, peticion: Dict[str, Any]) -> List[str]:
    hallados: List[str] = []
    # explícito
    for k in ("dominio", "dominios", "campo", "disciplina"):
        v = peticion.get(k)
        if v is None:
            continue
        items = v if isinstance(v, (list, tuple)) else [v]
        for it in items:
            s = str(it).strip().lower()
            if s and s not in hallados:
                hallados.append(s)
    for nombre, senales in _DOMINIOS:
        if any(s in texto for s in senales):
            if nombre not in hallados:
                hallados.append(nombre)
    return hallados


def _detectar_escala(texto: str, peticion: Dict[str, Any]) -> str:
    esc = peticion.get("escala")
    if esc and str(esc).strip():
        return str(esc).strip().lower()
    for nombre, senales in _SENALES_ESCALA:
        if any(s in texto for s in senales):
            return nombre
    # heurística suave: texto muy corto → frase/átomo; largo → conversacion
    puro = re.sub(r"\s+", " ", texto).strip()
    if len(puro.split()) <= 3:
        return "atomo"
    if len(puro.split()) <= 25:
        return "frase"
    return "conversacion"


def _detectar_sujetos(texto: str, peticion: Dict[str, Any]) -> List[str]:
    """Focos nominales simples (María, Carlo, …) si la petición o el texto los traen."""
    sujetos: List[str] = []
    for k in ("sujeto", "sujetos", "foco", "agente", "hablante"):
        v = peticion.get(k)
        if v is None:
            continue
        items = v if isinstance(v, (list, tuple)) else [v]
        for it in items:
            s = str(it).strip()
            if s and s not in sujetos:
                sujetos.append(s)
    # nombres capitalizados en el texto original (si vino)
    raw = (
        peticion.get("texto")
        or peticion.get("mensaje")
        or peticion.get("conversacion")
        or peticion.get("enunciado_O")
        or ""
    )
    if isinstance(raw, (list, tuple)):
        raw = " ".join(str(x) for x in raw)
    for m in re.finditer(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})\b", str(raw)):
        nom = m.group(1)
        # evita palabras típicas de inicio de frase no-nombre
        if nom.lower() in (
            "el", "la", "los", "las", "una", "uno", "esto", "esta", "ese",
            "esa", "the", "this", "that", "hola", "bueno", "entonces",
        ):
            continue
        if nom not in sujetos:
            sujetos.append(nom)
    return sujetos[:8]  # cota operativa, no ontológica


def _pide_otro_contexto(texto: str, peticion: Dict[str, Any]) -> bool:
    if peticion.get("otro_contexto") is True:
        return True
    if peticion.get("pedir_otro_marco") is True:
        return True
    return any(s in texto for s in _SENALES_OTRO_CONTEXTO)


def _hay_material(texto: str, peticion: Dict[str, Any]) -> bool:
    if texto.strip():
        return True
    for k in ("texto", "mensaje", "conversacion", "dialogo", "diálogo", "historial"):
        if peticion.get(k):
            return True
    return False


def _proponer_o_id(dominios: List[str], escala: str, sujetos: List[str], otro: bool) -> str:
    partes = [_O_ID_PREFIJO]
    if dominios:
        partes.append(dominios[0][:24])
    if sujetos:
        partes.append(re.sub(r"[^A-Za-z0-9_]", "", sujetos[0])[:20] or "sujeto")
    partes.append(escala[:16])
    if otro:
        partes.append("alt")
    return "_".join(partes)


def _proponer_enunciado(
    dominios: List[str],
    escala: str,
    sujetos: List[str],
    otro: bool,
    texto: str,
) -> str:
    dom = ", ".join(dominios) if dominios else "dominio derivable del material"
    focos = ", ".join(sujetos) if sujetos else "sin foco de sujeto nominal explícito"
    fragmento = re.sub(r"\s+", " ", texto).strip()
    if len(fragmento) > 180:
        fragmento = fragmento[:177] + "..."
    base = (
        f"Marco O propuesto desde repositorio + material de entrada. "
        f"Dominios señalados: {dom}. Escala: {escala}. Foco(s): {focos}."
    )
    if fragmento:
        base += f" Material de anclaje: «{fragmento}»."
    if otro:
        base += (
            " Solicitud de *otro* contexto sobre el mismo material: "
            "este marco no sustituye ni borra marcos previos (CX-A25 / EF-T2); "
            "cada O se evalúa por separado bajo CA."
        )
    else:
        base += (
            " Este O es un marco evaluable, no el único posible sobre el material. "
            "Puede pedirse otro contexto (más general, más local, otro sujeto)."
        )
    base += (
        " CX clasifica; no calcula Tru_Ri ni Tru_total. "
        "La comparación entre sujetos o marcos es posterior (CA bajo cada O)."
    )
    return base


def validar() -> Dict[str, Any]:
    return {
        "ok": True,
        "regla": REGLA["id"],
        "nombre": REGLA["nombre"],
        "version": REGLA["version"],
        "modos": [
            "O_predeclarado",
            "O_desde_conversacion",
            "otro_contexto_sobre_mismo_material",
        ],
        "escalas": [e[0] for e in _SENALES_ESCALA],
        "dominios_reconocidos": [d[0] for d in _DOMINIOS],
        "oficios_prohibidos": [
            "calcular Tru",
            "asignar K numérico",
            "comparar Tru entre sujetos",
            "emitir cadena CIT",
        ],
        "anclas": list(REGLA["anclas_cx"]),
    }


def clasificar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica / propone O.

    Casos:
      - Sin material y sin O → no aplica (otras reglas pueden actuar).
      - O predeclarado completo → estable (o cambio si se pide otro).
      - Material sin O → propone O anclado a dominio/escala/sujeto.
      - Pedido de otro contexto → evento cambio/expansión, nuevo O_id.

    Nunca emite Tru / C / L / K numérico.
    """
    peticion = dict(peticion or {})
    texto = _texto_entrada(peticion)
    o_id_prev, enunciado_prev = _o_predeclarado(peticion)
    otro = _pide_otro_contexto(texto, peticion)
    material = _hay_material(texto, peticion)

    # ¿Debemos actuar?
    forzar = any(
        peticion.get(f) is True
        for f in (
            "generar_contexto",
            "proponer_O",
            "marco_desde_repo",
            "otro_contexto",
            "pedir_otro_marco",
        )
    )
    if not forzar and not o_id_prev and not material and not otro:
        return {
            "ok": True,
            "oficio": "marco_desde_repositorio",
            "aplica": False,
            "ids_cx": list(REGLA["anclas_cx"]),
        }

    dominios = _detectar_dominios(texto, peticion)
    escala = _detectar_escala(texto, peticion)
    sujetos = _detectar_sujetos(texto, peticion)

    # ----- Modo 1: O predeclarado, sin pedido de "otro" -----
    if o_id_prev and enunciado_prev and not otro:
        estado_decl = peticion.get("estado")
        evento_decl = peticion.get("evento")
        if estado_decl == "cambio" or evento_decl in ("cambio", "expansion"):
            estado, evento = "cambio", (
                evento_decl if evento_decl in ("cambio", "expansion") else "cambio"
            )
            permite = False
        else:
            estado, evento = "estable", "mismo_O"
            permite = True
        return {
            "ok": True,
            "oficio": "marco_desde_repositorio",
            "aplica": True,
            "estado": estado,
            "evento": evento,
            "incompleto": False,
            "O_id": o_id_prev,
            "enunciado_O": enunciado_prev,
            "escala": peticion.get("escala") or escala,
            "modo_entrada": (
                peticion.get("modo_entrada")
                or peticion.get("modo")
                or "conversacion"
            ),
            "pedir_anuncio": bool(peticion.get("pedir_anuncio"))
            or bool(peticion.get("tipos_peticion")),
            "tipos_peticion": list(_TIPOS)
            if peticion.get("pedir_anuncio") or peticion.get("tipos_peticion")
            else [],
            "permite_k_sugerido": permite,
            "ids_cx": [
                "CX-R-MARCO-REPO",
                "CX-A1",
                "CX-A14",
                "CX-OP-1",
                "CX-OP-2",
                "Def-5.3.1",
            ],
            "mensajes": [
                "O predeclarado respetado. CX no lo reescribe. "
                "Este marco es evaluable; no es el único posible sobre el material. "
                "Para otro marco, pedir 'otro contexto' (EF-T2 / CX-A25)."
            ],
            "ligaduras": {
                "origen_marco": "predeclarado",
                "dominios": ",".join(dominios) if dominios else "segun_enunciado",
                "sujetos": ",".join(sujetos) if sujetos else "",
            },
        }

    # ----- Sin material ni O → indefinido (no fabricar) -----
    if not material and not (o_id_prev and enunciado_prev):
        return {
            "ok": True,
            "oficio": "marco_desde_repositorio",
            "aplica": True,
            "estado": "indefinido",
            "evento": "indefinido",
            "incompleto": True,
            "O_id": None,
            "enunciado_O": None,
            "pedir_anuncio": True,
            "tipos_peticion": ["dame_O", "dame_limites"],
            "permite_k_sugerido": False,
            "ids_cx": [
                "CX-R-MARCO-REPO",
                "CX-A14",
                "CX-A10",
                "Def-5.3.1",
                "IND-D1",
                "IND-A5",
            ],
            "mensajes": [
                "Pedido de marco sin material de conversación y sin O predeclarado: "
                "estado indefinido; CX no fabrica dominio (Def-5.3.1)."
            ],
        }

    # ----- Modo 2: proponer O desde conversación / otro contexto -----
    o_id = _proponer_o_id(dominios, escala, sujetos, otro=otro)
    enunciado = _proponer_enunciado(dominios, escala, sujetos, otro=otro, texto=texto)

    if otro:
        estado, evento = "cambio", "expansion"
        permite = False
        ids = [
            "CX-R-MARCO-REPO",
            "CX-A8",
            "CX-A25",
            "CX-T6",
            "CX-T15",
            "EF-A4",
            "EF-T2",
            "CX-A14",
        ]
        msg = (
            "Se propone *otro* O sobre el mismo material. "
            "No borra marcos previos (CX-A25). Cada O se calcula aparte bajo CA; "
            "comparar Tru_total(Carlo) vs Tru_total(María) es evaluación *por marco*, "
            "no oficio de CX."
        )
    else:
        estado, evento = "estable", "mismo_O"
        permite = True
        ids = [
            "CX-R-MARCO-REPO",
            "CX-A1",
            "CX-A14",
            "CX-OP-1",
            "CX-OP-2",
            "Def-5.3.1",
            "TA3",
            "EF-T2",
        ]
        msg = (
            "O propuesto desde la conversación y señales de dominio/escala/sujeto. "
            "Anclado al material; no afirma unicidad. "
            "CX clasifica antes del cálculo; conteos/CA evalúan bajo este O. "
            "Puede pedirse otro contexto (más general, más local, otro sujeto)."
        )

    return {
        "ok": True,
        "oficio": "marco_desde_repositorio",
        "aplica": True,
        "estado": estado,
        "evento": evento,
        "incompleto": False,
        "O_id": o_id,
        "enunciado_O": enunciado,
        "escala": escala,
        "modo_entrada": (
            peticion.get("modo_entrada")
            or peticion.get("modo")
            or "conversacion"
        ),
        "pedir_anuncio": bool(peticion.get("pedir_anuncio"))
        or bool(peticion.get("tipos_peticion"))
        or otro,
        "tipos_peticion": list(_TIPOS)
        if (peticion.get("pedir_anuncio") or peticion.get("tipos_peticion") or otro)
        else [],
        "permite_k_sugerido": permite,
        "ids_cx": ids,
        "mensajes": [msg],
        "ligaduras": {
            "origen_marco": "otro_contexto" if otro else "desde_conversacion",
            "dominios": ",".join(dominios) if dominios else "general",
            "sujetos": ",".join(sujetos) if sujetos else "",
            "escala": escala,
        },
    }


__all__ = ["REGLA", "clasificar", "validar"]
