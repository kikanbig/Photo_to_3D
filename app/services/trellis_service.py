"""
TRELLIS 3D Generation Service
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
import torch
import numpy as np
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

class TrellisService:
    """Service for 3D model generation using TRELLIS"""
    
    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize TRELLIS pipeline"""
        try:
            # Set environment variables for TRELLIS
            os.environ['ATTN_BACKEND'] = settings.ATTN_BACKEND
            os.environ['SPCONV_ALGO'] = settings.SPCONV_ALGO
            os.environ['CUDA_VISIBLE_DEVICES'] = settings.CUDA_VISIBLE_DEVICES
            
            # Import TRELLIS modules
            from trellis.pipelines import TrellisImageTo3DPipeline
            from trellis.utils import render_utils, postprocessing_utils
            
            logger.info("Loading TRELLIS pipeline", model_path=settings.TRELLIS_MODEL_PATH)
            
            # Load pipeline in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.pipeline = await loop.run_in_executor(
                None, 
                self._load_pipeline
            )
            
            self.is_initialized = True
            logger.info("TRELLIS pipeline loaded successfully")
            
        except Exception as e:
            logger.error("Failed to initialize TRELLIS service", error=str(e))
            raise
    
    def _load_pipeline(self):
        """Load TRELLIS pipeline (runs in executor)"""
        from trellis.pipelines import TrellisImageTo3DPipeline
        
        pipeline = TrellisImageTo3DPipeline.from_pretrained(settings.TRELLIS_MODEL_PATH)
        pipeline.cuda() if self.device == "cuda" else pipeline.cpu()
        return pipeline
    
    async def generate_3d_model(
        self,
        image: Image.Image,
        seed: int = 42,
        ss_guidance_strength: float = 7.5,
        ss_sampling_steps: int = 12,
        slat_guidance_strength: float = 3.0,
        slat_sampling_steps: int = 12,
        formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate 3D model from image
        
        Args:
            image: Input PIL Image
            seed: Random seed for generation
            ss_guidance_strength: Sparse structure guidance strength
            ss_sampling_steps: Sparse structure sampling steps
            slat_guidance_strength: Structured latent guidance strength
            slat_sampling_steps: Structured latent sampling steps
            formats: Output formats (gaussian, mesh, radiance_field)
            
        Returns:
            Dictionary containing generated 3D assets
        """
        if not self.is_initialized:
            raise RuntimeError("TRELLIS service not initialized")
        
        if formats is None:
            formats = ["gaussian", "mesh"]
        
        logger.info(
            "Starting 3D generation",
            seed=seed,
            formats=formats,
            image_size=image.size
        )
        
        try:
            # Run generation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(
                None,
                self._run_generation,
                image,
                seed,
                ss_guidance_strength,
                ss_sampling_steps,
                slat_guidance_strength,
                slat_sampling_steps,
                formats
            )
            
            logger.info("3D generation completed successfully")
            return outputs
            
        except Exception as e:
            logger.error("3D generation failed", error=str(e))
            raise
    
    def _run_generation(
        self,
        image: Image.Image,
        seed: int,
        ss_guidance_strength: float,
        ss_sampling_steps: int,
        slat_guidance_strength: float,
        slat_sampling_steps: int,
        formats: List[str]
    ) -> Dict[str, Any]:
        """Run TRELLIS generation (runs in executor)"""
        return self.pipeline.run(
            image,
            seed=seed,
            formats=formats,
            preprocess_image=True,
            sparse_structure_sampler_params={
                "steps": ss_sampling_steps,
                "cfg_strength": ss_guidance_strength,
            },
            slat_sampler_params={
                "steps": slat_sampling_steps,
                "cfg_strength": slat_guidance_strength,
            },
        )
    
    async def generate_glb(
        self,
        gaussian_output,
        mesh_output,
        simplify: float = 0.95,
        texture_size: int = 1024
    ) -> bytes:
        """
        Generate GLB file from 3D outputs
        
        Args:
            gaussian_output: Gaussian representation
            mesh_output: Mesh representation
            simplify: Mesh simplification ratio
            texture_size: Texture resolution
            
        Returns:
            GLB file as bytes
        """
        try:
            from trellis.utils import postprocessing_utils
            
            logger.info("Generating GLB file", simplify=simplify, texture_size=texture_size)
            
            # Generate GLB in executor
            loop = asyncio.get_event_loop()
            glb = await loop.run_in_executor(
                None,
                postprocessing_utils.to_glb,
                gaussian_output,
                mesh_output,
                simplify,
                texture_size,
                False  # verbose
            )
            
            # Export to bytes
            glb_bytes = glb.export()
            
            logger.info("GLB file generated successfully", size_bytes=len(glb_bytes))
            return glb_bytes
            
        except Exception as e:
            logger.error("GLB generation failed", error=str(e))
            raise
    
    async def generate_preview_video(
        self,
        gaussian_output,
        num_frames: int = 120
    ) -> np.ndarray:
        """
        Generate preview video from 3D output
        
        Args:
            gaussian_output: Gaussian representation
            num_frames: Number of frames in video
            
        Returns:
            Video frames as numpy array
        """
        try:
            from trellis.utils import render_utils
            
            logger.info("Generating preview video", num_frames=num_frames)
            
            # Generate video in executor
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None,
                render_utils.render_video,
                gaussian_output,
                num_frames
            )
            
            logger.info("Preview video generated successfully")
            return video['color']
            
        except Exception as e:
            logger.error("Preview video generation failed", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_initialized = False
        logger.info("TRELLIS service cleaned up")
