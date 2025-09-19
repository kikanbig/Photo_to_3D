"""
Mock nvdiffrast module for TRELLIS compatibility
"""
import sys

def create_mock_nvdiffrast():
    """Create mock nvdiffrast module"""
    mock_nvdiffrast = type('MockNvdiffrast', (), {
        'torch': type('MockNvdiffrastTorch', (), {
            'rasterize': lambda *args, **kwargs: None,
            'interpolate': lambda *args, **kwargs: None,
            'texture': lambda *args, **kwargs: None,
            'antialias': lambda *args, **kwargs: None
        })()
    })()
    
    # Register in sys.modules
    sys.modules['nvdiffrast'] = mock_nvdiffrast
    sys.modules['nvdiffrast.torch'] = mock_nvdiffrast.torch
    
    print("✅ Mock nvdiffrast module created successfully!")
    return mock_nvdiffrast

if __name__ == "__main__":
    create_mock_nvdiffrast()
