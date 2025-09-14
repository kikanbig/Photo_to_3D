"""
3D Generation API endpoints
"""
import io
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from PIL import Image
import structlog

from app.core.config import settings
from app.services.trellis_service import TrellisService
from app.models.generation import GenerationRequest, GenerationResponse, GenerationStatus
from app.services.generation_service import GenerationService

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_3d_model(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    seed: int = Form(42),
    ss_guidance_strength: float = Form(7.5),
    ss_sampling_steps: int = Form(12),
    slat_guidance_strength: float = Form(3.0),
    slat_sampling_steps: int = Form(12)
):
    """
    Generate 3D model from uploaded image
    """
    try:
        # Validate file
        if not image.content_type in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # Check file size
        if image.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Load and validate image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        logger.info(
            "Starting 3D generation",
            task_id=task_id,
            image_size=pil_image.size,
            user_id="anonymous"  # TODO: Get from auth
        )
        
        # Create TRELLIS service
        trellis_service = TrellisService()
        await trellis_service.initialize()
        
        # Start generation task
        generation_service = GenerationService(trellis_service)
        await generation_service.start_generation(
            task_id=task_id,
            image=pil_image,
            seed=seed,
            ss_guidance_strength=ss_guidance_strength,
            ss_sampling_steps=ss_sampling_steps,
            slat_guidance_strength=slat_guidance_strength,
            slat_sampling_steps=slat_sampling_steps
        )
        
        return GenerationResponse(
            task_id=task_id,
            status=GenerationStatus.PROCESSING,
            message="3D generation started"
        )
        
    except Exception as e:
        logger.error("Generation request failed", error=str(e))
        raise HTTPException(status_code=500, detail="Generation failed")

@router.get("/status/{task_id}", response_model=GenerationResponse)
async def get_generation_status(
    task_id: str
):
    """
    Get generation status by task ID
    """
    try:
        # For now, return a simple mock status
        # TODO: Implement proper status tracking with database
        return GenerationResponse(
            task_id=task_id,
            status=GenerationStatus.COMPLETED,
            message="Mock generation completed",
            glb_url=f"/api/v1/generation/download/{task_id}/glb",
            ply_url=f"/api/v1/generation/download/{task_id}/ply",
            preview_url=f"/api/v1/generation/preview/{task_id}"
        )
        
    except Exception as e:
        logger.error("Status check failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Status check failed")

@router.get("/download/{task_id}/glb")
async def download_glb(task_id: str):
    """
    Download GLB file for completed generation
    """
    try:
        # For demo purposes, create a simple mock GLB file
        import tempfile
        import os
        
        # Create temporary GLB file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.glb', delete=False) as f:
            f.write(b"mock_glb_data_for_demo")
            temp_path = f.name
        
        return FileResponse(
            path=temp_path,
            filename=f"model_{task_id}.glb",
            media_type="model/gltf-binary"
        )
        
    except Exception as e:
        logger.error("GLB download failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Download failed")

@router.get("/download/{task_id}/ply")
async def download_ply(task_id: str):
    """
    Download PLY file for completed generation
    """
    try:
        # For demo purposes, create a simple mock PLY file
        import tempfile
        
        ply_content = """ply
format ascii 1.0
element vertex 3
property float x
property float y
property float z
end_header
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ply', delete=False) as f:
            f.write(ply_content)
            temp_path = f.name
        
        return FileResponse(
            path=temp_path,
            filename=f"model_{task_id}.ply",
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error("PLY download failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Download failed")

@router.get("/preview/{task_id}")
async def get_preview_video(task_id: str):
    """
    Get preview video for completed generation
    """
    try:
        # Return a simple JSON response for now
        from fastapi.responses import JSONResponse
        return JSONResponse({
            "message": "Preview video not implemented yet",
            "task_id": task_id,
            "note": "This would return an MP4 video file in production"
        })
        
    except Exception as e:
        logger.error("Preview video failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Preview failed")
