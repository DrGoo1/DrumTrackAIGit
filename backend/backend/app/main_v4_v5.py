"""
DrumTracKAI v4/v5 Advanced Backend Integration
Main module to integrate all ChatGPT-5 advanced features into existing FastAPI server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .deps import services
from .services.export_service import ExportService
from .routes import kits, exports, groove, irs, reference_loops, samples, sections, preview, seed
from .routes.review import router as review_router
import logging

logger = logging.getLogger(__name__)

def integrate_v4_v5_features(app: FastAPI):
    """Integrate all v4/v5 advanced features into the FastAPI app"""
    
    # Initialize services
    logger.info("Initializing v4/v5 services...")
    
    # Export service
    export_service = ExportService()
    services.register('export_service', export_service)
    
    # Mock other services for now (implement as needed)
    services.register('audio_engine', None)
    services.register('groove_analyzer', None)
    services.register('reference_loops', None)
    
    # Add v4/v5 routers
    logger.info("Registering v4/v5 API routes...")
    
    app.include_router(kits.router)
    app.include_router(exports.router)
    app.include_router(groove.router)
    app.include_router(irs.router)
    app.include_router(reference_loops.router)
    app.include_router(review_router)
    app.include_router(samples.router)
    app.include_router(sections.router)
    app.include_router(preview.router)
    app.include_router(seed.router)
    
    logger.info("v4/v5 integration complete!")
    
    return app

def create_v4_v5_app() -> FastAPI:
    """Create a standalone v4/v5 FastAPI app (alternative to integration)"""
    
    app = FastAPI(
        title="DrumTracKAI v4/v5 Advanced Backend",
        description="Professional drum generation and DAW integration",
        version="4.5.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Integrate features
    integrate_v4_v5_features(app)
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "4.5.0",
            "features": [
                "advanced_kits",
                "professional_exports", 
                "groove_analysis",
                "impulse_responses",
                "llm_drums"
            ]
        }
    
    return app

# For standalone usage
if __name__ == "__main__":
    import uvicorn
    app = create_v4_v5_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
