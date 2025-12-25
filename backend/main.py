from fastapi import FastAPI
from backend.utils.logger import logger
from backend.websockets.websocket_endpoint import router as ws_router
from fastapi.middleware.cors import CORSMiddleware
from backend.src.routes import upload_model_spec_route
from backend.src.routes import upload_model_data_sheet_route

from backend.src.routes import generate_model_route

app = FastAPI()

# Initialize FastAPI app
app = FastAPI(
    title="Model Builder Backend",
    description="Backend for model builder app",
    version="1.0"
)

app.include_router(
    upload_model_spec_route.router,
    prefix="/upload-model",
    tags=["Upload"],
)

app.include_router(
    upload_model_data_sheet_route.router,
    prefix="/upload-model",
    tags=["Upload"],
)


app.include_router(generate_model_route.router,
                   prefix="/generate-model",
                   tags=["Generate"])


# Mount your websocket router (no prefix so path is /ws/{client_id})
app.include_router(ws_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Backend server is starting up...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Backend server is shutting down...")

@app.get("/")
async def root():
    return {"message": "Base-Case Explorer Backend running"}

origins = [
    "http://localhost:5173",  # your frontend dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)