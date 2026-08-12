import unittest

from analizador import analizar
from simulador import simular
from thompson import construir_afn


def acepta(expresion: str, cadena: str) -> bool:
    arbol = analizar(expresion).arbol
    afn = construir_afn(arbol)
    return simular(afn, cadena).aceptada


class PruebasThompsonYSimulacion(unittest.TestCase):
    def test_afn_contiene_estados_principales(self) -> None:
        afn = construir_afn(analizar("a").arbol)
        self.assertIn(afn.estado_inicial, afn.estados)
        self.assertIn(afn.estado_aceptacion, afn.estados)
        self.assertNotEqual(afn.estado_inicial, afn.estado_aceptacion)

    def test_estrella(self) -> None:
        for cadena in ["", "a", "aaaa"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(acepta("a*", cadena))
        self.assertFalse(acepta("a*", "b"))

    def test_cerradura_positiva(self) -> None:
        self.assertFalse(acepta("(ab)+", ""))
        self.assertTrue(acepta("(ab)+", "ab"))
        self.assertTrue(acepta("(ab)+", "abab"))
        self.assertFalse(acepta("(ab)+", "a"))

    def test_operador_opcional(self) -> None:
        self.assertTrue(acepta("a?", ""))
        self.assertTrue(acepta("a?", "a"))
        self.assertFalse(acepta("a?", "aa"))

    def test_epsilon(self) -> None:
        self.assertTrue(acepta("ε", ""))
        self.assertFalse(acepta("ε", "ε"))

    def test_primera_expresion_del_enunciado(self) -> None:
        for cadena in ["", "a", "bbb", "aabbaa", "abab"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(acepta("(a*|b*)+", cadena))
        self.assertFalse(acepta("(a*|b*)+", "abc"))

    def test_segunda_expresion_del_enunciado(self) -> None:
        for cadena in ["", "a", "bbb", "abba"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(acepta("((ε|a)|b*)*", cadena))
        self.assertFalse(acepta("((ε|a)|b*)*", "c"))

    def test_tercera_expresion_del_enunciado(self) -> None:
        for cadena in ["abb", "aabb", "abba", "babbab"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(acepta("(a|b)*abb(a|b)*", cadena))
        for cadena in ["", "ab", "baba", "aaaa"]:
            with self.subTest(cadena=cadena):
                self.assertFalse(acepta("(a|b)*abb(a|b)*", cadena))

    def test_cuarta_expresion_del_enunciado(self) -> None:
        for cadena in ["", "0", "1", "10", "010", "000"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(acepta("0?(1?)?0*", cadena))
        for cadena in ["11", "101", "001", "a"]:
            with self.subTest(cadena=cadena):
                self.assertFalse(acepta("0?(1?)?0*", cadena))

    def test_registra_un_paso_por_simbolo(self) -> None:
        afn = construir_afn(analizar("ab").arbol)
        resultado = simular(afn, "ab")
        self.assertEqual(len(resultado.pasos), 2)
        self.assertTrue(resultado.aceptada)


if __name__ == "__main__":
    unittest.main(verbosity=2)
