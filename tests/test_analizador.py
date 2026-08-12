import unittest

from analizador import ErrorExpresion, analizar, formatear_postfix


class PruebasAnalizador(unittest.TestCase):
    def test_expresiones_del_enunciado(self) -> None:
        casos = {
            "(a*|b*)+": "a * b * | +",
            "((ε|a)|b*)*": "ε a | b * | *",
            "(a|b)*abb(a|b)*": "a b | * a · b · b · a b | * ·",
            "0?(1?)?0*": "0 ? 1 ? ? · 0 * ·",
        }

        for expresion, esperado in casos.items():
            with self.subTest(expresion=expresion):
                resultado = analizar(expresion)
                self.assertEqual(formatear_postfix(resultado.postfix), esperado)

    def test_construye_la_raiz_del_arbol(self) -> None:
        self.assertEqual(analizar("(a|b)*").arbol.tipo, "estrella")
        self.assertEqual(analizar("ab").arbol.tipo, "concatenacion")
        self.assertEqual(analizar("a|b").arbol.tipo, "union")

    def test_operador_escapado_es_literal(self) -> None:
        arbol = analizar(r"\*").arbol
        self.assertEqual(arbol.tipo, "simbolo")
        self.assertEqual(arbol.valor, "*")

    def test_rechaza_expresiones_invalidas(self) -> None:
        expresiones = ["", "|a", "a|", "(a", "a)", "()", "*a", "a\\"]

        for expresion in expresiones:
            with self.subTest(expresion=expresion):
                with self.assertRaises(ErrorExpresion):
                    analizar(expresion)


if __name__ == "__main__":
    unittest.main(verbosity=2)
