"""Generación de una representación SVG para un AFN."""

from __future__ import annotations

import html
import math
import webbrowser
from collections import defaultdict
from pathlib import Path

from thompson import AFN


RADIO = 27
SEPARACION_X = 125
SEPARACION_Y = 105
MARGEN_X = 85
MARGEN_SUPERIOR = 120
MARGEN_INFERIOR = 100


def _escapar(texto: str) -> str:
    return html.escape(texto, quote=True)


def _agrupar_transiciones(afn: AFN) -> dict[tuple[int, int], list[str]]:
    agrupadas: dict[tuple[int, int], list[str]] = defaultdict(list)

    for transicion in afn.transiciones:
        simbolo = "ε" if transicion.simbolo is None else transicion.simbolo
        clave = (transicion.origen, transicion.destino)
        if simbolo not in agrupadas[clave]:
            agrupadas[clave].append(simbolo)

    return dict(agrupadas)


def _calcular_posiciones(
    afn: AFN,
) -> tuple[dict[int, tuple[float, float]], int, int]:
    niveles = {estado: 0 for estado in afn.estados}

    for estado in sorted(afn.estados):
        for transicion in afn.transiciones:
            if transicion.origen == estado and transicion.destino > estado:
                niveles[transicion.destino] = max(
                    niveles[transicion.destino], niveles[estado] + 1
                )

    por_nivel: dict[int, list[int]] = defaultdict(list)
    for estado in sorted(afn.estados):
        por_nivel[niveles[estado]].append(estado)

    nivel_maximo = max(por_nivel)
    cantidad_vertical = max(len(estados) for estados in por_nivel.values())
    alto = max(
        470,
        MARGEN_SUPERIOR
        + MARGEN_INFERIOR
        + max(0, cantidad_vertical - 1) * SEPARACION_Y,
    )
    centro_y = (MARGEN_SUPERIOR + alto - MARGEN_INFERIOR) / 2
    ancho = max(850, 2 * MARGEN_X + nivel_maximo * SEPARACION_X)

    posiciones: dict[int, tuple[float, float]] = {}
    for nivel, estados in por_nivel.items():
        desplazamiento = (len(estados) - 1) * SEPARACION_Y / 2
        for indice, estado in enumerate(estados):
            posiciones[estado] = (
                MARGEN_X + nivel * SEPARACION_X,
                centro_y - desplazamiento + indice * SEPARACION_Y,
            )

    return posiciones, ancho, alto


def _extremos_de_linea(
    origen: tuple[float, float], destino: tuple[float, float]
) -> tuple[float, float, float, float]:
    x1, y1 = origen
    x2, y2 = destino
    distancia = math.hypot(x2 - x1, y2 - y1)
    if distancia == 0:
        return x1, y1, x2, y2

    unidad_x = (x2 - x1) / distancia
    unidad_y = (y2 - y1) / distancia
    return (
        x1 + unidad_x * RADIO,
        y1 + unidad_y * RADIO,
        x2 - unidad_x * RADIO,
        y2 - unidad_y * RADIO,
    )


def _dibujar_transicion(
    origen: int,
    destino: int,
    simbolos: list[str],
    posiciones: dict[int, tuple[float, float]],
    alto: int,
) -> str:
    x_origen, y_origen = posiciones[origen]
    x_destino, y_destino = posiciones[destino]
    etiqueta = _escapar(", ".join(simbolos))

    if origen == destino:
        camino = (
            f"M {x_origen - 14} {y_origen - 23} "
            f"C {x_origen - 45} {y_origen - 88}, "
            f"{x_origen + 45} {y_origen - 88}, "
            f"{x_origen + 14} {y_origen - 23}"
        )
        etiqueta_x = x_origen
        etiqueta_y = y_origen - 78
    elif destino > origen:
        inicio_x, inicio_y, fin_x, fin_y = _extremos_de_linea(
            (x_origen, y_origen), (x_destino, y_destino)
        )
        obstaculos = [
            (x, y)
            for estado, (x, y) in posiciones.items()
            if (
                estado not in {origen, destino}
                and inicio_x < x < fin_x
                and abs(y - (inicio_y + fin_y) / 2) < RADIO * 1.7
            )
        ]

        if obstaculos:
            medio_x = (inicio_x + fin_x) / 2
            control_y = min(
                inicio_y,
                fin_y,
                *(y for _, y in obstaculos),
            ) - 130 - len(obstaculos) * 12
            camino = (
                f"M {inicio_x} {inicio_y} "
                f"Q {medio_x} {control_y} {fin_x} {fin_y}"
            )
            etiqueta_x = medio_x
            etiqueta_y = (
                inicio_y + 2 * control_y + fin_y
            ) / 4 - 9
        else:
            camino = f"M {inicio_x} {inicio_y} L {fin_x} {fin_y}"
            etiqueta_x = (inicio_x + fin_x) / 2
            etiqueta_y = (inicio_y + fin_y) / 2 - 9
    else:
        base_y = min(
            alto - 35,
            max(y_origen, y_destino)
            + 65
            + min(150, (origen - destino) * 9),
        )
        camino = (
            f"M {x_origen} {y_origen + RADIO} "
            f"C {x_origen} {base_y}, {x_destino} {base_y}, "
            f"{x_destino} {y_destino + RADIO}"
        )
        etiqueta_x = (x_origen + x_destino) / 2
        etiqueta_y = base_y - 8

    return (
        f'<path d="{camino}" class="transicion" marker-end="url(#flecha)"/>'
        f'<text x="{etiqueta_x}" y="{etiqueta_y}" '
        f'class="etiqueta">{etiqueta}</text>'
    )


def generar_svg(afn: AFN, ruta: Path, titulo: str) -> Path:
    """Guarda el grafo del AFN como una imagen SVG."""

    posiciones, ancho, alto = _calcular_posiciones(afn)
    estados = sorted(afn.estados)

    elementos: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" '
            f'height="{alto}" viewBox="0 0 {ancho} {alto}">'
        ),
        "<defs>",
        (
            '<marker id="flecha" markerWidth="9" markerHeight="7" '
            'refX="8" refY="3.5" orient="auto">'
            '<polygon points="0 0, 9 3.5, 0 7" fill="#334155"/>'
            "</marker>"
        ),
        "</defs>",
        "<style>",
        ".fondo { fill: #f8fafc; }",
        ".transicion { fill: none; stroke: #334155; stroke-width: 1.8; }",
        (
            ".etiqueta { font: 16px sans-serif; text-anchor: middle; "
            "fill: #0f172a; stroke: #f8fafc; stroke-width: 5px; "
            "paint-order: stroke; }"
        ),
        ".estado { fill: white; stroke: #0f172a; stroke-width: 2.2; }",
        ".inicial { fill: #dbeafe; }",
        ".aceptacion { fill: #dcfce7; }",
        ".nombre { font: 15px sans-serif; text-anchor: middle; fill: #0f172a; }",
        ".titulo { font: bold 22px sans-serif; fill: #0f172a; }",
        ".detalle { font: 15px sans-serif; fill: #475569; }",
        "</style>",
        f'<rect class="fondo" width="{ancho}" height="{alto}"/>',
        f'<text x="30" y="38" class="titulo">{_escapar(titulo)}</text>',
        (
            f'<text x="30" y="64" class="detalle">'
            f'{len(estados)} estados · {len(afn.transiciones)} transiciones'
            "</text>"
        ),
    ]

    for (origen, destino), simbolos in sorted(
        _agrupar_transiciones(afn).items()
    ):
        elementos.append(
            _dibujar_transicion(
                origen, destino, simbolos, posiciones, alto
            )
        )

    x_inicial, y_inicial = posiciones[afn.estado_inicial]
    elementos.append(
        f'<path d="M 18 {y_inicial} L {x_inicial - RADIO} {y_inicial}" '
        'class="transicion" marker-end="url(#flecha)"/>'
    )
    elementos.append(
        f'<text x="18" y="{y_inicial - 13}" class="detalle">inicio</text>'
    )

    for estado in estados:
        clases = ["estado"]
        if estado == afn.estado_inicial:
            clases.append("inicial")
        if estado == afn.estado_aceptacion:
            clases.append("aceptacion")

        x, y = posiciones[estado]
        elementos.append(
            f'<circle cx="{x}" cy="{y}" r="{RADIO}" '
            f'class="{" ".join(clases)}"/>'
        )
        if estado == afn.estado_aceptacion:
            elementos.append(
                f'<circle cx="{x}" cy="{y}" r="{RADIO - 5}" '
                'fill="none" stroke="#0f172a" stroke-width="2"/>'
            )
        elementos.append(
            f'<text x="{x}" y="{y + 5}" class="nombre">q{estado}</text>'
        )

    elementos.append("</svg>")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(elementos), encoding="utf-8")
    return ruta.resolve()


def mostrar_svg(ruta: Path) -> bool:
    """Abre una imagen SVG con la aplicación predeterminada."""

    return webbrowser.open(ruta.resolve().as_uri())
