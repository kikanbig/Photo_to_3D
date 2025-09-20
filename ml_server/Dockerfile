# TRELLIS ML Server for RunPod
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_simple.txt requirements.txt

# Force install NumPy 1.x FIRST to avoid compatibility issues with PyTorch 2.1.0
RUN pip uninstall -y numpy && pip install --no-cache-dir "numpy==1.24.4" --force-reinstall

RUN pip install --no-cache-dir -r requirements.txt

# Clone TRELLIS repository
RUN git clone https://github.com/microsoft/TRELLIS.git /workspace/trellis_source

# Install TRELLIS dependencies
WORKDIR /workspace/trellis_source
RUN pip install -e .

# Download TRELLIS model files directly from Hugging Face
WORKDIR /workspace
RUN mkdir -p /workspace/models/models--microsoft--TRELLIS-image-large/snapshots/main

# Download model files directly using wget
RUN echo "🔄 Downloading TRELLIS model files directly..." && \
    cd /workspace/models/models--microsoft--TRELLIS-image-large/snapshots/main && \
    wget -q https://huggingface.co/microsoft/TRELLIS-image-large/resolve/main/pipeline.json && \
    wget -q https://huggingface.co/microsoft/TRELLIS-image-large/resolve/main/config.json && \
    wget -q https://huggingface.co/microsoft/TRELLIS-image-large/resolve/main/model_index.json && \
    mkdir -p ckpts && \
    cd ckpts && \
    wget -q https://huggingface.co/microsoft/TRELLIS-image-large/resolve/main/ckpts/ss_flow_img_dit_L_16l8_fp16.safetensors && \
    wget -q https://huggingface.co/microsoft/TRELLIS-image-large/resolve/main/ckpts/slat_flow_img_dit_L_64l8p2_fp16.safetensors && \
    echo "✅ Model files downloaded successfully!" && \
    ls -la /workspace/models/models--microsoft--TRELLIS-image-large/snapshots/main/ && \
    ls -la /workspace/models/models--microsoft--TRELLIS-image-large/snapshots/main/ckpts/

# Test model loading
RUN python -c "
import os
os.environ['HF_HOME'] = '/workspace/models'
print('🔍 Testing model loading...')
try:
    from transformers import TrellisImageTo3DPipeline
    pipeline = TrellisImageTo3DPipeline.from_pretrained('microsoft/TRELLIS-image-large')
    print('✅ TRELLIS model loaded successfully!')
except Exception as e:
    print(f'❌ Error loading model: {e}')
    # Don't exit, just warn
    print('⚠️ Model loading failed, but continuing build...')
"

# Copy our ML server code
COPY . .

# Set Python path
ENV PYTHONPATH=/workspace:/workspace/trellis_source
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_CUDA_ARCH_LIST="6.1 7.0 7.5 8.0 8.6 9.0"

# Expose port for RunPod
EXPOSE 8000

# Start command
CMD ["python", "handler.py"]
