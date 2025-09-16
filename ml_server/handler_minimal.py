"""
Минимальный RunPod Handler для отладки
"""
import runpod
import json

def handler(job):
    """
    Минимальный handler который всегда работает
    """
    print("✅ Handler started successfully")
    
    try:
        job_input = job.get("input", {})
        task_id = job_input.get("task_id", "test")
        
        print(f"📋 Processing task: {task_id}")
        
        # Просто возвращаем успешный результат
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "Minimal handler working",
            "handler_version": "minimal_v1.0"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

# Start the RunPod handler
if __name__ == "__main__":
    print("🚀 Starting minimal RunPod handler...")
    runpod.serverless.start({"handler": handler})
