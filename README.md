# RAG Multimodal Financial Document Processor

A comprehensive solution for processing financial documents using RAG (Retrieval-Augmented Generation) and multimodal AI techniques.

## Features

- Extract text from financial documents using OCR
- Detect and extract tables
- Extract ISINs and related information
- Analyze financial data
- Validate and enhance data using AI
- Visualize results
- API for integration with other systems
- Web interface for easy use

## Requirements

### System Dependencies

- Node.js 16+
- Python 3.8+
- Poppler (for PDF processing)
- Tesseract OCR (with English and Hebrew language packs)
- GraphicsMagick or ImageMagick

### API Keys

- OpenAI API key or Google API key for AI validation

## Installation

### Using Docker

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-multimodal-processor.git
   cd rag-multimodal-processor
   ```

2. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

3. Build and run the Docker container:
   ```
   docker build -t rag-multimodal-processor .
   docker run -p 3000:3000 --env-file .env rag-multimodal-processor
   ```

4. Access the web interface at http://localhost:3000

### Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-multimodal-processor.git
   cd rag-multimodal-processor
   ```

2. Install backend dependencies:
   ```
   cd backend
   npm install
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd ../frontend
   npm install
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

5. Build the frontend:
   ```
   npm run build
   ```

6. Start the server:
   ```
   cd ../backend
   npm start
   ```

7. Access the web interface at http://localhost:3000

## Usage

### Web Interface

1. Upload a financial document (PDF)
2. Wait for processing to complete
3. View the extracted data, including:
   - Total portfolio value
   - Securities (ISINs, names, quantities, prices, values)
   - Asset allocation
   - Accuracy metrics

### API

The API provides the following endpoints:

- `POST /api/process`: Upload and process a document
- `GET /api/status/:taskId`: Check processing status
- `GET /api/result/:taskId`: Get processing result
- `GET /api/visualizations/:taskId`: Get visualizations

## Testing

To run the simple test script:

1. Place a PDF file named `messos.pdf` in the `simple_test` directory
2. Run the test script:
   ```
   cd backend
   npm test
   ```

## Deployment to Google Cloud

1. Push the code to GitHub
2. Set up a Google Cloud Run service
3. Configure the service to build from the GitHub repository
4. Set the required environment variables
5. Deploy the service

## License

This project is licensed under the MIT License - see the LICENSE file for details.
