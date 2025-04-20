import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Tuple
from ollama import AsyncClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ollama-model-manager")

import os

client = AsyncClient(os.getenv("OLLAMA_URL", "http://localhost:11434"))

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ModelInfo(BaseModel):
    name: str
    size: int
    modified_at: str


class ModelDetail(ModelInfo):
    parameters: List[dict[str, str]]
    template: str


class CopyModelRequest(BaseModel):
    model: str  # target model name
    base: str = None  # source model name (using from_ since 'from' is a Python keyword)
    parameters: Optional[dict] = None
    template: Optional[str] = None


# API Endpoints
@app.get("/api/models", response_model=List[ModelInfo])
async def list_models():
    try:
        response = await client.list()
        return [
            ModelInfo(
                name=m["model"],
                size=m["size"],
                modified_at=m["modified_at"].isoformat() if m["modified_at"] else "",
            )
            for m in response.get("models", [])
        ]
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models/{name}", response_model=ModelDetail)
async def get_model(name: str):
    try:
        model_info = await client.show(name)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{name}' not found")

        modified_at = model_info.get("modified_at")
        if modified_at:
            modified_at = modified_at.isoformat()

        parameters = model_info.get("parameters", "")
        parameters_dict = {}
        if parameters:
            # parse paraemters into a dictionary
            # format is below, one key-value pair per line, and separated by whitespace
            # it is in align text format:
            # key1     "value1"
            # key2     "value2"
            # key3     int_value
            for line in parameters.splitlines():
                if line.strip() == "":
                    continue
                key, value = line.split(maxsplit=1)
                # remove quotes from value
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                parameters_dict[key] = value

        return ModelDetail(
            name=name,
            size=model_info.get("size", 0),
            modified_at=modified_at,
            parameters=[{"key": k, "value": v} for k, v in parameters_dict.items()],
            template=model_info.get("template", ""),
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error fetching model '{name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/models/{name:path}")
async def delete_model(name: str):
    try:
        logger.info(f"Deleting model: {name}")
        await client.delete(name)
        return {"message": f"Model {name} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting model '{name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/models/copy")
async def copy_model(request: CopyModelRequest):
    try:
        logger.info(
            f"Creating model '{request.model}' from base '{request.base}' with parameters: {request.parameters} and template: {request.template}"
        )
        # Create new model using direct parameters
        await client.create(
            model=request.model,
            from_=request.base,  # Using from_ to match our model field
            parameters=request.parameters,
            template=request.template,
        )
        logger.info(f"Model {request.model} created successfully")
        return {"message": f"Model {request.model} created successfully"}
    except Exception as e:
        logger.error(
            f"Error copying model '{request.base}' to '{request.model}': {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# Serve static files - must come after API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
