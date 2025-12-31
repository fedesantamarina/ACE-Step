# POC ACE-Step en Español

Prueba de concepto para generación de música con letras en español usando el modelo ACE-Step.

## Descripción

Esta POC proporciona una interfaz en español para el modelo de generación de música ACE-Step, incluyendo:

- **Generador de música** con configuración en español
- **12 géneros musicales** latinos y españoles
- **Plantillas de letras** en español
- **Suite de tests** para validar el funcionamiento
- **Script de demostración** interactivo

## Requisitos

- Python 3.10+
- GPU con al menos 8GB de VRAM (recomendado: 16GB+)
- macOS, Linux o Windows

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/ACE-Step/ACE-Step.git
cd ACE-Step
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o en Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -e .
pip install pytest pytest-mock
```

## Estructura de la POC

```
poc_espanol/
├── __init__.py              # Inicialización del módulo
├── generador_musica.py      # Clase principal del generador
├── demo.py                  # Script de demostración
├── README.md                # Esta documentación
├── pytest.ini               # Configuración de pytest
└── tests/
    ├── __init__.py
    └── test_generador_musica.py  # Tests unitarios e integración
```

## Uso

### Listar géneros disponibles

```bash
python poc_espanol/demo.py --listar-generos
```

### Listar plantillas de letras

```bash
python poc_espanol/demo.py --listar-plantillas
```

### Generar música

```bash
# Generación básica (pop latino, 60 segundos)
python poc_espanol/demo.py

# Especificar género
python poc_espanol/demo.py --genero reggaeton

# Especificar duración
python poc_espanol/demo.py --genero balada --duracion 90

# Usar plantilla específica
python poc_espanol/demo.py --genero rock_espanol --plantilla reflexion

# Con semilla para reproducibilidad
python poc_espanol/demo.py --genero salsa --semilla 12345

# Con CPU offload para GPU con poca VRAM
python poc_espanol/demo.py --cpu-offload
```

### Uso programático

```python
from poc_espanol.generador_musica import (
    GeneradorMusicaEspanol,
    ConfiguracionGeneracion,
    PLANTILLAS_LETRAS,
)

# Crear configuración
config = ConfiguracionGeneracion(
    duracion_segundos=60.0,
    pasos_inferencia=60,
    usar_cpu_offload=True,
)

# Crear generador
generador = GeneradorMusicaEspanol(config)

# Generar canción
resultado = generador.generar_cancion(
    genero="reggaeton",
    letra=PLANTILLAS_LETRAS["fiesta"],
    duracion=60.0,
    semilla=42
)

if resultado.exitoso:
    print(f"Audio generado en: {resultado.ruta_audio}")
else:
    print(f"Error: {resultado.mensaje}")
```

## Géneros Disponibles

| Género | Descripción |
|--------|-------------|
| `pop_latino` | Pop latino tropical y pegadizo |
| `reggaeton` | Urban latino con dembow y trap |
| `balada` | Balada romántica y emotiva |
| `rock_espanol` | Rock en español energético |
| `cumbia` | Cumbia tropical festiva |
| `salsa` | Salsa con bronces y percusión |
| `bachata` | Bachata romántica dominicana |
| `flamenco` | Flamenco español apasionado |
| `mariachi` | Mariachi mexicano tradicional |
| `tango` | Tango argentino dramático |
| `urbano` | Trap y hip hop latino |
| `folclore` | Folclore acústico tradicional |

## Ejecutar Tests

### Tests unitarios (sin GPU)

```bash
# Todos los tests rápidos
pytest poc_espanol/tests/ -v

# Solo tests de configuración
pytest poc_espanol/tests/test_generador_musica.py::TestConfiguracionGeneracion -v

# Solo tests de validación
pytest poc_espanol/tests/test_generador_musica.py::TestValidacionLetras -v
```

### Tests de integración (requieren GPU)

```bash
# Ejecutar tests de integración
pytest poc_espanol/tests/ -v -m "integracion"
```

### Ver cobertura de tests

```bash
pip install pytest-cov
pytest poc_espanol/tests/ --cov=poc_espanol --cov-report=html
```

## Tests Incluidos

La suite de tests incluye:

### Tests Unitarios
- ✅ Configuración por defecto y personalizada
- ✅ Validación de géneros musicales
- ✅ Validación de plantillas de letras
- ✅ Validación de formato de letras
- ✅ Validación de parámetros de entrada
- ✅ Creación de letras personalizadas
- ✅ Importación de módulos ACE-Step

### Tests de Integración
- 🔧 Generación básica de música
- 🔧 Reproducibilidad con semillas
- 🔧 Diferentes géneros musicales

## Notas Importantes

1. **Primera ejecución**: El modelo (~7GB) se descargará automáticamente en `~/.cache/ace-step/checkpoints`

2. **Requisitos de GPU**:
   - Mínimo: 8GB VRAM con `--cpu-offload`
   - Recomendado: 16GB+ VRAM

3. **macOS**: Usar `--bf16 false` si hay errores

4. **Duración**:
   - Mínimo: 10 segundos
   - Máximo: 240 segundos (4 minutos)

## Solución de Problemas

### Error de memoria GPU

```bash
# Activar CPU offload
python poc_espanol/demo.py --cpu-offload
```

### Modelo no encontrado

El modelo se descarga automáticamente. Si hay problemas:

```bash
# Descargar manualmente
pip install huggingface_hub
huggingface-cli download ACE-Step/ACE-Step-v1-3.5B
```

### Tests fallan por importación

Asegúrate de que ACE-Step está instalado:

```bash
pip install -e .
```

## Licencia

Apache License 2.0 (igual que ACE-Step)
