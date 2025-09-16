"""
RunPod Handler for TRELLIS 3D Generation
"""
import os
import json
import base64
import tempfile
import traceback
from io import BytesIO
from typing import Dict, Any
import runpod
import requests
from PIL import Image
try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    print("⚠️ boto3 не установлен, S3 загрузка недоступна")
    S3_AVAILABLE = False

from trellis_worker import TrellisWorker

# Initialize TRELLIS worker
trellis_worker = TrellisWorker()

# AWS S3 client (optional)
s3_client = None
if S3_AVAILABLE:
    try:
        s3_client = boto3.client('s3')
        print("✅ S3 client initialized")
    except Exception as e:
        print(f"⚠️ S3 client not available: {e}")
else:
    print("⚠️ S3 не доступен - boto3 не установлен")

def upload_to_s3(file_path: str, bucket: str, key: str) -> str:
    """Upload file to S3 and return public URL"""
    if not s3_client:
        return None
    
    try:
        s3_client.upload_file(file_path, bucket, key)
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"S3 upload failed: {e}")
        return None

def notify_webhook(webhook_url: str, task_id: str, status: str, result: Dict = None):
    """Notify Railway API about task completion"""
    if not webhook_url:
        return
    
    try:
        payload = {
            "task_id": task_id,
            "status": status,
            "result": result
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=30
        )
        print(f"✅ Webhook notification sent: {response.status_code}")
        
    except Exception as e:
        print(f"⚠️ Webhook notification failed: {e}")

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    RunPod job handler for TRELLIS 3D generation
    
    Expected input:
    {
        "input": {
            "image_url": "https://...",
            "task_id": "uuid",
            "webhook_url": "https://railway.../webhook",
            "parameters": {
                "seed": 42,
                "guidance_strength": 7.5,
                "sampling_steps": 12
            }
        }
    }
    """
    try:
        job_input = job.get("input", {})
        
        # Extract parameters
        image_url = job_input.get("image_url")
        image_data = job_input.get("image_data")
        image_format = job_input.get("image_format", "png")
        task_id = job_input.get("task_id", "unknown")
        webhook_url = job_input.get("webhook_url")
        parameters = job_input.get("parameters", {})
        
        # Validate input - нужен либо image_url, либо image_data
        if not image_url and not image_data:
            return {
                "status": "failed",
                "error": "Either image_url or image_data is required",
                "task_id": task_id
            }
        
        print(f"🚀 Starting 3D generation for task: {task_id}")
        if image_url:
            print(f"📷 Image URL: {image_url}")
        else:
            print(f"📷 Image data: base64 ({len(image_data)} chars)")
        
        # Load and save image from URL or base64 data
        if image_url:
            print("📥 Downloading input image...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_content = response.content
        else:
            print("📥 Decoding base64 image...")
            image_content = base64.b64decode(image_data)
        
        # Save to temporary file
        file_extension = f'.{image_format}' if image_data else '.jpg'
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
            tmp_file.write(image_content)
            input_image_path = tmp_file.name
        
        print(f"✅ Image saved: {input_image_path}")
        
        # Generate 3D model using TRELLIS
        print("🧠 Generating 3D model with TRELLIS...")
        result = trellis_worker.generate_3d(
            image_path=input_image_path,
            **parameters
        )
        
        print(f"✅ 3D generation completed!")
        print(f"📊 Result: {list(result.keys())}")
        
        # Upload results to S3 (if configured)
        s3_bucket = os.environ.get("S3_BUCKET")
        if s3_bucket and s3_client:
            print("☁️ Uploading to S3...")
            
            for file_type, file_path in result.items():
                if file_path and os.path.exists(file_path):
                    s3_key = f"generations/{task_id}/{file_type}"
                    s3_url = upload_to_s3(file_path, s3_bucket, s3_key)
                    if s3_url:
                        result[f"{file_type}_url"] = s3_url
        
        # Notify Railway webhook
        if webhook_url:
            notify_webhook(webhook_url, task_id, "completed", result)
        
        # Convert files to base64 for download
        result_with_data = {}
        for key, file_path in result.items():
            if isinstance(file_path, str) and os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    
                    result_with_data[key] = file_path
                    result_with_data[f"{key}_base64"] = base64.b64encode(file_data).decode('utf-8')
                    result_with_data[f"{key}_size"] = len(file_data)
                    
                    print(f"✅ Encoded {key}: {len(file_data)} bytes")
                    
                except Exception as e:
                    print(f"⚠️ Failed to encode {key}: {e}")
                    result_with_data[key] = file_path
        
        # Cleanup temporary files
        try:
            os.unlink(input_image_path)
            for file_path in result.values():
                if isinstance(file_path, str) and os.path.exists(file_path):
                    os.unlink(file_path)
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result_with_data
        }
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        print(f"❌ Error in handler: {error_msg}")
        print(f"📍 Traceback: {error_trace}")
        
        # Notify webhook about error
        webhook_url = job.get("input", {}).get("webhook_url")
        task_id = job.get("input", {}).get("task_id", "unknown")
        
        if webhook_url:
            notify_webhook(webhook_url, task_id, "failed", {
                "error": error_msg,
                "traceback": error_trace
            })
        
        return {
            "task_id": task_id,
            "status": "failed",
            "error": error_msg
        }

if __name__ == "__main__":
    print("🚀 Starting TRELLIS RunPod Handler...")
    print(f"🔧 CUDA available: {trellis_worker.device}")
    
    # Start RunPod serverless handler
    runpod.serverless.start({"handler": handler})
