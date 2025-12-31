"""
Generador de Música en Español usando ACE-Step
===============================================

Este módulo proporciona una interfaz en español para el modelo ACE-Step,
facilitando la generación de música con letras en español.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ConfiguracionGeneracion:
    """Configuración para la generación de música en español."""

    # Configuración de audio
    duracion_segundos: float = 60.0
    formato_salida: str = "wav"

    # Configuración del modelo
    pasos_inferencia: int = 60
    escala_guia: float = 15.0
    tipo_scheduler: str = "euler"
    tipo_cfg: str = "apg"
    escala_omega: float = 10.0

    # Configuración avanzada
    intervalo_guia: float = 0.5
    decaimiento_guia: float = 0.0
    escala_guia_minima: float = 3.0
    usar_erg_tag: bool = True
    usar_erg_letra: bool = True
    usar_erg_difusion: bool = True

    # Semillas para reproducibilidad
    semillas: Optional[List[int]] = None

    # Rutas
    directorio_salida: str = "./salidas_espanol"
    ruta_checkpoint: Optional[str] = None

    # Configuración de hardware
    id_dispositivo: int = 0
    usar_bf16: bool = True
    usar_cpu_offload: bool = False
    usar_torch_compile: bool = False


@dataclass
class ResultadoGeneracion:
    """Resultado de una generación de música."""

    exitoso: bool
    ruta_audio: Optional[str] = None
    mensaje: str = ""
    parametros: Dict[str, Any] = field(default_factory=dict)
    tiempos: Dict[str, float] = field(default_factory=dict)
    semillas_usadas: List[int] = field(default_factory=list)


# Géneros musicales con descripciones en español
GENEROS_ESPANOL = {
    "pop_latino": "pop, latin pop, tropical, catchy, upbeat, spanish",
    "reggaeton": "reggaeton, urban latin, dembow, perreo, trap latino",
    "balada": "ballad, romantic, slow, emotional, acoustic guitar, piano",
    "rock_espanol": "rock en español, rock latino, guitar, drums, energetic",
    "cumbia": "cumbia, tropical, accordion, dance, festive, colombian",
    "salsa": "salsa, tropical, brass, piano, percussion, dance",
    "bachata": "bachata, romantic, guitar, dominican, sensual",
    "flamenco": "flamenco, spanish guitar, passionate, rhythmic, andalusian",
    "mariachi": "mariachi, mexican, trumpet, violin, traditional",
    "tango": "tango, argentine, bandoneon, dramatic, passionate",
    "urbano": "urban, trap, hip hop latino, 808, autotune",
    "folclore": "folk, acoustic, traditional, spanish, guitar"
}

# Plantillas de letras en español
PLANTILLAS_LETRAS = {
    "amor": """[verse]
Cada vez que te veo pasar
Mi corazón empieza a latir
No puedo dejar de pensar
En todo lo que quiero decir

[chorus]
Porque tú eres mi luz
Mi camino y mi razón
Contigo todo es mejor
Eres dueña de mi corazón

[verse]
Las noches son más largas sin ti
Los días pierden su color
Pero cuando estás aquí
Todo brilla con tu amor

[chorus]
Porque tú eres mi luz
Mi camino y mi razón
Contigo todo es mejor
Eres dueña de mi corazón""",

    "fiesta": """[verse]
La noche está encendida
La música suena sin parar
Todos juntos en la pista
Es hora de bailar

[chorus]
Mueve el cuerpo al ritmo
Siente la vibración
Esta noche es nuestra
Vive la emoción

[verse]
Las luces parpadean
El DJ sube el volumen
Los problemas se alejan
Que la fiesta no se detenga

[chorus]
Mueve el cuerpo al ritmo
Siente la vibración
Esta noche es nuestra
Vive la emoción""",

    "reflexion": """[verse]
Caminando por las calles vacías
Pensando en lo que pudo ser
Recuerdos de mejores días
Que no van a volver

[bridge]
Pero aprendí a levantarme
Cada vez que caí
A no rendirme nunca
A creer en mí

[chorus]
Porque la vida sigue adelante
Con sus altos y sus bajos
Lo importante es ser constante
Y dar siempre lo máximo

[verse]
El tiempo cura las heridas
Las tormentas siempre pasan
Nuevas puertas se abren
Cuando otras se cierran"""
}


class GeneradorMusicaEspanol:
    """
    Generador de música con letras en español usando ACE-Step.

    Esta clase proporciona una interfaz simplificada en español
    para generar música usando el modelo ACE-Step.

    Ejemplo de uso:
        >>> generador = GeneradorMusicaEspanol()
        >>> resultado = generador.generar_cancion(
        ...     genero="pop_latino",
        ...     letra=PLANTILLAS_LETRAS["amor"],
        ...     duracion=60
        ... )
        >>> print(resultado.ruta_audio)
    """

    def __init__(self, config: Optional[ConfiguracionGeneracion] = None):
        """
        Inicializa el generador de música.

        Args:
            config: Configuración opcional para la generación.
                   Si no se proporciona, se usan valores por defecto.
        """
        self.config = config or ConfiguracionGeneracion()
        self._pipeline = None
        self._inicializado = False

    def _inicializar_pipeline(self) -> bool:
        """
        Inicializa el pipeline de ACE-Step.

        Returns:
            True si la inicialización fue exitosa, False en caso contrario.
        """
        if self._inicializado:
            return True

        try:
            from acestep.pipeline_ace_step import ACEStepPipeline

            self._pipeline = ACEStepPipeline(
                checkpoint_dir=self.config.ruta_checkpoint,
                device_id=self.config.id_dispositivo,
                dtype="bfloat16" if self.config.usar_bf16 else "float32",
                torch_compile=self.config.usar_torch_compile,
                cpu_offload=self.config.usar_cpu_offload,
            )

            self._inicializado = True
            return True

        except Exception as e:
            print(f"Error al inicializar el pipeline: {e}")
            return False

    def obtener_generos_disponibles(self) -> Dict[str, str]:
        """
        Obtiene los géneros musicales disponibles.

        Returns:
            Diccionario con los géneros y sus descripciones.
        """
        return GENEROS_ESPANOL.copy()

    def obtener_plantillas_letras(self) -> Dict[str, str]:
        """
        Obtiene las plantillas de letras disponibles.

        Returns:
            Diccionario con las plantillas de letras.
        """
        return PLANTILLAS_LETRAS.copy()

    def validar_letra(self, letra: str) -> tuple[bool, str]:
        """
        Valida el formato de la letra.

        Args:
            letra: Letra a validar.

        Returns:
            Tupla (es_valida, mensaje_error)
        """
        if not letra or not letra.strip():
            return False, "La letra no puede estar vacía"

        # Verificar que tenga al menos una sección
        secciones_validas = ["[verse]", "[chorus]", "[bridge]", "[intro]", "[outro]"]
        tiene_seccion = any(seccion in letra.lower() for seccion in secciones_validas)

        if not tiene_seccion:
            return False, "La letra debe contener al menos una sección ([verse], [chorus], etc.)"

        # Verificar longitud mínima
        lineas = [l.strip() for l in letra.split("\n") if l.strip() and not l.strip().startswith("[")]
        if len(lineas) < 4:
            return False, "La letra debe contener al menos 4 líneas de texto"

        return True, ""

    def generar_cancion(
        self,
        genero: str = "pop_latino",
        letra: Optional[str] = None,
        duracion: float = 60.0,
        semilla: Optional[int] = None,
        nombre_archivo: Optional[str] = None
    ) -> ResultadoGeneracion:
        """
        Genera una canción con el género y letra especificados.

        Args:
            genero: Género musical (ver obtener_generos_disponibles())
            letra: Letra de la canción. Si no se proporciona, se usa una plantilla.
            duracion: Duración en segundos (10-240)
            semilla: Semilla para reproducibilidad
            nombre_archivo: Nombre del archivo de salida (sin extensión)

        Returns:
            ResultadoGeneracion con la información del resultado.
        """
        # Validar género
        if genero not in GENEROS_ESPANOL:
            generos_validos = ", ".join(GENEROS_ESPANOL.keys())
            return ResultadoGeneracion(
                exitoso=False,
                mensaje=f"Género '{genero}' no válido. Géneros disponibles: {generos_validos}"
            )

        # Usar plantilla si no se proporciona letra
        if letra is None:
            letra = PLANTILLAS_LETRAS["amor"]

        # Validar letra
        es_valida, error = self.validar_letra(letra)
        if not es_valida:
            return ResultadoGeneracion(
                exitoso=False,
                mensaje=f"Error en la letra: {error}"
            )

        # Validar duración
        if duracion < 10 or duracion > 240:
            return ResultadoGeneracion(
                exitoso=False,
                mensaje="La duración debe estar entre 10 y 240 segundos"
            )

        # Inicializar pipeline
        if not self._inicializar_pipeline():
            return ResultadoGeneracion(
                exitoso=False,
                mensaje="No se pudo inicializar el modelo. Verifica que tienes suficiente memoria GPU."
            )

        # Preparar directorio de salida
        os.makedirs(self.config.directorio_salida, exist_ok=True)

        # Preparar nombre de archivo
        if nombre_archivo:
            ruta_salida = os.path.join(
                self.config.directorio_salida,
                f"{nombre_archivo}.{self.config.formato_salida}"
            )
        else:
            ruta_salida = self.config.directorio_salida

        try:
            # Obtener prompt del género
            prompt = GENEROS_ESPANOL[genero]

            # Preparar semillas
            semillas = [semilla] if semilla else self.config.semillas

            # Generar música
            resultado = self._pipeline(
                format=self.config.formato_salida,
                audio_duration=duracion,
                prompt=prompt,
                lyrics=letra,
                infer_step=self.config.pasos_inferencia,
                guidance_scale=self.config.escala_guia,
                scheduler_type=self.config.tipo_scheduler,
                cfg_type=self.config.tipo_cfg,
                omega_scale=self.config.escala_omega,
                manual_seeds=semillas,
                guidance_interval=self.config.intervalo_guia,
                guidance_interval_decay=self.config.decaimiento_guia,
                min_guidance_scale=self.config.escala_guia_minima,
                use_erg_tag=self.config.usar_erg_tag,
                use_erg_lyric=self.config.usar_erg_letra,
                use_erg_diffusion=self.config.usar_erg_difusion,
                save_path=ruta_salida,
            )

            # Extraer información del resultado
            if isinstance(resultado, list) and len(resultado) > 0:
                ruta_audio = resultado[0] if isinstance(resultado[0], str) else None
                params = resultado[-1] if isinstance(resultado[-1], dict) else {}

                return ResultadoGeneracion(
                    exitoso=True,
                    ruta_audio=ruta_audio,
                    mensaje="Generación completada exitosamente",
                    parametros=params,
                    tiempos=params.get("timecosts", {}),
                    semillas_usadas=params.get("actual_seeds", [])
                )
            else:
                return ResultadoGeneracion(
                    exitoso=False,
                    mensaje="El modelo no retornó un resultado válido"
                )

        except Exception as e:
            return ResultadoGeneracion(
                exitoso=False,
                mensaje=f"Error durante la generación: {str(e)}"
            )

    def generar_demo(self, genero: str = "pop_latino") -> ResultadoGeneracion:
        """
        Genera una demo rápida con parámetros optimizados.

        Args:
            genero: Género musical para la demo.

        Returns:
            ResultadoGeneracion con la información del resultado.
        """
        # Configuración optimizada para demo rápida
        config_demo = ConfiguracionGeneracion(
            duracion_segundos=30.0,
            pasos_inferencia=27,  # Menos pasos para mayor velocidad
            escala_guia=12.0,
        )

        # Crear generador temporal con config de demo
        generador_demo = GeneradorMusicaEspanol(config_demo)
        generador_demo._pipeline = self._pipeline
        generador_demo._inicializado = self._inicializado

        return generador_demo.generar_cancion(
            genero=genero,
            duracion=30.0,
            nombre_archivo=f"demo_{genero}"
        )


def crear_letra_personalizada(
    versos: List[str],
    coro: str,
    bridge: Optional[str] = None
) -> str:
    """
    Crea una letra con formato correcto a partir de componentes.

    Args:
        versos: Lista de versos (cada verso es un string con múltiples líneas)
        coro: El coro de la canción
        bridge: El bridge opcional

    Returns:
        Letra formateada correctamente.
    """
    partes = []

    for i, verso in enumerate(versos):
        partes.append(f"[verse]\n{verso}")
        if i == 0:
            partes.append(f"[chorus]\n{coro}")

    if bridge:
        partes.append(f"[bridge]\n{bridge}")
        partes.append(f"[chorus]\n{coro}")

    return "\n\n".join(partes)
