# Laboratorio 4 - Problema 1

El programa construye un árbol sintáctico para cada expresión regular, aplica
el algoritmo de Thompson, genera la imagen del AFN y simula una cadena ingresada
por el usuario.

## Ejecución

```bash
python3 main.py
```

Las imágenes se guardan en la carpeta `salida` y se abren automáticamente. Para
generarlas sin abrirlas:

```bash
python3 main.py --no-abrir
```

También puede usarse un archivo con una cadena por cada expresión:

```bash
python3 main.py --cadenas cadenas.txt --no-abrir
```

Una línea vacía o el símbolo `ε` representan la cadena vacía.

## Video de ejecución

Enlace de video: [https://youtu.be/xMtrpEK9RGg](https://youtu.be/xMtrpEK9RGg)

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```
