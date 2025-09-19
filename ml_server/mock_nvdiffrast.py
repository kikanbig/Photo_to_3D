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
    
    # Mock xatlas module for TRELLIS compatibility
    mock_xatlas = type('MockXatlas', (), {
        'parametrize': lambda *args, **kwargs: None,
        'pack': lambda *args, **kwargs: None
    })()
    sys.modules['xatlas'] = mock_xatlas
    
    # Mock pyvista module for TRELLIS compatibility
    mock_pyvista = type('MockPyvista', (), {
        'PolyData': lambda *args, **kwargs: None,
        'save': lambda *args, **kwargs: None,
        'read': lambda *args, **kwargs: None
    })()
    sys.modules['pyvista'] = mock_pyvista
    
    print("✅ Mock nvdiffrast, xatlas and pyvista modules created successfully!")
    return mock_nvdiffrast

if __name__ == "__main__":
    create_mock_nvdiffrast()
