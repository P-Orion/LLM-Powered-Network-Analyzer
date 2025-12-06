# Project Structure Documentation

This document provides a comprehensive overview of the LLM-Powered Network Analyzer project structure, explaining the purpose and organization of each component.

## 📁 Root Directory Structure

```
LLM-Powered-Network-Analyzer/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.example                 # Environment configuration template
├── 📄 setup.py                     # Automated setup script
├── 📄 docker-compose.yml           # Docker deployment configuration
├── 📄 start.bat                    # Windows startup script
├── 📄 start.sh                     # Unix/Linux startup script
├── 📄 run.py                       # Cross-platform runner script
├── 📄 run.bat                      # Windows runner script
├── 📄 run.sh                       # Unix/Linux runner script
├── 📁 backend/                     # Python FastAPI backend
├── 📁 frontend/                    # Angular frontend application
├── 📁 docs/                        # Additional documentation
├── 📁 scripts/                     # Utility and deployment scripts
└── 📁 .github/                     # GitHub workflows and templates
```

## 🐍 Backend Structure (`backend/`)

The backend is built with Python FastAPI and handles all server-side logic, including PCAPNG parsing, anomaly detection, and LLM integration.

```
backend/
├── 📄 main.py                      # FastAPI application entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 Dockerfile                   # Docker configuration for backend
├── 📄 start.sh                     # Backend startup script
├── 📁 venv/                        # Python virtual environment (created during setup)
├── 📁 api/                         # API route handlers
│   ├── 📄 __init__.py
│   ├── 📄 upload.py                # File upload endpoints
│   ├── 📄 analysis.py              # Analysis endpoints
│   └── 📄 websocket.py             # WebSocket handlers
├── 📁 core/                        # Core business logic
│   ├── 📄 __init__.py
│   ├── 📄 config.py                # Configuration management
│   ├── 📄 security.py              # Security utilities
│   └── 📄 exceptions.py            # Custom exceptions
├── 📁 models/                      # Data models and schemas
│   ├── 📄 __init__.py
│   ├── 📄 analysis.py              # Analysis result models
│   ├── 📄 upload.py                # Upload models
│   └── 📄 websocket.py             # WebSocket message models
├── 📁 services/                    # Business logic services
│   ├── 📄 __init__.py
│   ├── 📄 analysis_service.py      # Analysis orchestration
│   ├── 📄 file_service.py          # File handling service
│   └── 📄 notification_service.py  # Progress notifications
├── 📁 parsers/                     # PCAPNG file parsing
│   ├── 📄 __init__.py
│   ├── 📄 log_parser.py            # Main PCAPNG parser using Scapy
│   ├── 📄 packet_extractor.py      # Packet data extraction
│   └── 📄 format_detector.py       # File format detection
├── 📁 analyzers/                   # Anomaly detection logic
│   ├── 📄 __init__.py
│   ├── 📄 anomaly_detector.py      # Main anomaly detection engine
│   ├── 📄 statistical_analyzer.py  # Statistical analysis
│   ├── 📄 pattern_detector.py      # Pattern recognition
│   └── 📄 baseline_calculator.py   # Baseline metrics calculation
├── 📁 llm/                         # LLM integration
│   ├── 📄 __init__.py
│   ├── 📄 gemma_client.py          # Ollama/Gemma integration
│   ├── 📄 prompt_templates.py      # LLM prompt templates
│   ├── 📄 response_parser.py       # LLM response parsing
│   └── 📄 chunking_strategy.py     # Data chunking for LLM
├── 📁 utils/                       # Utility functions
│   ├── 📄 __init__.py
│   ├── 📄 file_utils.py            # File handling utilities
│   ├── 📄 network_utils.py         # Network-related utilities
│   ├── 📄 time_utils.py            # Time and date utilities
│   └── 📄 validation.py            # Input validation
├── 📁 tests/                       # Test files and test data
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py              # Pytest configuration
│   ├── 📄 test_main.py             # Main application tests
│   ├── 📄 test_parsers.py          # Parser tests
│   ├── 📄 test_analyzers.py        # Analyzer tests
│   ├── 📄 test_llm.py              # LLM integration tests
│   ├── 📄 generate_test_pcapng.py  # Test PCAPNG file generator
│   ├── 📄 generate_quick_test.py   # Quick test data generator
│   ├── 📄 quick_test.pcapng        # Small test file
│   └── 📁 fixtures/                # Test fixtures and sample data
└── 📁 logs/                        # Application logs (created at runtime)
```

### Key Backend Components

#### `main.py`
- FastAPI application initialization
- CORS configuration
- Route registration
- WebSocket setup
- Health check endpoints

#### `parsers/log_parser.py`
- PCAPNG file parsing using Scapy
- Packet data extraction
- Protocol analysis (TCP, UDP, ICMP)
- Metadata extraction (IPs, ports, flags, timestamps)

#### `analyzers/anomaly_detector.py`
- Statistical anomaly detection
- Pattern recognition algorithms
- Baseline calculation
- Threshold-based detection for:
  - Port scanning
  - SYN floods
  - High retransmissions
  - Connection failures
  - Unusual port usage
  - Suspicious traffic patterns

#### `llm/gemma_client.py`
- Ollama API integration
- Gemma 2 12B model communication
- Prompt engineering
- Response parsing and validation

## 🌐 Frontend Structure (`frontend/`)

The frontend is built with Angular 18 and provides a modern, responsive user interface for file upload, analysis progress tracking, and results visualization.

```
frontend/
├── 📄 package.json                 # Node.js dependencies and scripts
├── 📄 package-lock.json            # Dependency lock file
├── 📄 angular.json                 # Angular CLI configuration
├── 📄 tsconfig.json                # TypeScript configuration
├── 📄 tsconfig.app.json            # App-specific TypeScript config
├── 📄 tsconfig.spec.json           # Test TypeScript configuration
├── 📄 .editorconfig                # Editor configuration
├── 📄 .gitignore                   # Frontend-specific git ignores
├── 📄 README.md                    # Frontend-specific documentation
├── 📄 Dockerfile                   # Docker configuration for frontend
├── 📄 nginx.conf                   # Nginx configuration for production
├── 📁 .angular/                    # Angular CLI cache (auto-generated)
├── 📁 .vscode/                     # VS Code configuration
├── 📁 node_modules/                # Node.js dependencies (auto-generated)
├── 📁 dist/                        # Build output (auto-generated)
├── 📁 public/                      # Static assets
│   └── 📄 favicon.ico              # Application favicon
└── 📁 src/                         # Source code
    ├── 📄 index.html               # Main HTML template
    ├── 📄 main.ts                  # Application bootstrap
    ├── 📄 styles.scss              # Global styles
    └── 📁 app/                     # Application code
        ├── 📄 app.component.html   # Root component template
        ├── 📄 app.component.scss   # Root component styles
        ├── 📄 app.component.spec.ts # Root component tests
        ├── 📄 app.component.ts     # Root component logic
        ├── 📄 app.config.ts        # Application configuration
        ├── 📄 app.routes.ts        # Routing configuration
        ├── 📁 components/          # Reusable components
        │   ├── 📁 upload/          # File upload component
        │   │   ├── 📄 upload.component.html
        │   │   ├── 📄 upload.component.scss
        │   │   ├── 📄 upload.component.spec.ts
        │   │   └── 📄 upload.component.ts
        │   ├── 📁 results/         # Analysis results component
        │   │   ├── 📄 results.component.html
        │   │   ├── 📄 results.component.scss
        │   │   ├── 📄 results.component.spec.ts
        │   │   └── 📄 results.component.ts
        │   ├── 📁 progress/        # Progress indicator component
        │   ├── 📁 anomaly-card/    # Individual anomaly display
        │   └── 📁 export/          # Export functionality component
        ├── 📁 services/            # Angular services
        │   ├── 📄 analysis.service.ts      # WebSocket communication
        │   ├── 📄 file-upload.service.ts   # File upload handling
        │   ├── 📄 export.service.ts        # Export functionality
        │   └── 📄 notification.service.ts  # User notifications
        ├── 📁 models/              # TypeScript interfaces
        │   ├── 📄 analysis.model.ts        # Analysis result interfaces
        │   ├── 📄 upload.model.ts          # Upload-related interfaces
        │   ├── 📄 websocket.model.ts       # WebSocket message interfaces
        │   └── 📄 anomaly.model.ts         # Anomaly data interfaces
        ├── 📁 guards/              # Route guards
        │   └── 📄 analysis.guard.ts        # Analysis route protection
        ├── 📁 interceptors/        # HTTP interceptors
        │   ├── 📄 error.interceptor.ts     # Error handling
        │   └── 📄 loading.interceptor.ts   # Loading state management
        ├── 📁 pipes/               # Custom pipes
        │   ├── 📄 file-size.pipe.ts        # File size formatting
        │   └── 📄 duration.pipe.ts         # Duration formatting
        └── 📁 shared/              # Shared utilities
            ├── 📁 constants/       # Application constants
            ├── 📁 utils/           # Utility functions
            └── 📁 validators/      # Custom form validators
```

### Key Frontend Components

#### `components/upload/`
- Drag-and-drop file upload interface
- File validation (format, size)
- Upload progress tracking
- Error handling and user feedback

#### `components/results/`
- Analysis results display
- Severity-based color coding
- Expandable anomaly details
- Export functionality integration

#### `services/analysis.service.ts`
- WebSocket connection management
- Real-time progress updates
- Analysis state management
- Error handling and reconnection logic

## 📚 Documentation Structure (`docs/`)

```
docs/
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
├── 📄 TROUBLESHOOTING.md           # Common issues and solutions
├── 📄 DEPLOYMENT.md                # Deployment guides and configurations
├── 📄 API_REFERENCE.md             # API documentation
├── 📄 DEVELOPMENT.md               # Development setup and guidelines
├── 📄 SECURITY.md                  # Security considerations and best practices
├── 📄 PERFORMANCE.md               # Performance optimization guide
├── 📁 images/                      # Documentation images and screenshots
├── 📁 examples/                    # Usage examples and sample files
└── 📁 architecture/                # Architecture diagrams and designs
```

## 🔧 Scripts Structure (`scripts/`)

```
scripts/
├── 📄 setup.sh                     # Unix/Linux setup script
├── 📄 setup.bat                    # Windows setup script
├── 📄 build.sh                     # Build script for production
├── 📄 deploy.sh                    # Deployment automation script
├── 📄 test.sh                      # Test runner script
├── 📄 backup.sh                    # Backup script
└── 📁 docker/                      # Docker-related scripts
    ├── 📄 build-images.sh          # Docker image building
    └── 📄 push-images.sh           # Docker image publishing
```

## 🐙 GitHub Structure (`.github/`)

```
.github/
├── 📁 workflows/                   # GitHub Actions workflows
│   ├── 📄 ci.yml                  # Continuous Integration
│   ├── 📄 cd.yml                  # Continuous Deployment
│   ├── 📄 security.yml            # Security scanning
│   └── 📄 docs.yml                # Documentation updates
├── 📁 ISSUE_TEMPLATE/              # Issue templates
│   ├── 📄 bug_report.md           # Bug report template
│   ├── 📄 feature_request.md      # Feature request template
│   └── 📄 question.md             # Question template
├── 📁 PULL_REQUEST_TEMPLATE/       # PR templates
│   └── 📄 pull_request_template.md
└── 📄 SECURITY.md                  # Security policy
```

## 🏗️ Architecture Overview

### Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Ollama/LLM    │
│   (Angular)     │    │   (FastAPI)     │    │   (Gemma 2 12B) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Upload PCAPNG      │                       │
         ├──────────────────────►│                       │
         │                       │ 2. Parse & Extract    │
         │                       ├─────────────────────► │
         │                       │                       │
         │ 3. WebSocket Progress │ 4. Statistical        │
         │◄──────────────────────┤    Analysis          │
         │                       │                       │
         │                       │ 5. LLM Analysis      │
         │                       ├──────────────────────►│
         │                       │                       │
         │ 6. Final Results      │ 7. Response Parsing   │
         │◄──────────────────────┤◄──────────────────────┤
         │                       │                       │
```

### Component Interactions

1. **File Upload**: User uploads PCAPNG file via Angular frontend
2. **Parsing**: Backend uses Scapy to parse network packets
3. **Statistical Analysis**: Anomaly detector identifies suspicious patterns
4. **LLM Analysis**: Suspicious data sent to Gemma 2 12B for detailed analysis
5. **Results**: Plain-English explanations returned to frontend
6. **Display**: Results shown with severity coding and recommendations

### Technology Stack

#### Backend Technologies
- **Python 3.10+**: Core language
- **FastAPI**: Web framework
- **Scapy**: Packet parsing
- **Ollama**: LLM integration
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

#### Frontend Technologies
- **Angular 18**: Frontend framework
- **TypeScript**: Type-safe JavaScript
- **Angular Material**: UI components
- **RxJS**: Reactive programming
- **SCSS**: Styling
- **WebSocket API**: Real-time updates

#### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving
- **Kubernetes**: Container orchestration (optional)

## 🔒 Security Architecture

### Data Flow Security
- **Local Processing**: All data stays on user's machine
- **No External APIs**: Except local Ollama instance
- **Input Validation**: All uploads validated and sanitized
- **Memory Management**: Sensitive data cleared after processing

### Network Security
- **CORS Configuration**: Restricted to localhost origins
- **WebSocket Security**: Connection validation and rate limiting
- **File Upload Limits**: Size and format restrictions
- **Error Handling**: No sensitive information in error messages

## 📊 Performance Architecture

### Optimization Strategies
- **Statistical Pre-filtering**: Reduces LLM processing by 70-80%
- **Async Processing**: Non-blocking I/O operations
- **Streaming**: Large files processed in chunks
- **Caching**: Frequently accessed data cached in memory
- **Connection Pooling**: Efficient resource utilization

### Scalability Considerations
- **Horizontal Scaling**: Multiple backend instances
- **Load Balancing**: Distribute requests across instances
- **Resource Isolation**: Separate LLM processing
- **Queue Management**: Handle concurrent analysis requests

## 🧪 Testing Architecture

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

### Test Data
- **Generated Test Files**: Synthetic PCAPNG files with known anomalies
- **Real-world Samples**: Anonymized production data
- **Edge Cases**: Malformed files and boundary conditions
- **Performance Datasets**: Large files for performance testing

---

This project structure is designed for:
- **Maintainability**: Clear separation of concerns
- **Scalability**: Modular architecture supports growth
- **Security**: Privacy-first design with local processing
- **Developer Experience**: Well-organized code with comprehensive documentation
- **Production Readiness**: Deployment configurations and monitoring support