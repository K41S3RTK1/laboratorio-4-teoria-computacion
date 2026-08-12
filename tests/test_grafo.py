import tempfile
import unittest
from pathlib import Path

from analizador import analizar
from grafo import generar_svg
from thompson import construir_afn


class PruebasGrafo(unittest.TestCase):
    def test_genera_svg_con_estados_y_transiciones(self) -> None:
        afn = construir_afn(analizar("a|b").arbol)

        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "afn.svg"
            generar_svg(afn, ruta, "AFN de prueba")
            contenido = ruta.read_text(encoding="utf-8")

        self.assertIn("<svg", contenido)
        self.assertIn("AFN de prueba", contenido)
        self.assertIn("inicio", contenido)
        self.assertIn("ε", contenido)
        self.assertIn(f"q{afn.estado_inicial}", contenido)
        self.assertIn(f"q{afn.estado_aceptacion}", contenido)
        self.assertIn("aceptacion", contenido)
        self.assertIn('marker-end="url(#flecha)"', contenido)


if __name__ == "__main__":
    unittest.main(verbosity=2)
