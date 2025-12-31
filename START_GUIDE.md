# Guía de Inicio Rápido - ACE-Step

## 🚀 Inicio Rápido con start.sh

### Para macOS

```bash
# 1. Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh

# 2. Ejecutar el script
./start.sh
```

El script automáticamente:
- ✅ Detecta que estás en macOS
- ✅ Desactiva bf16 (no compatible con Mac)
- ✅ Activa el entorno virtual (o lo crea si no existe)
- ✅ Instala las dependencias necesarias
- ✅ Abre el navegador automáticamente
- ✅ Permite acceso desde otros dispositivos en tu red local

### Acceso desde otros dispositivos

Una vez iniciado, verás las URLs de acceso:

```
📱 Acceso LOCAL:
   http://localhost:7865

🌐 Acceso desde RED LOCAL:
   http://192.168.1.X:7865
```

Comparte la URL de red local con otros dispositivos (tablets, otros ordenadores) conectados a la misma red WiFi.

### Para detener el servidor

Presiona `Ctrl+C` en la terminal.

## ⚙️ Personalización

### Cambiar el puerto

Edita el archivo `start.sh` y cambia la línea:

```bash
PORT=7865
```

Por ejemplo, para usar el puerto 8080:

```bash
PORT=8080
```

### Activar optimizaciones (solo si tienes problemas de memoria)

En el archivo `start.sh`, busca la sección:

```bash
# Optimizaciones específicas para Mac
if [ "$IS_MAC" = true ]; then
    print_info "Aplicando optimizaciones para macOS..."
    # No agregamos torch_compile ni cpu_offload en Mac por defecto
```

Y puedes agregar:

```bash
if [ "$IS_MAC" = true ]; then
    print_info "Aplicando optimizaciones para macOS..."
    PARAMS="$PARAMS --cpu_offload true --overlapped_decode true"
```

**Nota**: Estas optimizaciones reducen el uso de memoria pero pueden hacer la generación más lenta en Mac.

## 🔧 Solución de Problemas

### Error: "Permission denied"

```bash
chmod +x start.sh
./start.sh
```

### Error: "Python not found"

Asegúrate de tener Python 3.10+ instalado:

```bash
python3 --version
```

### Error: "Module not found"

El script instalará automáticamente las dependencias, pero si hay problemas:

```bash
source venv/bin/activate
pip install -e .
```

### No se abre el navegador automáticamente

Abre manualmente:
- Local: http://localhost:7865
- Red local: http://TU_IP_LOCAL:7865

### Otros dispositivos no pueden conectarse

1. Verifica que estén en la misma red WiFi
2. Verifica el firewall de macOS:
   - Ve a Preferencias del Sistema → Seguridad y Privacidad → Firewall
   - Asegúrate de permitir conexiones entrantes para Python

## 📝 Modo Manual (alternativa)

Si prefieres no usar el script:

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar en Mac
acestep --server_name 0.0.0.0 --port 7865 --bf16 false

# Abrir navegador
open http://localhost:7865
```

## 🌐 Acceso Público (Internet)

Si quieres compartir tu interfaz por Internet (no solo red local):

```bash
# Edita start.sh y cambia PARAMS para incluir --share true
PARAMS="--server_name 0.0.0.0 --port $PORT --bf16 $BF16_FLAG --share true"
```

Gradio generará un link público temporal (válido por 72 horas).

## ⚡ Rendimiento en Mac

- **M1/M2/M3 Max**: Buen rendimiento (~26s para 1 min de audio en M2 Max)
- **M1/M2/M3 Base**: Funcional pero más lento
- **Intel Mac**: Más lento, considera usar cpu_offload

## 📋 Características del Script

El script `start.sh` incluye:

- 🔍 **Detección automática** de macOS vs Linux
- 🎨 **Output colorizado** para mejor legibilidad
- 🔧 **Configuración automática** de parámetros según el OS
- 🌐 **Detección de IP local** para acceso en red
- 🌍 **Apertura automática** del navegador
- ✅ **Verificación de dependencias**
- 🛡️ **Manejo de errores** con mensajes claros
- 🧹 **Salida limpia** con Ctrl+C

## 💡 Consejos

1. **Primera ejecución**: Tardará más tiempo (descarga del modelo ~7GB)
2. **Modelo guardado en**: `~/.cache/ace-step/checkpoints`
3. **Uso de red**: Mejor usar cable ethernet para dispositivos de alta demanda
4. **Mac con poca RAM**: Cierra otras aplicaciones antes de iniciar
