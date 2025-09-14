# Photo to 3D

AI-powered web service for generating 3D models from photographs using Microsoft TRELLIS.

## Features

- 🖼️ **Image to 3D**: Convert photos to high-quality 3D models
- 🎯 **Multiple Formats**: Export as GLB, PLY, and preview videos
- 💳 **Monetization**: Pay-per-use and subscription models
- 🤖 **Telegram Bot**: Generate 3D models via Telegram
- 🌐 **Web Interface**: Modern React-based frontend
- ⚡ **Fast API**: High-performance FastAPI backend

## Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **3D Generation**: Microsoft TRELLIS
- **Database**: PostgreSQL
- **Cache**: Redis
- **Storage**: S3-compatible storage
- **Deployment**: Railway
- **Frontend**: React/Next.js
- **Payments**: Stripe

## Quick Start

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (16GB+ VRAM recommended)
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/photo-to-3d.git
   cd photo-to-3d
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python -m app.main
   ```

## API Usage

### Generate 3D Model

```bash
curl -X POST "http://localhost:8000/api/v1/generation/generate" \
  -F "image=@your_image.jpg" \
  -F "seed=42" \
  -F "ss_guidance_strength=7.5" \
  -F "ss_sampling_steps=12"
```

### Check Generation Status

```bash
curl "http://localhost:8000/api/v1/generation/status/{task_id}"
```

### Download GLB File

```bash
curl "http://localhost:8000/api/v1/generation/download/{task_id}/glb" -o model.glb
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `TRELLIS_MODEL_PATH` | TRELLIS model path | `microsoft/TRELLIS-image-large` |
| `STRIPE_SECRET_KEY` | Stripe secret key | Optional |
| `S3_BUCKET` | S3 bucket name | `photo-to-3d-models` |

### TRELLIS Models

The service supports different TRELLIS models:

- `microsoft/TRELLIS-image-large` (1.2B parameters) - Recommended
- `microsoft/TRELLIS-text-base` (342M parameters)
- `microsoft/TRELLIS-text-large` (1.1B parameters)

## Development

### Project Structure

```
Photo_to_3D/
├── app/                    # Main application
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Data models
│   └── services/          # Business logic
├── frontend/              # React frontend
├── telegram_bot/          # Telegram bot
├── tests/                 # Test files
└── configs/               # Configuration files
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
isort app/
```

## Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Docker

```bash
docker build -t photo-to-3d .
docker run -p 8000:8000 photo-to-3d
```

## Monetization

### Pricing Models

- **Pay-per-use**: $0.50-2.00 per generation
- **Subscription**: $9.99-49.99/month
- **Credits**: Bulk credit packages

### Payment Integration

- Stripe for web payments
- Telegram Payments for bot
- Webhook handling for subscription updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Microsoft TRELLIS](https://github.com/Microsoft/TRELLIS) for 3D generation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Railway](https://railway.app/) for deployment platform

## Support

For support and questions:

- 📧 Email: support@photo-to-3d.com
- 💬 Discord: [Join our community](https://discord.gg/photo-to-3d)
- 📖 Documentation: [docs.photo-to-3d.com](https://docs.photo-to-3d.com)
