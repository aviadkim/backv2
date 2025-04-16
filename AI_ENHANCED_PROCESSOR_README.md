# AI Enhanced Financial Document Processor

This system provides an AI-enhanced financial document processor with feedback learning capabilities. It can extract information from financial documents, learn from user corrections, and improve over time.

## Features

- **AI-Enhanced Extraction**: Uses AI to enhance extraction results and identify issues
- **Feedback Learning**: Learns from user corrections to improve future extractions
- **Memory**: Remembers corrections and applies them to similar documents
- **Web Interface**: Provides a web interface for uploading documents and viewing results

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the OpenRouter API key**:
   
   Create a `.env` file in the root directory with the following content:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```
   
   Alternatively, you can set the environment variable directly:
   ```bash
   export OPENROUTER_API_KEY=your_openrouter_api_key
   ```

## Usage

### Process a Document

```bash
python run_all_agents.py path/to/document.pdf
```

This will process the document and display a summary of the results.

### Record a Correction

```bash
python run_all_agents.py path/to/document.pdf --correct --field "portfolio_value" --original "1000000" --corrected "1500000"
```

This will process the document and record a correction for the specified field.

### Generate Improvement Suggestions

```bash
python run_all_agents.py path/to/document.pdf --suggestions
```

This will process the document and generate suggestions for improving extraction based on previous corrections.

### Use the Web Interface

```bash
python run_web_interface.py
```

Then open your browser and navigate to http://localhost:8080

## How the AI Learning Works

The AI learning system works as follows:

1. **Document Processing**: The system processes a financial document and extracts information.
2. **User Corrections**: The user reviews the extraction results and makes corrections if needed.
3. **Learning**: The system learns from these corrections using the OpenRouter API.
4. **Improvement**: When processing similar documents in the future, the system applies the learned corrections.
5. **Continuous Learning**: The system continues to learn and improve with each correction.

## Testing

To run the tests:

```bash
python run_tests_with_api_key.py
```

This will run all the tests with the API key from the environment.

To run specific tests:

```bash
python run_tests_with_api_key.py --test-type unit
python run_tests_with_api_key.py --test-type integration
```

## Components

- **AI Feedback Learning** (`ai_feedback_learning.py`): Implements the feedback learning mechanism
- **AI Enhanced Processor** (`ai_enhanced_processor.py`): Integrates the financial document processor with AI enhancement
- **Web Interface** (`web_interface.py`): Provides a web interface for the system
- **Run All Agents** (`run_all_agents.py`): Script to run all agents with the best processing combination
- **Run Web Interface** (`run_web_interface.py`): Script to run the web interface
- **Run Tests With API Key** (`run_tests_with_api_key.py`): Script to run tests with the API key

## Security

- The OpenRouter API key is stored in the `.env` file, which is excluded from version control.
- The system does not expose the API key in logs or output.
- All API requests are made securely using HTTPS.

## Next Steps

1. **Collect More Feedback**: The more corrections the system receives, the better it gets.
2. **Refine the Learning Algorithm**: Improve the similarity measures for finding relevant corrections.
3. **Add More AI Agents**: Integrate more specialized AI agents for specific tasks.
4. **Improve the Web Interface**: Add more features to the web interface for better user experience.
5. **Add Database Integration**: Store corrections and learning in a database for persistence.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
