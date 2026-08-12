"""Análisis de expresiones regulares y construcción del árbol sintáctico."""

from __future__ import annotations

from dataclasses import dataclass


CONCATENACION = "·"
OPERADORES_BINARIOS = {"|", CONCATENACION}
OPERADORES_POSTFIJOS = {"*", "+", "?"}
PRECEDENCIA = {"|": 1, CONCATENACION: 2}

LITERAL = "literal"
OPERADOR = "operador"
PARENTESIS_IZQUIERDO = "parentesis_izquierdo"
PARENTESIS_DERECHO = "parentesis_derecho"


class ErrorExpresion(ValueError):
    """Indica que una expresión regular no tiene una sintaxis válida."""


@dataclass(frozen=True, slots=True)
class Token:
    valor: str
    tipo: str
    posicion: int


@dataclass(frozen=True, slots=True)
class Nodo:
    """Nodo inmutable del árbol sintáctico."""

    tipo: str
    valor: str | None = None
    izquierdo: Nodo | None = None
    derecho: Nodo | None = None


@dataclass(frozen=True, slots=True)
class ResultadoAnalisis:
    expresion: str
    tokens: tuple[Token, ...]
    postfix: tuple[Token, ...]
    arbol: Nodo


def _tipo_de_caracter(caracter: str) -> str:
    if caracter == "(":
        return PARENTESIS_IZQUIERDO
    if caracter == ")":
        return PARENTESIS_DERECHO
    if caracter in OPERADORES_BINARIOS | OPERADORES_POSTFIJOS:
        return OPERADOR
    return LITERAL


def tokenizar(expresion: str) -> list[Token]:
    """Separa una expresión en operadores, paréntesis y símbolos literales."""

    tokens: list[Token] = []
    indice = 0

    while indice < len(expresion):
        caracter = expresion[indice]

        if caracter.isspace():
            indice += 1
            continue

        if caracter == "\\":
            if indice + 1 >= len(expresion):
                raise ErrorExpresion(
                    f"Escape incompleto en la posición {indice + 1}"
                )
            tokens.append(Token(expresion[indice + 1], LITERAL, indice + 1))
            indice += 2
            continue

        tokens.append(
            Token(caracter, _tipo_de_caracter(caracter), indice + 1)
        )
        indice += 1

    if not tokens:
        raise ErrorExpresion("La expresión regular está vacía")

    return tokens


def _puede_terminar(token: Token) -> bool:
    return (
        token.tipo == LITERAL
        or token.tipo == PARENTESIS_DERECHO
        or token.valor in OPERADORES_POSTFIJOS
    )


def _puede_iniciar(token: Token) -> bool:
    return token.tipo == LITERAL or token.tipo == PARENTESIS_IZQUIERDO


def insertar_concatenaciones(tokens: list[Token]) -> list[Token]:
    """Hace explícitas las concatenaciones escritas de forma implícita."""

    resultado: list[Token] = []

    for token in tokens:
        if (
            resultado
            and _puede_terminar(resultado[-1])
            and _puede_iniciar(token)
        ):
            resultado.append(Token(CONCATENACION, OPERADOR, token.posicion))
        resultado.append(token)

    return resultado


def convertir_a_postfix(tokens: list[Token]) -> list[Token]:
    """Convierte los tokens infix a postfix mediante Shunting Yard."""

    salida: list[Token] = []
    pila: list[Token] = []
    espera_operando = True

    for token in tokens:
        if token.tipo == LITERAL:
            if not espera_operando:
                raise ErrorExpresion(
                    f"Falta un operador antes de la posición {token.posicion}"
                )
            salida.append(token)
            espera_operando = False
            continue

        if token.tipo == PARENTESIS_IZQUIERDO:
            if not espera_operando:
                raise ErrorExpresion(
                    f"Falta un operador antes de la posición {token.posicion}"
                )
            pila.append(token)
            continue

        if token.tipo == PARENTESIS_DERECHO:
            if espera_operando:
                raise ErrorExpresion(
                    f"Cierre de paréntesis inesperado en la posición {token.posicion}"
                )

            while pila and pila[-1].tipo != PARENTESIS_IZQUIERDO:
                salida.append(pila.pop())

            if not pila:
                raise ErrorExpresion(
                    f"Paréntesis sin apertura en la posición {token.posicion}"
                )

            pila.pop()
            espera_operando = False
            continue

        if token.valor in OPERADORES_POSTFIJOS:
            if espera_operando:
                raise ErrorExpresion(
                    f"El operador {token.valor!r} no tiene operando "
                    f"en la posición {token.posicion}"
                )
            salida.append(token)
            continue

        if token.valor in OPERADORES_BINARIOS:
            if espera_operando:
                raise ErrorExpresion(
                    f"El operador {token.valor!r} no tiene operando izquierdo "
                    f"en la posición {token.posicion}"
                )

            while (
                pila
                and pila[-1].valor in OPERADORES_BINARIOS
                and PRECEDENCIA[pila[-1].valor] >= PRECEDENCIA[token.valor]
            ):
                salida.append(pila.pop())

            pila.append(token)
            espera_operando = True
            continue

        raise ErrorExpresion(
            f"Token no reconocido en la posición {token.posicion}"
        )

    if espera_operando:
        raise ErrorExpresion("La expresión termina esperando un operando")

    while pila:
        token = pila.pop()
        if token.tipo == PARENTESIS_IZQUIERDO:
            raise ErrorExpresion(
                f"Paréntesis sin cierre en la posición {token.posicion}"
            )
        salida.append(token)

    return salida


def construir_arbol(postfix: list[Token]) -> Nodo:
    """Construye un árbol sintáctico a partir de una expresión postfix."""

    pila: list[Nodo] = []

    for token in postfix:
        if token.tipo == LITERAL:
            pila.append(Nodo("simbolo", valor=token.valor))
            continue

        if token.valor in OPERADORES_POSTFIJOS:
            if not pila:
                raise ErrorExpresion(
                    f"El operador {token.valor!r} no tiene operando"
                )
            operando = pila.pop()
            tipos = {"*": "estrella", "+": "positiva", "?": "opcional"}
            pila.append(Nodo(tipos[token.valor], izquierdo=operando))
            continue

        if token.valor in OPERADORES_BINARIOS:
            if len(pila) < 2:
                raise ErrorExpresion(
                    f"El operador {token.valor!r} no tiene dos operandos"
                )
            derecho = pila.pop()
            izquierdo = pila.pop()
            tipo = "union" if token.valor == "|" else "concatenacion"
            pila.append(Nodo(tipo, izquierdo=izquierdo, derecho=derecho))
            continue

        raise ErrorExpresion(f"Operador postfix no reconocido: {token.valor!r}")

    if len(pila) != 1:
        raise ErrorExpresion("No se pudo construir un único árbol sintáctico")

    return pila[0]


def analizar(expresion: str) -> ResultadoAnalisis:
    """Ejecuta todas las etapas del análisis de una expresión regular."""

    tokens = tokenizar(expresion)
    tokens_con_concatenacion = insertar_concatenaciones(tokens)
    postfix = convertir_a_postfix(tokens_con_concatenacion)
    arbol = construir_arbol(postfix)

    return ResultadoAnalisis(
        expresion=expresion,
        tokens=tuple(tokens_con_concatenacion),
        postfix=tuple(postfix),
        arbol=arbol,
    )


def formatear_postfix(postfix: tuple[Token, ...]) -> str:
    return " ".join(token.valor for token in postfix)
