"""
VPSI-TRUTH --- modules/realidad/_base_dominio.py

Utilidades compartidas para disciplinas de conocimiento humano.
No declara FUNCION: no es un dominio; es soporte de contrato.

Cada disciplina debe:
  1. Declarar FUNCION con contrato de simbiosis.
  2. Usar Canal de modules.realidad.acceso (no reimplementar red).
  3. Etiquetar material; no afirmar R ni Tru.
  4. Pedir evaluación a Engine bajo su O.
  5. Aprobar o rechazar antes de que el material suba.
  6. No calcular C, L, K ni Tru.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

ESTADOS_MATERIAL = (
    "pendiente",
    "evaluado",
    "aprobado",
    "rechazado",
    "bloqueado_re",
)

CATEGORIA = "conocimiento_humano"


def material_id(origen: str, cuerpo_preview: str = "") -> str:
    base = (origen or "").strip() + "||" + (cuerpo_preview or "")[:200]
    return "mat_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def etiquetar(
    *,
    dominio: str,
    origen: str,
    tipo: str,
    cuerpo: Any,
    url: Optional[str] = None,
    metadatos: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    preview = ""
    if isinstance(cuerpo, (bytes, bytearray)):
        preview = cuerpo[:200].decode("utf-8", errors="replace")
    elif cuerpo is not None:
        preview = str(cuerpo)[:200]

    return {
        "material_id": material_id(origen or url or dominio, preview),
        "dominio": dominio,
        "categoria": CATEGORIA,
        "origen": origen,
        "url": url,
        "tipo": tipo,
        "cuerpo": cuerpo,
        "metadatos": dict(metadatos or {}),
        "estado": "pendiente",
        "nota": (
            "Candidato a contraste. No es ancla de R. "
            "Requiere evaluación bajo O del dominio y aprobación local."
        ),
    }


def peticion_evaluacion_engine(
    *,
    dominio: str,
    material: Dict[str, Any],
    o_evaluacion: str,
    modo_entrada: str = "auditoria",
) -> Dict[str, Any]:
    return {
        "modo_entrada": modo_entrada,
        "O_id": "O_{0}".format(dominio),
        "enunciado_O": o_evaluacion,
        "O_context": o_evaluacion,
        "descripcion": material.get("origen") or material.get("material_id"),
        "mensaje": (
            (material.get("metadatos") or {}).get("resumen")
            or material.get("origen")
            or ""
        ),
        "material_id": material.get("material_id"),
        "dominio_realidad": dominio,
        "categoria": CATEGORIA,
        "contexto": o_evaluacion,
    }


def aplicar_aprobacion(
    material: Dict[str, Any],
    resultado_engine: Dict[str, Any],
    aprobar: bool,
    motivo: str = "",
) -> Dict[str, Any]:
    out = dict(material)
    out["estado"] = "aprobado" if aprobar else "rechazado"
    out["resultado_engine"] = {
        "presente": isinstance(resultado_engine, dict),
        "claves": list(resultado_engine.keys()) if isinstance(resultado_engine, dict) else [],
    }
    out["aprobacion_dominio"] = bool(aprobar)
    out["motivo_aprobacion"] = motivo or (
        "aprobado por contrato de dominio" if aprobar else "rechazado por contrato de dominio"
    )
    return out


def traer_url(
    *,
    dominio: str,
    url: str,
    tipo: str = "recurso",
    metadatos: Optional[Dict[str, Any]] = None,
    canal: Any = None,
) -> Dict[str, Any]:
    meta = dict(metadatos or {})
    meta.setdefault("disciplina", dominio)
    meta.setdefault("categoria", CATEGORIA)

    try:
        from modules.realidad.acceso import Canal, hay_acceso
    except Exception as e:
        mat = etiquetar(
            dominio=dominio,
            origen=url,
            tipo=tipo,
            cuerpo=b"",
            url=url,
            metadatos={**meta, "error": "acceso_no_importable: {0}".format(e)},
        )
        mat["estado"] = "rechazado"
        mat["motivo_aprobacion"] = "módulo acceso no disponible"
        return mat

    if not hay_acceso(timeout=2):
        mat = etiquetar(
            dominio=dominio,
            origen=url,
            tipo=tipo,
            cuerpo=b"",
            url=url,
            metadatos={**meta, "error": "sin_acceso_internet"},
        )
        mat["estado"] = "rechazado"
        mat["motivo_aprobacion"] = "sin acceso a Internet"
        return mat

    propio = canal is None
    c = canal or Canal()
    try:
        if propio:
            c.abrir()
        resp = c.obtener(url)
    finally:
        if propio:
            try:
                c.cerrar()
            except Exception:
                pass

    if resp.get("error"):
        mat = etiquetar(
            dominio=dominio,
            origen=url,
            tipo=tipo,
            cuerpo=b"",
            url=url,
            metadatos={**meta, "error_canal": resp["error"]},
        )
        mat["estado"] = "rechazado"
        mat["motivo_aprobacion"] = "fallo de canal: {0}".format(resp["error"])
        return mat

    meta["http_estado"] = resp.get("estado")
    meta["url_final"] = resp.get("url_final")
    return etiquetar(
        dominio=dominio,
        origen=url,
        tipo=tipo,
        cuerpo=resp.get("cuerpo") or b"",
        url=resp.get("url_final") or url,
        metadatos=meta,
    )


def aprobar_por_defecto(
    material: Dict[str, Any],
    resultado_engine: Dict[str, Any],
    *,
    aprobar: Optional[bool] = None,
    motivo: str = "",
) -> Dict[str, Any]:
    if aprobar is None:
        if not isinstance(resultado_engine, dict):
            aprobar = False
            motivo = motivo or "sin resultado_engine usable"
        elif resultado_engine.get("errores"):
            aprobar = False
            motivo = motivo or "resultado_engine con errores"
        else:
            aprobar = True
            motivo = motivo or "estructura de evaluación presente; candidato aprobado por dominio"
    return aplicar_aprobacion(material, resultado_engine, bool(aprobar), motivo)


def filtrar_lote(
    dominio: str,
    materiales: List[Dict[str, Any]],
    resultados_por_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    aprobados: List[Dict[str, Any]] = []
    rechazados: List[Dict[str, Any]] = []
    for mat in materiales:
        mid = mat.get("material_id") or ""
        res = resultados_por_id.get(mid, {})
        out = aprobar_por_defecto(mat, res)
        if out.get("estado") == "aprobado":
            aprobados.append(out)
        else:
            rechazados.append(out)
    return {
        "dominio": dominio,
        "categoria": CATEGORIA,
        "n_entrada": len(materiales),
        "n_aprobados": len(aprobados),
        "n_rechazados": len(rechazados),
        "aprobados": aprobados,
        "rechazados": rechazados,
    }
