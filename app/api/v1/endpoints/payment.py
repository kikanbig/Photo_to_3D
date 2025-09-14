"""
Payment API endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/create-checkout")
async def create_checkout():
    """Create Stripe checkout session"""
    # TODO: Implement Stripe checkout
    pass

@router.post("/webhook")
async def stripe_webhook():
    """Stripe webhook handler"""
    # TODO: Implement Stripe webhook
    pass

@router.get("/subscription")
async def get_subscription():
    """Get user subscription info"""
    # TODO: Implement subscription info
    pass
