#!/bin/bash

# Install frontend dependencies
cd DevDocs/frontend
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion react-router-dom

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Install root dependencies
cd ../..
pip install -r requirements.txt

# Install additional dependencies for AI enhanced processor
pip install requests python-dotenv pdfplumber

echo "All dependencies installed successfully!"
