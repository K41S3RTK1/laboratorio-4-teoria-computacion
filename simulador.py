"""Simulación de un AFN mediante cerraduras epsilon."""

from __future__ import annotations

from dataclasses import dataclass

from thompson import AFN


@dataclass(frozen=True, slots=True)
class PasoSimulacion:
    simbolo: str
    estados_antes: tuple[int, ...]
    estados_despues: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ResultadoSimulacion:
    aceptada: bool
    estados_iniciales: tuple[int, ...]
    pasos: tuple[PasoSimulacion, ...]
    estados_finales: tuple[int, ...]


def cerradura_epsilon(afn: AFN, estados: set[int]) -> set[int]:
    """Obtiene los estados alcanzables usando solamente transiciones epsilon."""

    cierre = set(estados)
    pendientes = list(estados)

    while pendientes:
        actual = pendientes.pop()
        for transicion in afn.transiciones:
            if (
                transicion.origen == actual
                and transicion.simbolo is None
                and transicion.destino not in cierre
            ):
                cierre.add(transicion.destino)
                pendientes.append(transicion.destino)

    return cierre


def mover(afn: AFN, estados: set[int], simbolo: str) -> set[int]:
    destinos: set[int] = set()

    for transicion in afn.transiciones:
        if (
            transicion.origen in estados
            and transicion.simbolo == simbolo
        ):
            destinos.add(transicion.destino)

    return destinos


def simular(afn: AFN, cadena: str) -> ResultadoSimulacion:
    """Procesa una cadena y determina si el AFN la acepta."""

    actuales = cerradura_epsilon(afn, {afn.estado_inicial})
    iniciales = tuple(sorted(actuales))
    pasos: list[PasoSimulacion] = []

    for simbolo in cadena:
        anteriores = tuple(sorted(actuales))
        alcanzados = mover(afn, actuales, simbolo)
        actuales = cerradura_epsilon(afn, alcanzados)
        pasos.append(
            PasoSimulacion(
                simbolo=simbolo,
                estados_antes=anteriores,
                estados_despues=tuple(sorted(actuales)),
            )
        )

    finales = tuple(sorted(actuales))
    return ResultadoSimulacion(
        aceptada=afn.estado_aceptacion in actuales,
        estados_iniciales=iniciales,
        pasos=tuple(pasos),
        estados_finales=finales,
    )
