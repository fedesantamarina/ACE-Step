#!/usr/bin/env python3
"""
Demo de ACE-Step en Español
===========================

Script de demostración para generar música con letras en español.

Uso:
    python demo.py                    # Genera con configuración por defecto
    python demo.py --genero reggaeton # Especifica un género
    python demo.py --duracion 30      # Especifica duración en segundos
    python demo.py --listar-generos   # Lista géneros disponibles
"""

import argparse
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc_espanol.generador_musica import (
    GeneradorMusicaEspanol,
    ConfiguracionGeneracion,
    GENEROS_ESPANOL,
    PLANTILLAS_LETRAS,
)


def listar_generos():
    """Lista todos los géneros disponibles."""
    print("\n" + "=" * 60)
    print("GÉNEROS MUSICALES DISPONIBLES")
    print("=" * 60 + "\n")

    for genero, descripcion in GENEROS_ESPANOL.items():
        print(f"  {genero:20} → {descripcion}")

    print("\n" + "=" * 60 + "\n")


def listar_plantillas():
    """Lista todas las plantillas de letras disponibles."""
    print("\n" + "=" * 60)
    print("PLANTILLAS DE LETRAS DISPONIBLES")
    print("=" * 60 + "\n")

    for nombre, letra in PLANTILLAS_LETRAS.items():
        # Mostrar solo las primeras líneas
        lineas = letra.split("\n")[:5]
        preview = "\n    ".join(lineas)
        print(f"  {nombre}:")
        print(f"    {preview}")
        print("    ...")
        print()

    print("=" * 60 + "\n")


def generar_musica(args):
    """Genera música con los parámetros especificados."""
    print("\n" + "=" * 60)
    print("GENERADOR DE MÚSICA ACE-STEP EN ESPAÑOL")
    print("=" * 60 + "\n")

    # Configuración
    config = ConfiguracionGeneracion(
        duracion_segundos=args.duracion,
        pasos_inferencia=args.pasos,
        directorio_salida=args.salida,
        usar_cpu_offload=args.cpu_offload,
    )

    print(f"Configuración:")
    print(f"  - Género: {args.genero}")
    print(f"  - Duración: {args.duracion} segundos")
    print(f"  - Pasos de inferencia: {args.pasos}")
    print(f"  - Directorio de salida: {args.salida}")
    print(f"  - CPU Offload: {'Sí' if args.cpu_offload else 'No'}")

    if args.semilla:
        print(f"  - Semilla: {args.semilla}")

    print("\nIniciando generación...\n")

    # Crear generador
    generador = GeneradorMusicaEspanol(config)

    # Obtener letra
    if args.plantilla and args.plantilla in PLANTILLAS_LETRAS:
        letra = PLANTILLAS_LETRAS[args.plantilla]
        print(f"Usando plantilla: {args.plantilla}")
    else:
        letra = PLANTILLAS_LETRAS["amor"]
        print("Usando plantilla por defecto: amor")

    # Generar
    resultado = generador.generar_cancion(
        genero=args.genero,
        letra=letra,
        duracion=args.duracion,
        semilla=args.semilla,
        nombre_archivo=args.nombre_archivo
    )

    # Mostrar resultado
    print("\n" + "-" * 60)

    if resultado.exitoso:
        print("¡GENERACIÓN EXITOSA!")
        print(f"\nArchivo generado: {resultado.ruta_audio}")

        if resultado.tiempos:
            print("\nTiempos de ejecución:")
            for etapa, tiempo in resultado.tiempos.items():
                print(f"  - {etapa}: {tiempo:.2f}s")

        if resultado.semillas_usadas:
            print(f"\nSemillas usadas: {resultado.semillas_usadas}")

    else:
        print("ERROR EN LA GENERACIÓN")
        print(f"\nMensaje: {resultado.mensaje}")

    print("\n" + "=" * 60 + "\n")

    return 0 if resultado.exitoso else 1


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Generador de música ACE-Step en español",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python demo.py --genero reggaeton --duracion 60
  python demo.py --genero balada --plantilla reflexion
  python demo.py --listar-generos
  python demo.py --listar-plantillas
        """
    )

    # Argumentos para listar opciones
    parser.add_argument(
        "--listar-generos",
        action="store_true",
        help="Lista los géneros musicales disponibles"
    )
    parser.add_argument(
        "--listar-plantillas",
        action="store_true",
        help="Lista las plantillas de letras disponibles"
    )

    # Argumentos de generación
    parser.add_argument(
        "--genero",
        type=str,
        default="pop_latino",
        choices=list(GENEROS_ESPANOL.keys()),
        help="Género musical (default: pop_latino)"
    )
    parser.add_argument(
        "--plantilla",
        type=str,
        choices=list(PLANTILLAS_LETRAS.keys()),
        help="Plantilla de letra a usar"
    )
    parser.add_argument(
        "--duracion",
        type=float,
        default=60.0,
        help="Duración en segundos (10-240, default: 60)"
    )
    parser.add_argument(
        "--pasos",
        type=int,
        default=60,
        help="Pasos de inferencia (default: 60)"
    )
    parser.add_argument(
        "--semilla",
        type=int,
        help="Semilla para reproducibilidad"
    )
    parser.add_argument(
        "--salida",
        type=str,
        default="./salidas_espanol",
        help="Directorio de salida (default: ./salidas_espanol)"
    )
    parser.add_argument(
        "--nombre-archivo",
        type=str,
        help="Nombre del archivo de salida (sin extensión)"
    )
    parser.add_argument(
        "--cpu-offload",
        action="store_true",
        help="Activar CPU offload para reducir uso de VRAM"
    )

    args = parser.parse_args()

    # Manejar opciones de listado
    if args.listar_generos:
        listar_generos()
        return 0

    if args.listar_plantillas:
        listar_plantillas()
        return 0

    # Generar música
    return generar_musica(args)


if __name__ == "__main__":
    sys.exit(main())
