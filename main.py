"""Genera y simula los AFN de un archivo de expresiones regulares."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from analizador import ErrorExpresion, analizar, formatear_postfix
from grafo import generar_svg, mostrar_svg
from simulador import ResultadoSimulacion, simular
from thompson import construir_afn


def leer_expresiones(ruta: Path) -> list[str]:
    lineas = ruta.read_text(encoding="utf-8-sig").splitlines()
    return [linea.strip() for linea in lineas if linea.strip()]


def leer_cadenas(ruta: Path) -> list[str]:
    return ruta.read_text(encoding="utf-8-sig").splitlines()


def _formatear_estados(estados: tuple[int, ...]) -> str:
    if not estados:
        return "∅"
    return "{" + ", ".join(f"q{estado}" for estado in estados) + "}"


def imprimir_simulacion(
    cadena: str, resultado: ResultadoSimulacion
) -> None:
    cadena_mostrada = cadena if cadena else "ε"
    print(f"Cadena evaluada: {cadena_mostrada}")
    print(
        "Cerradura epsilon inicial: "
        f"{_formatear_estados(resultado.estados_iniciales)}"
    )

    for numero, paso in enumerate(resultado.pasos, start=1):
        print(
            f"  Paso {numero}: leer {paso.simbolo!r} -> "
            f"{_formatear_estados(paso.estados_despues)}"
        )

    print(f"Estados finales: {_formatear_estados(resultado.estados_finales)}")
    print(f"Resultado: {'sí' if resultado.aceptada else 'no'}")


def _pedir_cadena(numero: int) -> str:
    cadena = input(
        f"Ingrese la cadena w para la expresión {numero} "
        "(Enter representa ε): "
    )
    return "" if cadena == "ε" else cadena


def crear_parser() -> argparse.ArgumentParser:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Construye y simula AFN mediante el algoritmo de Thompson."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        type=Path,
        default=base / "expresiones.txt",
        help="archivo con una expresión regular por línea",
    )
    parser.add_argument(
        "--cadenas",
        type=Path,
        help="archivo opcional con una cadena por cada expresión",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=base / "salida",
        help="directorio donde se guardarán las imágenes SVG",
    )
    parser.add_argument(
        "--no-abrir",
        action="store_true",
        help="genera las imágenes sin abrirlas en pantalla",
    )
    return parser


def main(argumentos: Sequence[str] | None = None) -> int:
    opciones = crear_parser().parse_args(argumentos)

    try:
        expresiones = leer_expresiones(opciones.archivo)
    except FileNotFoundError:
        print(f"ERROR: no se encontró el archivo {opciones.archivo}")
        return 1
    except (OSError, UnicodeError) as error:
        print(f"ERROR: no se pudo leer {opciones.archivo}: {error}")
        return 1

    if not expresiones:
        print("ERROR: el archivo no contiene expresiones regulares")
        return 1

    cadenas: list[str] | None = None
    if opciones.cadenas is not None:
        try:
            cadenas = leer_cadenas(opciones.cadenas)
        except FileNotFoundError:
            print(f"ERROR: no se encontró el archivo {opciones.cadenas}")
            return 1
        except (OSError, UnicodeError) as error:
            print(f"ERROR: no se pudo leer {opciones.cadenas}: {error}")
            return 1

        if len(cadenas) != len(expresiones):
            print(
                "ERROR: el archivo de cadenas debe tener una línea por "
                "cada expresión regular"
            )
            return 1

    print(f"Archivo procesado: {opciones.archivo.resolve()}")
    print(f"Expresiones encontradas: {len(expresiones)}")

    errores = 0
    for numero, expresion in enumerate(expresiones, start=1):
        print("\n" + "=" * 72)
        print(f"EXPRESIÓN {numero}: {expresion}")

        try:
            analisis = analizar(expresion)
            afn = construir_afn(analisis.arbol)
            ruta_svg = generar_svg(
                afn,
                opciones.salida / f"afn_{numero}.svg",
                f"AFN {numero}: {expresion}",
            )
        except (ErrorExpresion, OSError, ValueError) as error:
            print(f"ERROR: {error}")
            errores += 1
            continue

        print(f"Postfix: {formatear_postfix(analisis.postfix)}")
        print(f"Estado inicial: q{afn.estado_inicial}")
        print(f"Estado de aceptación: q{afn.estado_aceptacion}")
        print(f"Cantidad de estados: {len(afn.estados)}")
        print(f"Imagen generada: {ruta_svg}")

        if not opciones.no_abrir and not mostrar_svg(ruta_svg):
            print("Aviso: la imagen no se pudo abrir automáticamente")

        try:
            cadena = cadenas[numero - 1] if cadenas is not None else _pedir_cadena(numero)
        except (EOFError, KeyboardInterrupt):
            print("\nEjecución interrumpida antes de ingresar la cadena")
            return 130

        if cadena == "ε":
            cadena = ""
        imprimir_simulacion(cadena, simular(afn, cadena))

    print("\n" + "=" * 72)
    if errores:
        print(f"Proceso terminado con {errores} expresión(es) inválida(s)")
        return 2

    print("Todas las expresiones fueron procesadas correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
