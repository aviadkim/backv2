"""
GitHub OCR Fallback - Uses external OCR tools from GitHub repositories.
"""
import os
import sys
import subprocess
import json
import tempfile
import shutil
import requests
from pathlib import Path

class GitHubOCRFallback:
    """Fallback OCR using external tools from GitHub repositories."""
    
    def __init__(self):
        self.tools = {
            'ocrmypdf': {
                'repo': 'https://github.com/ocrmypdf/OCRmyPDF',
                'install_cmd': 'pip install ocrmypdf',
                'run_cmd': 'ocrmypdf --force-ocr --output-type pdf --skip-text --optimize 0 --deskew --clean --language eng+heb {input} {output}'
            },
            'tesseract_advanced': {
                'repo': 'https://github.com/tesseract-ocr/tesseract',
                'install_cmd': 'pip install pytesseract',
                'run_cmd': 'tesseract {input} {output} -l eng+heb --psm 6'
            },
            'markitdown': {
                'repo': 'https://github.com/microsoft/MarkItDown',
                'install_cmd': 'pip install markitdown',
                'run_cmd': 'python -m markitdown.cli {input} --output {output}'
            }
        }
        self.temp_dir = None
    
    def process(self, pdf_path):
        """Process a PDF document using external OCR tools."""
        print("GitHub OCR Fallback: Using external OCR tools...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        print(f"Created temporary directory: {self.temp_dir}")
        
        results = {}
        
        try:
            # Try each tool
            for tool_name, tool_info in self.tools.items():
                print(f"Trying {tool_name}...")
                
                # Check if tool is installed
                if not self._is_tool_installed(tool_name):
                    print(f"{tool_name} is not installed. Attempting to install...")
                    self._install_tool(tool_name, tool_info)
                
                # Run the tool
                result = self._run_tool(tool_name, tool_info, pdf_path)
                if result:
                    results[tool_name] = result
            
            # Save results
            output_dir = 'agent_results'
            os.makedirs(output_dir, exist_ok=True)
            
            with open(os.path.join(output_dir, 'github_ocr_results.json'), 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            print(f"GitHub OCR Fallback: Processed with {len(results)} tools")
            
            return results
        
        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Removed temporary directory: {self.temp_dir}")
    
    def _is_tool_installed(self, tool_name):
        """Check if a tool is installed."""
        if tool_name == 'ocrmypdf':
            try:
                subprocess.run(['ocrmypdf', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                return True
            except FileNotFoundError:
                return False
        
        elif tool_name == 'tesseract_advanced':
            try:
                subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                return True
            except FileNotFoundError:
                return False
        
        elif tool_name == 'markitdown':
            try:
                subprocess.run(['python', '-m', 'markitdown.cli', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                return False
        
        return False
    
    def _install_tool(self, tool_name, tool_info):
        """Install a tool."""
        try:
            print(f"Installing {tool_name}...")
            subprocess.run(tool_info['install_cmd'], shell=True, check=True)
            print(f"Successfully installed {tool_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing {tool_name}: {str(e)}")
            return False
    
    def _run_tool(self, tool_name, tool_info, pdf_path):
        """Run a tool on the PDF."""
        try:
            # Prepare input and output paths
            input_path = pdf_path
            output_dir = os.path.join(self.temp_dir, tool_name)
            os.makedirs(output_dir, exist_ok=True)
            
            if tool_name == 'ocrmypdf':
                output_path = os.path.join(output_dir, 'output.pdf')
                text_path = os.path.join(output_dir, 'output.txt')
                
                # Run OCRmyPDF
                cmd = tool_info['run_cmd'].format(input=input_path, output=output_path)
                subprocess.run(cmd, shell=True, check=True)
                
                # Extract text from the OCRed PDF
                subprocess.run(f'pdftotext {output_path} {text_path}', shell=True, check=True)
                
                # Read the extracted text
                with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                return {
                    'text': text,
                    'output_path': output_path
                }
            
            elif tool_name == 'tesseract_advanced':
                output_base = os.path.join(output_dir, 'output')
                output_path = output_base + '.txt'
                
                # Convert PDF to images and process each page
                from pdf2image import convert_from_path
                
                try:
                    pages = convert_from_path(input_path)
                    all_text = ""
                    
                    for i, page in enumerate(pages):
                        page_path = os.path.join(output_dir, f'page_{i+1}.png')
                        page.save(page_path)
                        
                        page_output_base = os.path.join(output_dir, f'page_{i+1}')
                        cmd = tool_info['run_cmd'].format(input=page_path, output=page_output_base)
                        subprocess.run(cmd, shell=True, check=True)
                        
                        # Read the extracted text
                        page_output_path = page_output_base + '.txt'
                        if os.path.exists(page_output_path):
                            with open(page_output_path, 'r', encoding='utf-8', errors='ignore') as f:
                                all_text += f.read() + "\n\n"
                    
                    return {
                        'text': all_text,
                        'output_dir': output_dir
                    }
                
                except Exception as e:
                    print(f"Error processing PDF with Tesseract: {str(e)}")
                    return None
            
            elif tool_name == 'markitdown':
                output_path = os.path.join(output_dir, 'output.md')
                
                # Run MarkItDown
                cmd = tool_info['run_cmd'].format(input=input_path, output=output_path)
                subprocess.run(cmd, shell=True, check=True)
                
                # Read the extracted text
                if os.path.exists(output_path):
                    with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    
                    return {
                        'text': text,
                        'output_path': output_path
                    }
                else:
                    print(f"Output file not found: {output_path}")
                    return None
            
            return None
        
        except Exception as e:
            print(f"Error running {tool_name}: {str(e)}")
            return None
    
    def download_github_repo(self, repo_url, target_dir):
        """Download a GitHub repository."""
        try:
            # Extract owner and repo name from URL
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            # Download as zip
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            response = requests.get(zip_url, stream=True)
            
            if response.status_code == 200:
                zip_path = os.path.join(self.temp_dir, f"{repo}.zip")
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract zip
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                
                print(f"Downloaded and extracted {repo_url} to {target_dir}")
                return True
            else:
                print(f"Failed to download {repo_url}: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"Error downloading {repo_url}: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github_ocr_fallback.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    fallback = GitHubOCRFallback()
    fallback.process(pdf_path)
