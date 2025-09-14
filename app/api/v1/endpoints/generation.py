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
    slat_sampling_steps: int = Form(12),
    trellis_service: TrellisService = Depends(lambda: None)  # Will be injected
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
    task_id: str,
    generation_service: GenerationService = Depends(lambda: None)  # Will be injected
):
    """
    Get generation status by task ID
    """
    try:
        status = await generation_service.get_status(task_id)
        return status
        
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error("Status check failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Status check failed")

@router.get("/download/{task_id}/glb")
async def download_glb(
    task_id: str,
    generation_service: GenerationService = Depends(lambda: None)  # Will be injected
):
    """
    Download GLB file for completed generation
    """
    try:
        glb_path = await generation_service.get_glb_path(task_id)
        return FileResponse(
            path=glb_path,
            filename=f"model_{task_id}.glb",
            media_type="model/gltf-binary"
        )
        
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GLB file not found")
    except Exception as e:
        logger.error("GLB download failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Download failed")

@router.get("/download/{task_id}/ply")
async def download_ply(
    task_id: str,
    generation_service: GenerationService = Depends(lambda: None)  # Will be injected
):
    """
    Download PLY file for completed generation
    """
    try:
        ply_path = await generation_service.get_ply_path(task_id)
        return FileResponse(
            path=ply_path,
            filename=f"model_{task_id}.ply",
            media_type="application/octet-stream"
        )
        
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="PLY file not found")
    except Exception as e:
        logger.error("PLY download failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Download failed")

@router.get("/preview/{task_id}")
async def get_preview_video(
    task_id: str,
    generation_service: GenerationService = Depends(lambda: None)  # Will be injected
):
    """
    Get preview video for completed generation
    """
    try:
        video_path = await generation_service.get_video_path(task_id)
        return FileResponse(
            path=video_path,
            filename=f"preview_{task_id}.mp4",
            media_type="video/mp4"
        )
        
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Preview video not found")
    except Exception as e:
        logger.error("Preview video failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Preview failed")
