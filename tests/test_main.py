import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from main import main


class PruebasIntegracion(unittest.TestCase):
    def test_procesa_archivos_sin_interaccion(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            base = Path(temporal)
            expresiones = base / "expresiones.txt"
            cadenas = base / "cadenas.txt"
            salida = base / "salida"
            expresiones.write_text("a*\n(a|b)*abb(a|b)*\n", encoding="utf-8")
            cadenas.write_text("aaa\naabb\n", encoding="utf-8")

            consola = io.StringIO()
            with contextlib.redirect_stdout(consola):
                codigo = main(
                    [
                        str(expresiones),
                        "--cadenas",
                        str(cadenas),
                        "--salida",
                        str(salida),
                        "--no-abrir",
                    ]
                )

            self.assertEqual(codigo, 0)
            self.assertTrue((salida / "afn_1.svg").is_file())
            self.assertTrue((salida / "afn_2.svg").is_file())
            self.assertEqual(consola.getvalue().count("Resultado: sí"), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
