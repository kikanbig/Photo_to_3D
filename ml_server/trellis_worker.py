"""
TRELLIS Worker for 3D Generation
"""
import os
import sys
import tempfile
import logging
from typing import Dict, Optional, Any
from PIL import Image
import torch
import numpy as np

# Add TRELLIS to Python path
trellis_path = '/workspace/trellis_source'
sys.path.append(trellis_path)

# Debug information
print(f"🔍 Python path: {sys.path}")
print(f"🔍 TRELLIS path exists: {os.path.exists(trellis_path)}")
if os.path.exists(trellis_path):
    print(f"🔍 TRELLIS contents: {os.listdir(trellis_path)}")

try:
    print("🔄 Attempting to import TRELLIS...")
    from trellis.pipelines import TrellisImageTo3DPipeline
    from trellis.utils import render_utils, postprocessing_utils
    TRELLIS_AVAILABLE = True
    print("✅ TRELLIS modules imported successfully")
except ImportError as e:
    print(f"❌ TRELLIS import failed: {e}")
    print(f"❌ Import error type: {type(e)}")
    import traceback
    print(f"❌ Full traceback: {traceback.format_exc()}")
    TRELLIS_AVAILABLE = False

class TrellisWorker:
    """Worker class for TRELLIS 3D generation"""
    
    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_initialized = False
        
        print(f"🔧 TrellisWorker initialized on device: {self.device}")
        
        # Initialize pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize TRELLIS pipeline"""
        if not TRELLIS_AVAILABLE:
            print("⚠️ TRELLIS not available, using mock mode")
            self.pipeline = "mock"
            self.is_initialized = True
            return
        
        try:
            print("📦 Loading TRELLIS pipeline...")
            
            # Set environment variables
            os.environ.setdefault("ATTN_BACKEND", "flash-attn")
            os.environ.setdefault("SPCONV_ALGO", "native")
            
            # Load pipeline
            model_path = os.environ.get("TRELLIS_MODEL_PATH", "microsoft/TRELLIS-image-large")
            print(f"📥 Loading model: {model_path}")
            
            self.pipeline = TrellisImageTo3DPipeline.from_pretrained(model_path)
            
            if self.device == "cuda":
                self.pipeline = self.pipeline.cuda()
            else:
                self.pipeline = self.pipeline.cpu()
            
            self.is_initialized = True
            print("✅ TRELLIS pipeline loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize TRELLIS pipeline: {e}")
            print("🔄 Falling back to mock mode")
            self.pipeline = "mock"
            self.is_initialized = True
    
    def generate_3d(
        self,
        image_path: str,
        seed: int = 42,
        ss_guidance_strength: float = 7.5,
        ss_sampling_steps: int = 12,
        slat_guidance_strength: float = 3.0,
        slat_sampling_steps: int = 12,
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate 3D model from image
        
        Returns:
            Dict with file paths: {"glb_path": "...", "ply_path": "...", "preview_path": "..."}
        """
        
        if not self.is_initialized:
            raise RuntimeError("TrellisWorker not initialized")
        
        # Load and preprocess image
        print(f"📷 Loading image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        
        # Resize image if needed
        max_size = 512
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"📐 Resized image to: {image.size}")
        
        if self.pipeline == "mock":
            return self._generate_mock_3d(image_path)
        
        try:
            print("🧠 Running TRELLIS inference...")
            
            # Set random seed
            torch.manual_seed(seed)
            np.random.seed(seed)
            
            # Generate 3D
            with torch.no_grad():
                # Run pipeline
                outputs = self.pipeline(
                    image,
                    seed=seed,
                    formats=["gaussian", "mesh"],
                    preprocess_image=True,
                    sparse_structure_sampler_params={
                        "steps": ss_sampling_steps,
                        "cfg_strength": ss_guidance_strength,
                    },
                    slat_sampler_params={
                        "steps": slat_sampling_steps, 
                        "cfg_strength": slat_guidance_strength,
                    }
                )
            
            print("✅ TRELLIS inference completed")
            
            # Extract results
            gaussian = outputs.get('gaussian', [None])[0]
            mesh = outputs.get('mesh', [None])[0]
            
            # Save outputs
            result_paths = {}
            
            # Save GLB file
            if mesh is not None:
                glb_path = tempfile.mktemp(suffix='.glb')
                mesh.export(glb_path)
                result_paths['glb_path'] = glb_path
                print(f"💾 GLB saved: {glb_path}")
            
            # Save PLY file
            if gaussian is not None:
                ply_path = tempfile.mktemp(suffix='.ply')
                gaussian.save_ply(ply_path)
                result_paths['ply_path'] = ply_path
                print(f"💾 PLY saved: {ply_path}")
            
            # Generate preview video
            if gaussian is not None:
                try:
                    preview_path = tempfile.mktemp(suffix='.mp4')
                    render_utils.render_video(gaussian, preview_path, num_frames=30)
                    result_paths['preview_path'] = preview_path
                    print(f"🎥 Preview video saved: {preview_path}")
                except Exception as e:
                    print(f"⚠️ Preview generation failed: {e}")
            
            return result_paths
            
        except Exception as e:
            print(f"❌ TRELLIS generation failed: {e}")
            raise
    
    def _generate_mock_3d(self, image_path: str) -> Dict[str, str]:
        """Generate mock 3D files for testing"""
        print("🎭 Generating mock 3D files...")
        
        # Create mock GLB file
        glb_path = tempfile.mktemp(suffix='.glb')
        with open(glb_path, 'wb') as f:
            f.write(b"mock_glb_data_for_demo_purposes")
        
        # Create mock PLY file
        ply_path = tempfile.mktemp(suffix='.ply')
        ply_content = """ply
format ascii 1.0
element vertex 4
property float x
property float y
property float z
end_header
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
"""
        with open(ply_path, 'w') as f:
            f.write(ply_content)
        
        print("✅ Mock 3D files generated")
        
        return {
            'glb_path': glb_path,
            'ply_path': ply_path
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.pipeline and self.pipeline != "mock":
            del self.pipeline
            self.pipeline = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("🧹 TrellisWorker cleaned up")
