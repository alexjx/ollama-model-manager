# Ollama Model Manager

A web-based management tool for Ollama models with an intuitive user interface built with Vue 3 and FastAPI.

## Features

- **Model Management**
  - View comprehensive list of available models
  - Display detailed model information including parameters and templates
  - Sort and filter models using an interactive table interface
  - Real-time model status updates

- **Model Operations**
  - Delete models with confirmation dialog
  - Copy models with customizable options
  - Modify parameters and templates when copying models
  - Batch operations support

- **User Interface**
  - Modern Material Design theme using PrimeVue
  - Responsive layout for all device sizes
  - Interactive data tables with sorting and filtering
  - Toast notifications for action feedback
  - Loading indicators for async operations

## Architecture

### Backend (FastAPI)

- **API Endpoints**
  - `GET /api/models` - List all available models
  - `GET /api/models/{name}` - Get detailed model information
  - `DELETE /api/models/{name}` - Remove a model
  - `POST /api/models/copy` - Copy model with custom parameters

- **Features**
  - Asynchronous request handling
  - Integrated Ollama SDK
  - Comprehensive logging system
  - Error handling and validation

### Frontend (Vue 3 + PrimeVue)

- **Core Components**
  - `ModelsTable`: Interactive model listing with sort/filter capabilities
  - `ModelDetailCard`: Detailed model information display
  - `CopyModelDialog`: Configuration modal for model copying
  - `DeleteConfirmDialog`: Confirmation dialog for model deletion

- **Technologies**
  - Vue 3 Composition API
  - PrimeVue UI Components
  - PrimeFlex for responsive layouts
  - Material Design theme

## Getting Started

### Prerequisites

- Python 3.7+
- Node.js 14+
- Ollama installed and running

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python src/main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The web interface will be available at `http://localhost:5173`

## API Documentation

Once the backend is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is open source and available under the MIT License.
