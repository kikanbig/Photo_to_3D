"""
Simple test script to verify basic application setup
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_basic_imports():
    """Test basic module imports"""
    try:
        # Set environment variables before importing
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
        os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        from app.models.generation import GenerationStatus
        print("✅ Models imported successfully")
        
        print("\n🎉 Basic setup is working!")
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
        from app.core.config import settings
        print(f"✅ Project name: {settings.PROJECT_NAME}")
        print(f"✅ Version: {settings.VERSION}")
        print(f"✅ API prefix: {settings.API_V1_STR}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Photo to 3D basic setup...\n")
    
    success = True
    success &= test_basic_imports()
    success &= test_config()
    
    if success:
        print("\n✅ All basic tests passed! The application structure is ready.")
        print("📝 Next steps:")
        print("   1. Install PyTorch and TRELLIS dependencies")
        print("   2. Set up database and Redis")
        print("   3. Configure environment variables")
        print("   4. Start development!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
