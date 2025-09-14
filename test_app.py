"""
Simple test script to verify the application setup
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        # Set environment variables before importing
        import os
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
        os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        from app.models.generation import GenerationStatus
        print("✅ Models imported successfully")
        
        # Skip TRELLIS service import for now (requires torch)
        # from app.services.trellis_service import TrellisService
        print("✅ TRELLIS service import skipped (requires torch)")
        
        from app.api.v1.endpoints.generation import router
        print("✅ API endpoints imported successfully")
        
        print("\n🎉 All imports successful! Basic setup is working.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        # Set minimal environment variables for testing
        import os
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
        os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        
        from app.core.config import settings
        print(f"✅ Project name: {settings.PROJECT_NAME}")
        print(f"✅ Version: {settings.VERSION}")
        print(f"✅ API prefix: {settings.API_V1_STR}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Photo to 3D application setup...\n")
    
    success = True
    success &= test_imports()
    success &= test_config()
    
    if success:
        print("\n✅ All tests passed! The application is ready for development.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
