import logging
from typing import Any
from typing import Dict
from typing import List
from typing import List as ListType
from typing import Optional
from typing import Type
from typing import Union

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ollama import AsyncClient
from pydantic import BaseModel

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


# Parameter type definitions
class ParameterType:
    def __init__(self, type_: Union[Type, ListType[Type]], allow_list: bool = False):
        self.type = type_
        self.allow_list = allow_list

    def cast(self, value: Any) -> Any:
        if self.allow_list and isinstance(value, list):
            return [self.type(item) for item in value]
        return self.type(value)

    @property
    def type_name(self) -> str:
        base_type = self.type.__name__
        return f"{base_type} or List[{base_type}]" if self.allow_list else base_type


# Parameter type mapping
PARAMETER_TYPES = {
    "mirostat": ParameterType(int),
    "mirostat_eta": ParameterType(float),
    "mirostat_tau": ParameterType(float),
    "num_ctx": ParameterType(int),
    "repeat_last_n": ParameterType(int),
    "repeat_penalty": ParameterType(float),
    "temperature": ParameterType(float),
    "seed": ParameterType(int),
    "stop": ParameterType(
        str, allow_list=True
    ),  # Supports both string and list of strings
    "num_predict": ParameterType(int),
    "top_k": ParameterType(int),
    "top_p": ParameterType(float),
    "min_p": ParameterType(float),
}


def validate_and_cast_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and cast parameters to their proper types."""
    if not parameters:
        return parameters

    result = {}
    for key, value in parameters.items():
        if key not in PARAMETER_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameter: {key}. Parameter must be one of: {', '.join(PARAMETER_TYPES.keys())}",
            )

        try:
            # Cast the value using the parameter type handler
            result[key] = PARAMETER_TYPES[key].cast(value)
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for {key}: {value}. Expected type: {PARAMETER_TYPES[key].type_name}",
            )

    return result


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


@app.get("/api/models/{name:path}", response_model=ModelDetail)
async def get_model(name: str):
    try:
        model_info = await client.show(name)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{name}' not found")

        modified_at = model_info.get("modified_at")
        if modified_at:
            modified_at = modified_at.isoformat()

        parameters = model_info.get("parameters", "")
        parameters_list = []
        if parameters:
            # parse paraemters into a dictionary
            # format is below, one key-value pair per line, and separated by whitespace
            # it is in align text format:
            # key1     "value1"
            # key2     "value1"
            # key2     "value2"
            # key2     "value3"
            # key3     int_value
            for line in parameters.splitlines():
                if line.strip() == "":
                    continue
                key, value = line.split(maxsplit=1)
                # remove quotes from value
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                parameters_list.append({"key": key, "value": value})

        return ModelDetail(
            name=name,
            size=model_info.get("size", 0),
            modified_at=modified_at,
            parameters=parameters_list,
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
        # Validate and cast parameters
        validated_parameters = validate_and_cast_parameters(request.parameters)

        logger.info(
            f"Creating model '{request.model}' from base '{request.base}' with parameters: {validated_parameters} and template: {request.template}"
        )
        await client.create(
            model=request.model,
            from_=request.base,  # Using from_ to match our model field
            parameters=validated_parameters,
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
