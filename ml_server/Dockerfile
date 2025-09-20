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
import sys
os.environ['HF_HOME'] = '/workspace/models'
print('🔄 Downloading TRELLIS model locally...')
print(f'📁 HF_HOME set to: {os.environ[\"HF_HOME\"]}')

try:
    from transformers import TrellisImageTo3DPipeline
    print('✅ Transformers imported successfully')
    
    # Try to download the model
    pipeline = TrellisImageTo3DPipeline.from_pretrained('microsoft/TRELLIS-image-large')
    print('✅ TRELLIS model downloaded successfully!')
    
    # Check if model files exist
    model_dir = '/workspace/models'
    if os.path.exists(model_dir):
        print(f'📁 Model directory exists: {model_dir}')
        for root, dirs, files in os.walk(model_dir):
            level = root.replace(model_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f'{subindent}{file}')
            if len(files) > 5:
                print(f'{subindent}... and {len(files) - 5} more files')
    else:
        print('❌ Model directory not found!')
        
except Exception as e:
    print(f'❌ Error downloading model: {e}')
    sys.exit(1)
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
