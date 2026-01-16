# PaperChecker - Citation Compliance Checker

A sophisticated academic paper citation compliance checking system that automatically analyzes citations and references in academic documents, identifying mismatches, missing citations, and format inconsistencies to improve paper quality and academic standards.

**Developed by**: Agent4S Project Team, TaShan Interdisciplinary Innovation Association, University of Chinese Academy of Sciences  
**Website**: [tashan.ac.cn](https://tashan.ac.cn)

## 🚀 Features

### Document Processing
- **Supported Formats**: Word documents (.docx, .doc) and PDF files
- **File Size Limit**: Up to 10MB per document
- **Smart Parsing**: Automatic identification of document structure, extracting main content and reference sections

### Citation Recognition

The system recognizes citations in academic papers and matches them with reference lists. Here's what formats are currently supported:

| Citation Format | Support Level | Examples | Notes |
|----------------|---------------|----------|-------|
| **Author-Year (Chinese)** | ✅ Full Support | 张三（2024）<br>李四 等（2020） | Complete citation-reference matching and validation |
| **Author-Year (English)** | ✅ Full Support | Smith (2020)<br>Smith & Jones (2019)<br>Smith et al. (2018) | Complete citation-reference matching and validation |
| **GB/T 7714-2015 著者-出版年制** | ✅ Full Support | Same as author-year formats above | This is the primary format this tool is designed for |
| **Numeric Sequential** | ⚠️ Partial Support | [1], [2], [15]<br>[1-3] (range) | Can extract and identify, but does not perform citation-reference matching validation |
| **GB/T 7714-2015 顺序编码制** | ⚠️ Partial Support | Same as numeric sequential | Can extract and identify only |
| **IEEE (numeric)** | ⚠️ Partial Support | [1], [2] (bracket style only) | Can extract bracket-style numbers; superscript numbers (e.g., text¹) are not supported |
| **APA** | ⚠️ Partial Support | Basic author-year only | Only supports basic author-year format; page numbers and advanced features not supported |
| **MLA** | ❌ Not Supported | - | Planned but not implemented |
| **Chicago** | ❌ Not Supported | - | Planned but not implemented |

**Best Results**: This tool works best with papers using **author-year citation format** (GB/T 7714-2015 著者-出版年制 or similar styles). For papers using numeric citation systems, the tool can identify citations but cannot perform comprehensive matching analysis.

### Intelligent Matching (for Author-Year Format)
- **Bidirectional Mapping**: Precise matching between in-text citations and reference list
- **Context Analysis**: Understanding of citation usage in document context
- **Tolerance for Variations**: Correct matching even with slight formatting differences
- **Note**: Full matching analysis is available for author-year format citations only

### Automated Verification & Correction
- **Year Validation**: Detection of citation year inconsistencies with reference years
- **Format Standardization**: Consistent citation formatting across documents
- **Quality Assurance**: Identification of uncited references and unreferenced citations

### Comprehensive Reporting
- **Match Statistics**: Citation count statistics and match success rates
- **Correction Suggestions**: Year inconsistency corrections and format standardization recommendations
- **Formatted Citations**: Standardized citations according to academic standards

### AI-Powered Optimization
- **Intelligent Formatting**: AI model-optimized citation formats
- **Error Tolerance**: Handling of non-standard formats with automatic correction
- **Context Understanding**: Analysis of citation correctness in context

## 🛠️ Technical Stack

- **Framework**: FastAPI (Python)
- **Document Processing**: python-docx, PyMuPDF
- **AI Services**: DashScope, LangChain, OpenAI integration
- **Web Interface**: HTML/CSS/JavaScript frontend
- **API Architecture**: RESTful API design with CORS support

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (required for AI-enhanced features; basic citation matching works offline)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TashanGKD/TaShan-PaperChecker.git
   cd TaShan-PaperChecker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional but recommended for AI features):
   Create a `.env` file in the project root with your API keys:
   ```env
   DASHSCOPE_API_KEY=your_dashscope_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```
   
   **Note**: The system can work without AI API keys, but some advanced features like AI-powered citation extraction and relevance checking will be limited. Basic citation matching for author-year format will still function.

5. Configure the application (optional):
   You can modify the default settings in `config/config.py` or create a `.env` file with the following options:
   ```env
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8002
   SERVER_RELOAD=true
   TEMP_DIR=temp_uploads
   MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
   API_PREFIX=/api
   ```

6. The application will automatically create required directories on startup.
   These directories (temp_uploads, reports_md, logs, pdf_cache) are included in .gitignore and will not be tracked by Git.

## ⚙️ Configuration

The application can be configured through the `config/config.py` file:

- `server_host`: Host address for the API server (default: "0.0.0.0")
- `server_port`: Port number for the API server (default: 8002)
- `max_upload_size`: Maximum file upload size in bytes (default: 10MB)
- `temp_dir`: Directory for temporary file storage (default: "temp_uploads")

## 🏃‍♂️ Running the Application

### Development Mode
```bash
python run_server.py
```

The API server will start on `http://localhost:8002` by default.

### Production Mode
For production deployment, use uvicorn with multiple workers:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

## 🌐 API Endpoints

### Health Check
- `GET /` - Root endpoint showing API information
- `GET /api/health` - Check service health status

### File Operations
- `POST /api/upload-only` - Upload a document file without processing
- `GET /api/list-all-files` - List all uploaded files in the temp_uploads directory
- `DELETE /api/file?file_path={path}` - Delete a specific file by path

### Citation Analysis
- `POST /api/full-report` - Generate complete citation compliance report by uploading a file
- `POST /api/full-report-from-path` - Generate report using file path with optional author format parameter
- `POST /api/extract-citations` - Extract citations from document (form data input)
- `POST /api/extract-citations-json` - Extract citations from document (JSON input)
- `POST /api/relevance-check` - Perform citation relevance check with target content

### Frontend Access
- `/frontend` - Access the web-based user interface for uploading documents and viewing analysis results

## 💡 Usage Examples

### Using cURL

#### Upload and analyze a document
```bash
curl -X POST "http://localhost:8002/api/full-report" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.docx"
```

#### Upload a file without processing
```bash
curl -X POST "http://localhost:8002/api/upload-only" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.docx"
```

#### List uploaded files
```bash
curl -X GET "http://localhost:8002/api/list-all-files"
```

#### Extract citations from a file
```bash
curl -X POST "http://localhost:8002/api/extract-citations" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=temp_uploads/document.docx"
```

#### Perform relevance check
```bash
curl -X POST "http://localhost:8002/api/relevance-check" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=temp_uploads/document.docx" \
  -d "target_content=Machine learning techniques in NLP" \
  -d "task_type=文章整体" \
  -d "use_full_content=false"
```

#### Generate report from file path
```bash
curl -X POST "http://localhost:8002/api/full-report-from-path" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=temp_uploads/document.docx" \
  -d "author_format=full"
```

### Python Client Example
```python
import requests

# Upload and analyze a document
with open('document.docx', 'rb') as f:
    response = requests.post(
        'http://localhost:8002/api/full-report',
        files={'file': f}
    )

result = response.json()
print(result)

# Upload a file without processing
with open('document.docx', 'rb') as f:
    response = requests.post(
        'http://localhost:8002/api/upload-only',
        files={'file': f}
    )

upload_result = response.json()
print(upload_result)

# List all uploaded files
response = requests.get('http://localhost:8002/api/list-all-files')
files_list = response.json()
print(files_list)

# Extract citations from a file
response = requests.post(
    'http://localhost:8002/api/extract-citations',
    data={'file_path': 'temp_uploads/document.docx'}
)
citations = response.json()
print(citations)
```

### JavaScript/Fetch Example
```javascript
// Upload and analyze a document
const formData = new FormData();
const fileInput = document.querySelector('#file-input');
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8002/api/full-report', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// List all uploaded files
fetch('http://localhost:8002/api/list-all-files')
.then(response => response.json())
.then(data => console.log(data.files));
```

## 🏗️ Technical Architecture

PaperChecker follows a modular architecture with clear separation of concerns:

### Core Components
- **Extractor Layer**: Handles document parsing and content extraction for various formats (Word, PDF)
- **Checker Layer**: Performs citation analysis, validation, and compliance checking
- **Processor Layer**: Orchestrates the end-to-end analysis workflow
- **AI Services**: Integrates with LLM providers for intelligent document analysis
- **Report Generator**: Creates comprehensive compliance reports

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Client   │───▶│  FastAPI Server  │───▶│  AI Services    │
│                 │    │                  │    │ (DashScope,     │
│ (Browser/App)   │    │ • API Routes     │    │  OpenAI, etc.)  │
└─────────────────┘    │ • Request/Resp   │    └─────────────────┘
                       │ • Validation     │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │  Core Modules    │
                       │ • Extractor      │
                       │ • Checker        │
                       │ • Processor      │
                       │ • Reports        │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │  Utilities       │
                       │ • File Handler   │
                       │ • Format Utils   │
                       │ • Cache Manager  │
                       └──────────────────┘
```

### Project Structure

```
PaperChecker/
├── api/                    # API route definitions
├── app/                    # Main application entry point
│   └── main.py             # FastAPI application
├── config/                 # Configuration files
│   └── config.py           # Settings and configuration
├── core/                   # Core processing modules
│   ├── ai/                 # AI-related utilities
│   ├── ai_services/        # AI service integrations
│   ├── checker/            # Citation checking logic
│   ├── extractor/          # Document extraction logic
│   ├── polish/             # Text polishing and enhancement
│   ├── processors/         # Document processing logic
│   └── reports/            # Report generation logic
├── front/                  # Frontend web interface
├── models/                 # Data models and schemas
├── temp_uploads/           # Temporary file storage
├── pdf_cache/              # Cached PDF processing results
├── reports_md/             # Generated report files
├── pids/                   # Process ID files
├── logs/                   # Application logs
├── tests/                  # Test suite
├── utils/                  # Utility functions
├── run_server.py           # Server startup script
├── requirements.txt        # Python dependencies
├── AI_CODING_GUIDELINES.md # Development guidelines
├── DEPLOYMENT_README.md    # Deployment instructions
├── design.md               # System design documentation
└── README.md              # This file
```

### Key Technologies Used
- **FastAPI**: Modern, fast web framework with async support
- **Pydantic**: Data validation and settings management
- **python-docx**: Word document processing
- **PyMuPDF**: PDF processing capabilities
- **LangChain**: Framework for developing applications with LLMs
- **Tenacity**: Retry mechanism for robust operations
- **Semantic Scholar API**: Academic paper metadata retrieval
- **Crossref API**: Reference validation and enrichment

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 🤝 Contributing

We welcome contributions to PaperChecker! Here's how you can contribute:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests to ensure everything works (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines
Please read our [AI Coding Guidelines](AI_CODING_GUIDELINES.md) for best practices on development:

- Each new feature must include corresponding tests
- Follow the "small steps, quick iterations" development approach
- Reduce coupling between modules and increase reusability
- Prioritize using existing code over creating duplicate functionality
- Maintain clear documentation for all public interfaces

### Code Standards
- Follow PEP 8 style guide for Python code
- Write clear, descriptive commit messages
- Include docstrings for all public functions and classes
- Add type hints where appropriate

### Reporting Issues
When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🐛 Issues and Bug Reports

If you encounter any issues or bugs, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment details (OS, Python version, etc.)

## 🆘 Support

For support, you can:
- Open an issue on GitHub
- Check the documentation in this README
- Look at the test examples in the `tests/examples/` directory

## 🙏 Acknowledgments

### Development Team
This project is developed and maintained by the **Agent4S Project Team** of the **TaShan Interdisciplinary Innovation Association (他山学科交叉创新协会)** at the **University of Chinese Academy of Sciences (中国科学院大学)**.

- **Association**: TaShan Interdisciplinary Innovation Association
- **Website**: [tashan.ac.cn](https://tashan.ac.cn)
- **Project**: Agent4S - AI-powered Academic Tools
- **Research Paper**: [Agent4S: The Transformation of Research Paradigms from the Perspective of Large Language Models](https://arxiv.org/abs/2506.23692) (arXiv:2506.23692)

### Technical Acknowledgments
- Built with FastAPI for high-performance API development
- Uses advanced AI models for intelligent document analysis
- Inspired by the need for better academic writing tools

## 🤝 Support the Project

If this project helps you or your organization, consider supporting it:

- Star this repository
- Share it with others who might benefit
- Contribute code, documentation, or ideas
- Sponsor the maintainers through GitHub Sponsors or other channels

## 📞 Contact

For questions, suggestions, or support, feel free to:
- Open an issue on GitHub
- Email us at: **tashanxkjc@163.com**
- Visit our website: [tashan.ac.cn](https://tashan.ac.cn)

### Follow Us

**WeChat Official Account (微信公众号)**

<img src="image.png" alt="WeChat QR Code" width="200"/>

Scan the QR code above to follow our WeChat Official Account for updates and news.

**Douyin (抖音)**

Search "**他山学科交叉创新协会**" on Douyin to find our Agent4S course videos and tutorials.

**Learn More About Agent4S**

Read our comprehensive survey paper: [Agent4S: The Transformation of Research Paradigms from the Perspective of Large Language Models](https://arxiv.org/abs/2506.23692)