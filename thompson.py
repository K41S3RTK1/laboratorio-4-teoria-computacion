"""Construcción de autómatas finitos no deterministas con Thompson."""

from __future__ import annotations

from dataclasses import dataclass

from analizador import Nodo


@dataclass(frozen=True, slots=True)
class Transicion:
    origen: int
    simbolo: str | None
    destino: int


@dataclass(frozen=True, slots=True)
class AFN:
    estado_inicial: int
    estado_aceptacion: int
    estados: frozenset[int]
    transiciones: tuple[Transicion, ...]


@dataclass(frozen=True, slots=True)
class _Fragmento:
    inicio: int
    fin: int


class _ConstructorThompson:
    def __init__(self) -> None:
        self._siguiente_estado = 0
        self._transiciones: list[Transicion] = []

    def nuevo_estado(self) -> int:
        estado = self._siguiente_estado
        self._siguiente_estado += 1
        return estado

    def conectar(
        self, origen: int, simbolo: str | None, destino: int
    ) -> None:
        self._transiciones.append(Transicion(origen, simbolo, destino))

    def construir_fragmento(self, nodo: Nodo) -> _Fragmento:
        if nodo.tipo == "simbolo":
            inicio = self.nuevo_estado()
            fin = self.nuevo_estado()
            simbolo = None if nodo.valor == "ε" else nodo.valor
            self.conectar(inicio, simbolo, fin)
            return _Fragmento(inicio, fin)

        if nodo.tipo == "concatenacion":
            izquierdo = self.construir_fragmento(_requerir(nodo.izquierdo))
            derecho = self.construir_fragmento(_requerir(nodo.derecho))
            self.conectar(izquierdo.fin, None, derecho.inicio)
            return _Fragmento(izquierdo.inicio, derecho.fin)

        if nodo.tipo == "union":
            inicio = self.nuevo_estado()
            izquierdo = self.construir_fragmento(_requerir(nodo.izquierdo))
            derecho = self.construir_fragmento(_requerir(nodo.derecho))
            fin = self.nuevo_estado()

            self.conectar(inicio, None, izquierdo.inicio)
            self.conectar(inicio, None, derecho.inicio)
            self.conectar(izquierdo.fin, None, fin)
            self.conectar(derecho.fin, None, fin)
            return _Fragmento(inicio, fin)

        if nodo.tipo == "estrella":
            inicio = self.nuevo_estado()
            operando = self.construir_fragmento(_requerir(nodo.izquierdo))
            fin = self.nuevo_estado()

            self.conectar(inicio, None, operando.inicio)
            self.conectar(inicio, None, fin)
            self.conectar(operando.fin, None, operando.inicio)
            self.conectar(operando.fin, None, fin)
            return _Fragmento(inicio, fin)

        if nodo.tipo == "positiva":
            inicio = self.nuevo_estado()
            operando = self.construir_fragmento(_requerir(nodo.izquierdo))
            fin = self.nuevo_estado()

            self.conectar(inicio, None, operando.inicio)
            self.conectar(operando.fin, None, operando.inicio)
            self.conectar(operando.fin, None, fin)
            return _Fragmento(inicio, fin)

        if nodo.tipo == "opcional":
            inicio = self.nuevo_estado()
            operando = self.construir_fragmento(_requerir(nodo.izquierdo))
            fin = self.nuevo_estado()

            self.conectar(inicio, None, operando.inicio)
            self.conectar(inicio, None, fin)
            self.conectar(operando.fin, None, fin)
            return _Fragmento(inicio, fin)

        raise ValueError(f"Tipo de nodo desconocido: {nodo.tipo}")

    def terminar(self, raiz: Nodo) -> AFN:
        fragmento = self.construir_fragmento(raiz)
        return AFN(
            estado_inicial=fragmento.inicio,
            estado_aceptacion=fragmento.fin,
            estados=frozenset(range(self._siguiente_estado)),
            transiciones=tuple(self._transiciones),
        )


def _requerir(nodo: Nodo | None) -> Nodo:
    if nodo is None:
        raise ValueError("El árbol sintáctico está incompleto")
    return nodo


def construir_afn(arbol: Nodo) -> AFN:
    """Aplica el algoritmo de Thompson a un árbol sintáctico."""

    return _ConstructorThompson().terminar(arbol)
