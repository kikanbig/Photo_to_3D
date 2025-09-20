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
RUN pip install --no-cache-dir -r requirements.txt

# Force install NumPy 1.x to avoid compatibility issues with PyTorch 2.1.0
RUN pip uninstall -y numpy && pip install --no-cache-dir "numpy<2.0" --force-reinstall

# Clone TRELLIS repository
RUN git clone https://github.com/microsoft/TRELLIS.git /workspace/trellis_source

# Install TRELLIS dependencies
WORKDIR /workspace/trellis_source
RUN pip install -e .

# Download TRELLIS model locally during build
WORKDIR /workspace
RUN python -c "
import os
os.environ['HF_HOME'] = '/workspace/models'
from transformers import TrellisImageTo3DPipeline
print('🔄 Downloading TRELLIS model locally...')
pipeline = TrellisImageTo3DPipeline.from_pretrained('microsoft/TRELLIS-image-large')
print('✅ TRELLIS model downloaded successfully!')
print(f'📁 Model stored at: /workspace/models')
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
