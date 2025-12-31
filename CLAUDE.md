# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ACE-Step is an open-source foundation model for music generation that bridges the gap between LLM-based and diffusion-based approaches. It uses diffusion generation with Sana's Deep Compression AutoEncoder (DCAE) and a lightweight linear transformer to generate up to 4 minutes of music in ~20 seconds on an A100 GPU. The model supports 19 languages, multiple music genres, and advanced control features like lyric editing, voice cloning, and audio repainting.

## Core Commands

### Quick Start (Recommended)

```bash
# One-command startup (macOS optimized)
./start.sh

# The start.sh script automatically:
# - Detects macOS and configures bf16=false
# - Activates/creates virtual environment
# - Installs dependencies if needed
# - Opens browser automatically
# - Enables network access (0.0.0.0) for other devices
# - Shows local IP for access from tablets/phones on same network
```

See `START_GUIDE.md` for detailed usage and troubleshooting.

### Installation & Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# For training capabilities
pip install -e .[train]

# Windows-specific for torch.compile support
pip install triton-windows
```

### Running the Application

```bash
# Basic launch (Gradio UI)
acestep --port 7865

# With network access (for other devices on same WiFi)
acestep --server_name 0.0.0.0 --port 7865

# With optimizations for low VRAM (8GB minimum)
acestep --torch_compile true --cpu_offload true --overlapped_decode true

# macOS-specific (avoid bfloat16 errors)
acestep --bf16 false --server_name 0.0.0.0 --port 7865

# Development mode with custom checkpoint
acestep --checkpoint_path /path/to/checkpoint --device_id 0
```

### Inference (Programmatic)

```bash
# Basic inference
python infer.py --checkpoint_path /path/to/checkpoint --output_path ./output

# With optimizations
python infer.py --torch_compile true --cpu_offload true --overlapped_decode true
```

### Training

```bash
# Convert audio data to HuggingFace dataset format
python convert2hf_dataset.py --data_dir "./data" --repeat_count 2000 --output_name "zh_lora_dataset"

# Train LoRA adapter
python trainer.py \
  --dataset_path "./zh_lora_dataset" \
  --exp_name "my_lora" \
  --lora_config_path "config/zh_rap_lora_config.json" \
  --learning_rate 1e-4 \
  --max_steps 200000 \
  --every_n_train_steps 2000 \
  --devices 1
```

### Testing

```bash
# Run tests for Spanish PoC
pytest poc_espanol/tests/ -v

# Run only integration tests (requires GPU)
pytest poc_espanol/tests/ -v -m "integracion"

# With coverage report
pytest poc_espanol/tests/ --cov=poc_espanol --cov-report=html
```

## Architecture Overview

### Three-Stage Pipeline Architecture

ACE-Step uses a three-stage pipeline for music generation:

1. **Text Encoding Stage** (`acestep.pipeline_ace_step.ACEStepPipeline`)
   - **Text Encoder**: UMT5EncoderModel for processing tags/descriptions
   - **Lyric Tokenizer**: VoiceBpeTokenizer for multi-language lyric processing (19 languages)
   - **Language Segmentation**: Automatic language detection and segmentation for mixed-language lyrics
   - Produces text embeddings and lyric tokens that condition the generation

2. **Diffusion Generation Stage** (`acestep.models.ace_step_transformer.ACEStepTransformer2DModel`)
   - **Flow-Matching Transformer**: Lightweight linear transformer that generates latent representations
   - **Schedulers**: Three scheduler types available:
     - `FlowMatchEulerDiscreteScheduler` (default, fast)
     - `FlowMatchHeunDiscreteScheduler` (higher quality)
     - `FlowMatchPingPongScheduler` (SDE-based, best consistency)
   - **Guidance Mechanisms**:
     - APG (Adversarial Prompt Guidance) for style control
     - CFG (Classifier-Free Guidance) variants (zero_star, double_condition)
     - ERG (Enhanced Residual Guidance) for tags, lyrics, and diffusion
   - **Attention Processors**: Custom attention mechanisms for music coherence
   - Operates on compressed latent space (not raw audio)

3. **Audio Decoding Stage** (`acestep.music_dcae.MusicDCAE`)
   - **DCAE (Deep Compression AutoEncoder)**: Decodes latents to mel-spectrogram
   - **Vocoder**: Converts mel-spectrogram to final audio waveform
   - **Overlapped Decode**: Optional sliding window decoding for memory efficiency
   - Supports both standard and overlapped decoding modes

### Key Architectural Patterns

- **CPU Offloading** (`acestep.cpu_offload`): Load models to GPU only when needed, reducing VRAM from 16GB to 8GB
- **Torch Compile**: JIT compilation for 20-30% speed improvement (requires triton on Windows)
- **LoRA Training**: Parameter-efficient fine-tuning targeting attention layers (q, k, v, speaker_embedder)
- **Gradient Checkpointing**: Enabled during training to reduce memory usage
- **Flow-Matching**: Uses continuous-time flow matching instead of discrete diffusion steps

### Data Processing Pipeline

**Training Data Format** (see `convert2hf_dataset.py`):
- Each audio sample requires 3 files:
  - `filename.mp3` - Audio file
  - `filename_prompt.txt` - Comma-separated tags (genre, mood, tempo, key, instruments)
  - `filename_lyrics.txt` - Structured lyrics with [Verse], [Chorus] tags
- Converted to HuggingFace Dataset format with features: keys, filename, tags, norm_lyrics

**Dataset Loading** (`acestep.text2music_dataset.Text2MusicDataset`):
- Filters silent audio (>95% silence threshold)
- Multi-language lyric processing with automatic language detection
- Structure-aware lyric parsing (verse/chorus/bridge tags)
- Max duration: 240 seconds (4 minutes)

## Important Configuration Files

- `config/zh_rap_lora_config.json` - LoRA training configuration
  - `r`: Rank of LoRA matrices (256 default, reduce for low VRAM)
  - `lora_alpha`: Scaling factor (32 default)
  - `target_modules`: Attention layers to fine-tune
  - `use_rslora`: Rank-stabilized LoRA

## Supported Languages & Their Token IDs

The model supports 19 languages with specific token IDs used for language conditioning:
- English (259), German (260), French (262), Spanish (284), Italian (285)
- Portuguese (286), Polish (294), Turkish (295), Russian (267), Czech (293)
- Dutch (297), Arabic (5022), Chinese (5023), Japanese (5412), Hungarian (5753)
- Korean (6152), Hindi (6680)

Top 10 best-performing: English, Chinese, Russian, Spanish, Japanese, German, French, Portuguese, Italian, Korean

## Training Data Requirements

**Critical Training File Format**:
- **Strict naming**: `filename.mp3`, `filename_prompt.txt`, `filename_lyrics.txt`
- **No JSON support**: Only simple text files work
- **Prompt format**: Simple comma-separated tags only (no complex multi-variant descriptions)
- **Lyrics format**: Standard lyrics with optional [Verse], [Chorus], [Bridge] structure tags

**Example Prompt Tags**:
```
melodic techno, male vocal, electronic, emotional, minor key, 124 bpm, synthesizer, driving, atmospheric
```

**Example Lyrics**:
```
[Verse]
Lately I've been wondering
Why do I do this to myself

[Chorus]
It makes me want to cry
If you knew what you meant to me
```

## Memory Optimization Strategies

1. **8GB VRAM Setup** (minimum):
   ```bash
   acestep --cpu_offload true --overlapped_decode true
   ```

2. **16GB+ VRAM Setup** (recommended):
   ```bash
   acestep --torch_compile true
   ```

3. **Training on Limited VRAM**:
   - Reduce LoRA rank: `"r": 16` instead of 256
   - Reduce LoRA alpha: `"lora_alpha": 16` instead of 32
   - Use gradient accumulation: `--accumulate_grad_batches 4`
   - Enable CPU offloading during training

## Spanish PoC (poc_espanol/)

A complete proof-of-concept for Spanish music generation with:
- 12 Latin/Spanish music genres (reggaeton, salsa, bachata, tango, flamenco, etc.)
- Spanish lyric templates
- Test suite (unit + integration tests)
- Demo script with CLI interface

**Usage**:
```bash
# List genres
python poc_espanol/demo.py --listar-generos

# Generate music
python poc_espanol/demo.py --genero reggaeton --duracion 60

# Run tests
pytest poc_espanol/tests/ -v
```

## Model Downloads

Models are automatically downloaded from HuggingFace on first run:
- **Default path**: `~/.cache/ace-step/checkpoints`
- **Custom path**: Use `--checkpoint_path` flag
- **Repository**: ACE-Step/ACE-Step-v1-3.5B (~7GB)

## Advanced Features

### Variations Generation
- Uses trigFlow's noise formula to add Gaussian noise to initial noise
- Controlled via mixing ratio between original and new noise

### Repainting (Audio2Audio)
- Add noise to target audio and apply mask constraints during ODE process
- Can modify specific sections while preserving the rest
- Supports style transfer, lyric changes, vocal swapping

### Lyric Editing
- Uses flow-edit technology for localized lyric modifications
- Preserves melody, vocals, and accompaniment
- Can only modify small segments at once (apply multiple edits sequentially)

## Performance Benchmarks

| Device | RTF (27 steps) | Time (1 min audio, 27 steps) |
|--------|----------------|------------------------------|
| RTX 4090 | 34.48× | 1.74s |
| A100 | 27.27× | 2.20s |
| RTX 3090 | 12.76× | 4.70s |
| M2 Max | 2.27× | 26.43s |

RTF = Real-Time Factor (higher is faster)

## Common Pitfalls

1. **macOS bfloat16 errors**: Always use `--bf16 false` on macOS
2. **Training file format**: JSON files are NOT supported for training data
3. **LoRA config required**: Training MUST specify `--lora_config_path`
4. **Silent audio filtering**: Audio with >95% silence is automatically skipped during training
5. **Language tokens**: Lyrics must use supported languages or will default to English
6. **Structure tags**: Use `[Verse]`, `[Chorus]`, `[Bridge]` (case-sensitive, with brackets)
7. **Windows torch.compile**: Requires `pip install triton-windows`
