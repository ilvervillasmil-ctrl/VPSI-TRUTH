# ===============================================================
# BARRIDO AXIOMÁTICO (Actualizado para reportar detalles)
# ===============================================================

def barrer(self, declaraciones_externas: Dict[str, List[Dict]] = None) -> Dict:
    """
    Entrada del Engine:
        {nombre_de_modulo: [declaraciones]}

    Salida:
        coherente    False detiene el arranque
        choques      lista de contradicciones DETALLADAS
        errores      declaraciones mal formadas
        declaraciones   total de declaraciones cargadas
    """
    decls, errores = self._cargar_todos_los_archivos()

    # Añadir declaraciones externas (si las hay)
    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            if not isinstance(lista, list):
                errores.append({
                    "modulo": nombre,
                    "error": "declaraciones externas no es lista",
                })
                continue
            for d in lista:
                try:
                    decls.append(self.normalizar(d, nombre))
                except ValueError as e:
                    errores.append({
                        "modulo": nombre,
                        "error": str(e),
                    })

    # Detectar contradicciones
    choques = self._detectar_contradicciones_detalladas(decls)

    return {
        "coherente": not (choques or errores),
        "choques": choques,  # Ahora incluye detalles
        "errores": errores,
        "declaraciones": len(decls),
    }

def _detectar_contradicciones_detalladas(self, decls: List[Dict]) -> List[Dict]:
    """
    Detecta contradicciones y devuelve una lista con detalles específicos:
    - Tipo de contradicción.
    - Declaraciones involucradas.
    - Ubicación (archivo y línea si está disponible).
    """
    choques = []

    # Agrupar declaraciones por tripleta (sujeto, relación, objeto)
    grupos_por_tripleta = {}
    for d in decls:
        clave = self.clave(d)
        if clave not in grupos_por_tripleta:
            grupos_por_tripleta[clave] = []
        grupos_por_tripleta[clave].append(d)

    # Buscar contradicciones directas (misma tripleta, polaridad opuesta)
    for tripleta, grupo in grupos_por_tripleta.items():
        afirman = [d for d in grupo if d["polaridad"]]
        niegan = [d for d in grupo if not d["polaridad"]]
        for a in afirman:
            for n in niegan:
                choques.append({
                    "tipo": "contradiccion_directa",
                    "tripleta": " - ".join(tripleta),
                    "declaracion_1": {
                        "id": a["id"],
                        "sujeto": a["sujeto"],
                        "relacion": a["relacion"],
                        "objeto": a["objeto"],
                        "polaridad": a["polaridad"],
                        "ubicacion": f"{a['cuerpo']} (ID: {a['id']})",
                        "enunciado": a.get("enunciado", "Sin enunciado"),
                    },
                    "declaracion_2": {
                        "id": n["id"],
                        "sujeto": n["sujeto"],
                        "relacion": n["relacion"],
                        "objeto": n["objeto"],
                        "polaridad": n["polaridad"],
                        "ubicacion": f"{n['cuerpo']} (ID: {n['id']})",
                        "enunciado": n.get("enunciado", "Sin enunciado"),
                    },
                    "mensaje": (
                        f"Contradicción directa en la tripleta '{' - '.join(tripleta)}':\n"
                        f"  - {a['cuerpo']}:{a['id']} AFIRMA que {a['sujeto']} {a['relacion']} {a['objeto']}.\n"
                        f"  - {n['cuerpo']}:{n['id']} NIEGA que {n['sujeto']} {n['relacion']} {n['objeto']}."
                    )
                })

    # Buscar contradicciones de cota (mismo sujeto y relación, cotas distintas)
    grupos_por_sujeto_relacion = {}
    for d in decls:
        if d.get("cota") is None:
            continue
        clave = (d["sujeto"].lower().strip(), d["relacion"].lower().strip())
        if clave not in grupos_por_sujeto_relacion:
            grupos_por_sujeto_relacion[clave] = []
        grupos_por_sujeto_relacion[clave].append(d)

    for (suj, rel), grupo in grupos_por_sujeto_relacion.items():
        cotas = {}
        for d in grupo:
            cota = d["cota"]
            if cota not in cotas:
                cotas[cota] = []
            cotas[cota].append(d)

        if len(cotas) > 1:
            for cota1, decls_cota1 in cotas.items():
                for cota2, decls_cota2 in cotas.items():
                    if cota1 != cota2:
                        for d1 in decls_cota1:
                            for d2 in decls_cota2:
                                choques.append({
                                    "tipo": "contradiccion_de_cota",
                                    "sujeto": suj,
                                    "relacion": rel,
                                    "cota_1": cota1,
                                    "cota_2": cota2,
                                    "declaracion_1": {
                                        "id": d1["id"],
                                        "sujeto": d1["sujeto"],
                                        "relacion": d1["relacion"],
                                        "objeto": d1["objeto"],
                                        "cota": d1["cota"],
                                        "ubicacion": f"{d1['cuerpo']} (ID: {d1['id']})",
                                        "enunciado": d1.get("enunciado", "Sin enunciado"),
                                    },
                                    "declaracion_2": {
                                        "id": d2["id"],
                                        "sujeto": d2["sujeto"],
                                        "relacion": d2["relacion"],
                                        "objeto": d2["objeto"],
                                        "cota": d2["cota"],
                                        "ubicacion": f"{d2['cuerpo']} (ID: {d2['id']})",
                                        "enunciado": d2.get("enunciado", "Sin enunciado"),
                                    },
                                    "mensaje": (
                                        f"Contradicción de cota en '{suj} {rel}':\n"
                                        f"  - {d1['cuerpo']}:{d1['id']} define cota = {cota1}.\n"
                                        f"  - {d2['cuerpo']}:{d2['id']} define cota = {cota2}."
                                    )
                                })

    return choques
