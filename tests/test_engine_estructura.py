# file name: test_engine_estructura.py
import unittest
from pathlib import Path
from fractions import Fraction
from core.engine import Engine, Contenedor, ROLES, OBLIGATORIOS

class ModuloMockValido:
    ALPHA = Fraction(1, 2)
    BETA = Fraction(1, 2)
    CONTENEDOR = {
        "nombre": "mod_ct",
        "rol": "CT",
        "version": "1.0",
        "requiere": [],
        "capacidades": {}
    }

class ModuloMockCapacidadRota:
    CONTENEDOR = {
        "nombre": "mod_roto",
        "rol": "CA",
        "version": "1.0",
        "requiere": [],
        "capacidades": {
            "evaluar": "funcion_absolutamente_inexistente"
        }
    }

class TestEngineEstructura(unittest.TestCase):

    def _imprimir_informe(self, informe: dict, engine_version: str):
        print()
        print("=" * 80)
        print("AUDITORÍA ESTRUCTURAL DEL ENGINE")
        print("=" * 80)
        print(f"Estado general : {informe['estado']}")
        print(f"Engine         : {engine_version}")
        print(f"Aprobados      : {informe['n_aprobados']}")
        print(f"Retenidos      : {informe['n_retenidos']}")
        print()
        for i, item in enumerate(informe["items"], start=1):
            print("-" * 80)
            print(f"Item       : {i}")
            print(f"Tipo       : {item['tipo']}")
            print(f"Estado     : {item['estado']}")
            if "linea" in item:
                print(f"Línea      : {item['linea']}")
            print(f"Evidencia  : {item['evidencia']}")
        print("-" * 80)
        print("FIN DE AUDITORÍA")
        print("=" * 80)

    def test_auditoria_estructura_coherente(self):
        engine = Engine.__new__(Engine)
        engine.VERSION = "12.0"
        engine.estado = "OPERATIVO"
        
        class RegistroMock:
            def __init__(self):
                self.contenedores = {}
                self.por_rol = {r: [] for r in ROLES}
                self.rechazados = []
        
        engine.registro = RegistroMock()
        
        cont_valido = Contenedor(
            nombre="mod_valido",
            rol="CT",
            version="1.0",
            modulo=ModuloMockValido,
            ruta=Path("/tmp/mod_valido/__init__.py"),
            meta=ModuloMockValido.CONTENEDOR
        )
        engine.registro.contenedores["mod_valido"] = cont_valido
        engine.registro.por_rol["CT"].append(cont_valido)

        engine._ce_ids_skills = lambda: {"ids": ["id_1", "id_2"], "skills": [], "disponible": True, "n": 2}

        informe = engine.auditar_estructura()
        self._imprimir_informe(informe, engine.VERSION)

        tipos = {i["tipo"] for i in informe["items"]}
        self.assertIn("AST", tipos)
        self.assertEqual(informe["estado"], "COHERENTE")
        self.assertEqual(informe["n_retenidos"], 0)

    def test_auditoria_estructura_con_contradicciones_reales(self):
        engine = Engine.__new__(Engine)
        engine.VERSION = "12.0"
        engine.estado = "OPERATIVO"

        class RegistroMock:
            def __init__(self):
                self.contenedores = {}
                self.por_rol = {r: [] for r in ROLES}
                self.rechazados = []

        engine.registro = RegistroMock()

        # Caso real permitido por el cargador pero con contrato roto (capacidad sin función real)
        cont_roto = Contenedor(
            nombre="mod_roto",
            rol="CA",
            version="1.0",
            modulo=ModuloMockCapacidadRota,
            ruta=Path("/tmp/mod_roto/__init__.py"),
            meta=ModuloMockCapacidadRota.CONTENEDOR
        )
        engine.registro.contenedores["mod_roto"] = cont_roto
        engine.registro.por_rol["CA"].append(cont_roto)

        # IDs repetidos reales en CE
        engine._ce_ids_skills = lambda: {"ids": ["ce_mandato_sujetos", "ce_mandato_sujetos"], "skills": [], "disponible": True, "n": 2}

        informe = engine.auditar_estructura()
        self._imprimir_informe(informe, engine.VERSION)

        errores = [
            i["tipo"]
            for i in informe["items"]
            if i["estado"] == "RETENIDO"
        ]

        self.assertIn("IDS", errores)
        self.assertIn("CAPACIDAD", errores)
        self.assertEqual(informe["estado"], "CONTRADICCION")
        self.assertGreater(informe["n_retenidos"], 0)

if __name__ == "__main__":
    unittest.main()
