"""
3D Generation Service
"""
import os
import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime
import structlog

from app.models.generation import GenerationTask, GenerationStatus, GenerationResponse
from app.services.trellis_service import TrellisService

logger = structlog.get_logger(__name__)

class GenerationService:
    """Service for managing 3D generation tasks"""
    
    def __init__(self, trellis_service: TrellisService):
        self.trellis_service = trellis_service
        self.tasks: Dict[str, GenerationTask] = {}
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def start_generation(
        self,
        task_id: str,
        image,
        seed: int = 42,
        ss_guidance_strength: float = 7.5,
        ss_sampling_steps: int = 12,
        slat_guidance_strength: float = 3.0,
        slat_sampling_steps: int = 12
    ):
        """Start 3D generation task"""
        try:
            # Save image
            image_path = os.path.join(self.output_dir, f"{task_id}_input.png")
            image.save(image_path)
            
            # Create task
            task = GenerationTask(
                task_id=task_id,
                status=GenerationStatus.PROCESSING,
                image_path=image_path,
                parameters={
                    "seed": seed,
                    "ss_guidance_strength": ss_guidance_strength,
                    "ss_sampling_steps": ss_sampling_steps,
                    "slat_guidance_strength": slat_guidance_strength,
                    "slat_sampling_steps": slat_sampling_steps
                },
                created_at=datetime.utcnow()
            )
            
            self.tasks[task_id] = task
            
            # Start generation in background
            asyncio.create_task(self._process_generation(task_id))
            
            logger.info("Generation task started", task_id=task_id)
            
        except Exception as e:
            logger.error("Failed to start generation", task_id=task_id, error=str(e))
            if task_id in self.tasks:
                self.tasks[task_id].status = GenerationStatus.FAILED
                self.tasks[task_id].error_message = str(e)
            raise
    
    async def _process_generation(self, task_id: str):
        """Process 3D generation task"""
        try:
            task = self.tasks[task_id]
            
            # Load image
            from PIL import Image
            image = Image.open(task.image_path)
            
            # Generate 3D model
            outputs = await self.trellis_service.generate_3d_model(
                image=image,
                seed=task.parameters["seed"],
                ss_guidance_strength=task.parameters["ss_guidance_strength"],
                ss_sampling_steps=task.parameters["ss_sampling_steps"],
                slat_guidance_strength=task.parameters["slat_guidance_strength"],
                slat_sampling_steps=task.parameters["slat_sampling_steps"],
                formats=["gaussian", "mesh"]
            )
            
            # Generate GLB file
            glb_bytes = await self.trellis_service.generate_glb(
                outputs['gaussian'][0],
                outputs['mesh'][0]
            )
            
            # Save GLB file
            glb_path = os.path.join(self.output_dir, f"{task_id}.glb")
            with open(glb_path, 'wb') as f:
                f.write(glb_bytes)
            
            # Save PLY file
            ply_path = os.path.join(self.output_dir, f"{task_id}.ply")
            outputs['gaussian'][0].save_ply(ply_path)
            
            # Generate preview video
            video_frames = await self.trellis_service.generate_preview_video(
                outputs['gaussian'][0]
            )
            
            # Save video
            video_path = os.path.join(self.output_dir, f"{task_id}.mp4")
            import imageio
            imageio.mimsave(video_path, video_frames, fps=15)
            
            # Update task status
            task.status = GenerationStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.glb_path = glb_path
            task.ply_path = ply_path
            task.video_path = video_path
            task.updated_at = datetime.utcnow()
            
            logger.info("Generation task completed", task_id=task_id)
            
        except Exception as e:
            logger.error("Generation task failed", task_id=task_id, error=str(e))
            if task_id in self.tasks:
                self.tasks[task_id].status = GenerationStatus.FAILED
                self.tasks[task_id].error_message = str(e)
                self.tasks[task_id].updated_at = datetime.utcnow()
    
    async def get_status(self, task_id: str) -> GenerationResponse:
        """Get generation task status"""
        if task_id not in self.tasks:
            raise KeyError("Task not found")
        
        task = self.tasks[task_id]
        
        return GenerationResponse(
            task_id=task.task_id,
            status=task.status,
            message=self._get_status_message(task.status),
            created_at=task.created_at,
            updated_at=task.updated_at,
            glb_url=f"/api/v1/generation/download/{task_id}/glb" if task.glb_path else None,
            ply_url=f"/api/v1/generation/download/{task_id}/ply" if task.ply_path else None,
            preview_url=f"/api/v1/generation/preview/{task_id}" if task.video_path else None,
            parameters=task.parameters,
            error_message=task.error_message,
            error_code=task.error_code
        )
    
    def _get_status_message(self, status: GenerationStatus) -> str:
        """Get human-readable status message"""
        messages = {
            GenerationStatus.PENDING: "Task is pending",
            GenerationStatus.PROCESSING: "3D model is being generated",
            GenerationStatus.COMPLETED: "3D model generation completed",
            GenerationStatus.FAILED: "3D model generation failed",
            GenerationStatus.CANCELLED: "3D model generation cancelled"
        }
        return messages.get(status, "Unknown status")
    
    async def get_glb_path(self, task_id: str) -> str:
        """Get GLB file path"""
        if task_id not in self.tasks:
            raise KeyError("Task not found")
        
        task = self.tasks[task_id]
        if not task.glb_path or not os.path.exists(task.glb_path):
            raise FileNotFoundError("GLB file not found")
        
        return task.glb_path
    
    async def get_ply_path(self, task_id: str) -> str:
        """Get PLY file path"""
        if task_id not in self.tasks:
            raise KeyError("Task not found")
        
        task = self.tasks[task_id]
        if not task.ply_path or not os.path.exists(task.ply_path):
            raise FileNotFoundError("PLY file not found")
        
        return task.ply_path
    
    async def get_video_path(self, task_id: str) -> str:
        """Get preview video path"""
        if task_id not in self.tasks:
            raise KeyError("Task not found")
        
        task = self.tasks[task_id]
        if not task.video_path or not os.path.exists(task.video_path):
            raise FileNotFoundError("Preview video not found")
        
        return task.video_path
