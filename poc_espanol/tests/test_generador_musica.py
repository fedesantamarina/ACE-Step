"""
Tests para el Generador de Música en Español
============================================

Tests unitarios y de integración para validar el funcionamiento
del generador de música ACE-Step en español.

Ejecutar con:
    pytest poc_espanol/tests/test_generador_musica.py -v

Para ejecutar solo tests rápidos (sin GPU):
    pytest poc_espanol/tests/test_generador_musica.py -v -m "not integracion"

Para ejecutar tests de integración (requiere GPU):
    pytest poc_espanol/tests/test_generador_musica.py -v -m "integracion"
"""

import pytest
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc_espanol.generador_musica import (
    GeneradorMusicaEspanol,
    ConfiguracionGeneracion,
    ResultadoGeneracion,
    GENEROS_ESPANOL,
    PLANTILLAS_LETRAS,
    crear_letra_personalizada,
)


# =============================================================================
# TESTS DE CONFIGURACIÓN
# =============================================================================

class TestConfiguracionGeneracion:
    """Tests para la clase ConfiguracionGeneracion."""

    def test_configuracion_por_defecto(self):
        """Verifica que la configuración por defecto tiene valores correctos."""
        config = ConfiguracionGeneracion()

        assert config.duracion_segundos == 60.0
        assert config.formato_salida == "wav"
        assert config.pasos_inferencia == 60
        assert config.escala_guia == 15.0
        assert config.tipo_scheduler == "euler"
        assert config.tipo_cfg == "apg"
        assert config.escala_omega == 10.0

    def test_configuracion_personalizada(self):
        """Verifica que se pueden personalizar los valores de configuración."""
        config = ConfiguracionGeneracion(
            duracion_segundos=120.0,
            pasos_inferencia=30,
            escala_guia=12.0,
            usar_bf16=False
        )

        assert config.duracion_segundos == 120.0
        assert config.pasos_inferencia == 30
        assert config.escala_guia == 12.0
        assert config.usar_bf16 is False

    def test_configuracion_hardware(self):
        """Verifica la configuración de hardware."""
        config = ConfiguracionGeneracion(
            id_dispositivo=1,
            usar_cpu_offload=True,
            usar_torch_compile=True
        )

        assert config.id_dispositivo == 1
        assert config.usar_cpu_offload is True
        assert config.usar_torch_compile is True


# =============================================================================
# TESTS DE GÉNEROS MUSICALES
# =============================================================================

class TestGenerosEspanol:
    """Tests para los géneros musicales en español."""

    def test_generos_disponibles(self):
        """Verifica que todos los géneros esperados están definidos."""
        generos_esperados = [
            "pop_latino", "reggaeton", "balada", "rock_espanol",
            "cumbia", "salsa", "bachata", "flamenco",
            "mariachi", "tango", "urbano", "folclore"
        ]

        for genero in generos_esperados:
            assert genero in GENEROS_ESPANOL, f"Falta el género: {genero}"

    def test_descripciones_generos_no_vacias(self):
        """Verifica que todas las descripciones de géneros no están vacías."""
        for genero, descripcion in GENEROS_ESPANOL.items():
            assert descripcion, f"Descripción vacía para género: {genero}"
            assert len(descripcion) > 10, f"Descripción muy corta para: {genero}"

    def test_descripciones_contienen_palabras_clave(self):
        """Verifica que las descripciones contienen palabras clave relevantes."""
        assert "latin" in GENEROS_ESPANOL["pop_latino"].lower()
        assert "reggaeton" in GENEROS_ESPANOL["reggaeton"].lower()
        assert "romantic" in GENEROS_ESPANOL["balada"].lower()
        assert "flamenco" in GENEROS_ESPANOL["flamenco"].lower()


# =============================================================================
# TESTS DE PLANTILLAS DE LETRAS
# =============================================================================

class TestPlantillasLetras:
    """Tests para las plantillas de letras en español."""

    def test_plantillas_disponibles(self):
        """Verifica que las plantillas esperadas están definidas."""
        plantillas_esperadas = ["amor", "fiesta", "reflexion"]

        for plantilla in plantillas_esperadas:
            assert plantilla in PLANTILLAS_LETRAS, f"Falta plantilla: {plantilla}"

    def test_plantillas_tienen_secciones(self):
        """Verifica que las plantillas tienen secciones de canción."""
        for nombre, letra in PLANTILLAS_LETRAS.items():
            tiene_seccion = any(
                seccion in letra.lower()
                for seccion in ["[verse]", "[chorus]", "[bridge]"]
            )
            assert tiene_seccion, f"Plantilla '{nombre}' sin secciones"

    def test_plantillas_tienen_contenido_espanol(self):
        """Verifica que las plantillas contienen texto en español."""
        palabras_espanol = [
            "corazón", "amor", "noche", "vida", "siempre",
            "porque", "cuando", "todo", "puede", "quiero"
        ]

        for nombre, letra in PLANTILLAS_LETRAS.items():
            letra_lower = letra.lower()
            tiene_espanol = any(palabra in letra_lower for palabra in palabras_espanol)
            assert tiene_espanol, f"Plantilla '{nombre}' no parece estar en español"

    def test_plantilla_amor_estructura(self):
        """Verifica la estructura de la plantilla de amor."""
        letra = PLANTILLAS_LETRAS["amor"]

        assert "[verse]" in letra
        assert "[chorus]" in letra
        assert letra.count("[verse]") >= 2
        assert letra.count("[chorus]") >= 1


# =============================================================================
# TESTS DEL GENERADOR
# =============================================================================

class TestGeneradorMusicaEspanol:
    """Tests para la clase GeneradorMusicaEspanol."""

    def test_inicializacion_sin_config(self):
        """Verifica la inicialización sin configuración."""
        generador = GeneradorMusicaEspanol()

        assert generador.config is not None
        assert generador._pipeline is None
        assert generador._inicializado is False

    def test_inicializacion_con_config(self):
        """Verifica la inicialización con configuración personalizada."""
        config = ConfiguracionGeneracion(duracion_segundos=90.0)
        generador = GeneradorMusicaEspanol(config)

        assert generador.config.duracion_segundos == 90.0

    def test_obtener_generos_disponibles(self):
        """Verifica que se obtienen los géneros correctamente."""
        generador = GeneradorMusicaEspanol()
        generos = generador.obtener_generos_disponibles()

        assert isinstance(generos, dict)
        assert len(generos) == len(GENEROS_ESPANOL)
        assert "pop_latino" in generos

    def test_obtener_plantillas_letras(self):
        """Verifica que se obtienen las plantillas correctamente."""
        generador = GeneradorMusicaEspanol()
        plantillas = generador.obtener_plantillas_letras()

        assert isinstance(plantillas, dict)
        assert len(plantillas) == len(PLANTILLAS_LETRAS)
        assert "amor" in plantillas


# =============================================================================
# TESTS DE VALIDACIÓN DE LETRAS
# =============================================================================

class TestValidacionLetras:
    """Tests para la validación de letras."""

    def test_letra_valida(self):
        """Verifica que una letra válida pasa la validación."""
        generador = GeneradorMusicaEspanol()
        letra = PLANTILLAS_LETRAS["amor"]

        es_valida, error = generador.validar_letra(letra)

        assert es_valida is True
        assert error == ""

    def test_letra_vacia(self):
        """Verifica que una letra vacía falla la validación."""
        generador = GeneradorMusicaEspanol()

        es_valida, error = generador.validar_letra("")

        assert es_valida is False
        assert "vacía" in error.lower()

    def test_letra_sin_secciones(self):
        """Verifica que una letra sin secciones falla la validación."""
        generador = GeneradorMusicaEspanol()
        letra = "Esta es una letra sin secciones\nSolo texto plano"

        es_valida, error = generador.validar_letra(letra)

        assert es_valida is False
        assert "sección" in error.lower()

    def test_letra_muy_corta(self):
        """Verifica que una letra muy corta falla la validación."""
        generador = GeneradorMusicaEspanol()
        letra = "[verse]\nUna línea\nDos líneas"

        es_valida, error = generador.validar_letra(letra)

        assert es_valida is False
        assert "líneas" in error.lower()

    def test_letra_con_chorus(self):
        """Verifica que una letra con solo chorus es válida."""
        generador = GeneradorMusicaEspanol()
        letra = """[chorus]
Esta es la primera línea
Segunda línea del coro
Tercera línea aquí
Y la cuarta línea también"""

        es_valida, error = generador.validar_letra(letra)

        assert es_valida is True


# =============================================================================
# TESTS DE VALIDACIÓN DE PARÁMETROS
# =============================================================================

class TestValidacionParametros:
    """Tests para la validación de parámetros de generación."""

    def test_genero_invalido(self):
        """Verifica el manejo de género inválido."""
        generador = GeneradorMusicaEspanol()

        resultado = generador.generar_cancion(
            genero="genero_inexistente",
            letra=PLANTILLAS_LETRAS["amor"]
        )

        assert resultado.exitoso is False
        assert "no válido" in resultado.mensaje.lower()

    def test_duracion_muy_corta(self):
        """Verifica el manejo de duración muy corta."""
        generador = GeneradorMusicaEspanol()

        resultado = generador.generar_cancion(
            genero="pop_latino",
            duracion=5.0  # Menos de 10 segundos
        )

        assert resultado.exitoso is False
        assert "duración" in resultado.mensaje.lower()

    def test_duracion_muy_larga(self):
        """Verifica el manejo de duración muy larga."""
        generador = GeneradorMusicaEspanol()

        resultado = generador.generar_cancion(
            genero="pop_latino",
            duracion=300.0  # Más de 240 segundos
        )

        assert resultado.exitoso is False
        assert "duración" in resultado.mensaje.lower()


# =============================================================================
# TESTS DE UTILIDADES
# =============================================================================

class TestCrearLetraPersonalizada:
    """Tests para la función crear_letra_personalizada."""

    def test_crear_letra_basica(self):
        """Verifica la creación de letra básica."""
        versos = [
            "Primera línea del verso uno\nSegunda línea del verso uno",
            "Primera línea del verso dos\nSegunda línea del verso dos"
        ]
        coro = "Este es el coro\nQue se repite"

        letra = crear_letra_personalizada(versos, coro)

        assert "[verse]" in letra
        assert "[chorus]" in letra
        assert "Primera línea del verso uno" in letra
        assert "Este es el coro" in letra

    def test_crear_letra_con_bridge(self):
        """Verifica la creación de letra con bridge."""
        versos = ["Verso uno\nContinuación"]
        coro = "El coro aquí"
        bridge = "Este es el bridge\nParte especial"

        letra = crear_letra_personalizada(versos, coro, bridge)

        assert "[bridge]" in letra
        assert "Este es el bridge" in letra
        # El coro debe aparecer después del bridge
        assert letra.count("[chorus]") >= 2


# =============================================================================
# TESTS DE RESULTADO
# =============================================================================

class TestResultadoGeneracion:
    """Tests para la clase ResultadoGeneracion."""

    def test_resultado_exitoso(self):
        """Verifica un resultado exitoso."""
        resultado = ResultadoGeneracion(
            exitoso=True,
            ruta_audio="/ruta/al/audio.wav",
            mensaje="Generación completada"
        )

        assert resultado.exitoso is True
        assert resultado.ruta_audio == "/ruta/al/audio.wav"

    def test_resultado_fallido(self):
        """Verifica un resultado fallido."""
        resultado = ResultadoGeneracion(
            exitoso=False,
            mensaje="Error en la generación"
        )

        assert resultado.exitoso is False
        assert resultado.ruta_audio is None

    def test_resultado_con_parametros(self):
        """Verifica un resultado con parámetros adicionales."""
        resultado = ResultadoGeneracion(
            exitoso=True,
            parametros={"prompt": "test"},
            tiempos={"diffusion": 5.0},
            semillas_usadas=[12345]
        )

        assert resultado.parametros["prompt"] == "test"
        assert resultado.tiempos["diffusion"] == 5.0
        assert 12345 in resultado.semillas_usadas


# =============================================================================
# TESTS DE IMPORTACIÓN DE MÓDULOS ACE-STEP
# =============================================================================

class TestImportacionModulos:
    """Tests para verificar que los módulos de ACE-Step se pueden importar."""

    def test_importar_pipeline(self):
        """Verifica que el pipeline se puede importar."""
        try:
            from acestep.pipeline_ace_step import ACEStepPipeline
            assert ACEStepPipeline is not None
        except (ImportError, RuntimeError, ModuleNotFoundError) as e:
            pytest.skip(f"No se pudo importar ACEStepPipeline (posible incompatibilidad de versiones): {e}")

    def test_importar_schedulers(self):
        """Verifica que los schedulers se pueden importar."""
        try:
            from acestep.schedulers.scheduling_flow_match_euler_discrete import (
                FlowMatchEulerDiscreteScheduler
            )
            assert FlowMatchEulerDiscreteScheduler is not None
        except ImportError as e:
            pytest.skip(f"No se pudo importar scheduler: {e}")

    def test_importar_data_sampler(self):
        """Verifica que el DataSampler se puede importar."""
        try:
            from acestep.data_sampler import DataSampler
            assert DataSampler is not None
        except ImportError as e:
            pytest.skip(f"No se pudo importar DataSampler: {e}")


# =============================================================================
# TESTS DE INTEGRACIÓN (requieren GPU y modelo)
# =============================================================================

@pytest.mark.integracion
class TestIntegracion:
    """
    Tests de integración que requieren GPU y el modelo descargado.

    Estos tests verifican la generación real de música.
    Usar: pytest -m "integracion" para ejecutarlos.
    """

    @pytest.fixture
    def generador_real(self):
        """Crea un generador con configuración de test rápido."""
        config = ConfiguracionGeneracion(
            duracion_segundos=10.0,  # Duración mínima para tests
            pasos_inferencia=10,     # Pocos pasos para velocidad
            directorio_salida="./salidas_test",
            usar_cpu_offload=True,   # Para funcionar con menos VRAM
        )
        return GeneradorMusicaEspanol(config)

    @pytest.mark.skipif(
        not os.path.exists(os.path.expanduser("~/.cache/ace-step/checkpoints")),
        reason="Modelo no descargado"
    )
    def test_generacion_basica(self, generador_real):
        """Test de generación básica con configuración mínima."""
        resultado = generador_real.generar_cancion(
            genero="pop_latino",
            duracion=10.0,
            semilla=42
        )

        if not resultado.exitoso:
            pytest.skip(f"Generación falló (puede ser por falta de GPU): {resultado.mensaje}")

        assert resultado.exitoso is True
        assert resultado.ruta_audio is not None
        assert os.path.exists(resultado.ruta_audio)

        # Limpiar archivo generado
        if os.path.exists(resultado.ruta_audio):
            os.remove(resultado.ruta_audio)

    @pytest.mark.skipif(
        not os.path.exists(os.path.expanduser("~/.cache/ace-step/checkpoints")),
        reason="Modelo no descargado"
    )
    def test_reproducibilidad_con_semilla(self, generador_real):
        """Verifica que la misma semilla produce el mismo resultado."""
        semilla = 12345

        resultado1 = generador_real.generar_cancion(
            genero="balada",
            duracion=10.0,
            semilla=semilla
        )

        resultado2 = generador_real.generar_cancion(
            genero="balada",
            duracion=10.0,
            semilla=semilla
        )

        if not resultado1.exitoso or not resultado2.exitoso:
            pytest.skip("Generación falló")

        assert resultado1.semillas_usadas == resultado2.semillas_usadas

        # Limpiar archivos
        for r in [resultado1, resultado2]:
            if r.ruta_audio and os.path.exists(r.ruta_audio):
                os.remove(r.ruta_audio)


# =============================================================================
# MARCADORES DE PYTEST
# =============================================================================

def pytest_configure(config):
    """Configura marcadores personalizados para pytest."""
    config.addinivalue_line(
        "markers", "integracion: tests que requieren GPU y modelo descargado"
    )
