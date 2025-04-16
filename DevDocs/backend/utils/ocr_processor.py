"""
OCR Processor utility for financial documents using OCRmyPDF.
"""
import os
import tempfile
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Utility class for processing PDFs with OCRmyPDF.
    """
    
    @staticmethod
    def process_pdf(input_file_path, output_file_path=None, language="eng+heb", deskew=True, clean=True):
        """
        Process a PDF file with OCRmyPDF.
        
        Args:
            input_file_path (str): Path to the input PDF file
            output_file_path (str, optional): Path to save the output PDF file. If None, a temporary file will be created.
            language (str, optional): Language(s) to use for OCR. Default is "eng+heb" for English and Hebrew.
            deskew (bool, optional): Whether to deskew the PDF. Default is True.
            clean (bool, optional): Whether to clean the PDF. Default is True.
            
        Returns:
            str: Path to the processed PDF file
        """
        try:
            # If no output path is provided, create a temporary file
            if output_file_path is None:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    output_file_path = temp_file.name
            
            # Build the OCRmyPDF command
            cmd = ["ocrmypdf"]
            
            # Add language option
            cmd.extend(["-l", language])
            
            # Add deskew option if requested
            if deskew:
                cmd.append("--deskew")
            
            # Add clean option if requested
            if clean:
                cmd.append("--clean")
            
            # Add optimization options
            cmd.extend(["--optimize", "3"])
            
            # Add input and output file paths
            cmd.extend([input_file_path, output_file_path])
            
            # Run OCRmyPDF
            logger.info(f"Running OCRmyPDF with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"OCRmyPDF completed successfully: {result.stdout}")
            return output_file_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"OCRmyPDF failed: {e.stderr}")
            raise RuntimeError(f"OCRmyPDF processing failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    @staticmethod
    def process_financial_pdf(input_file_path, output_file_path=None):
        """
        Process a financial PDF with optimized settings for financial documents.
        
        Args:
            input_file_path (str): Path to the input PDF file
            output_file_path (str, optional): Path to save the output PDF file
            
        Returns:
            str: Path to the processed PDF file
        """
        # Financial documents often contain tables and numbers that need to be precisely recognized
        # Use higher DPI and specialized settings for financial documents
        try:
            # If no output path is provided, create a temporary file
            if output_file_path is None:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    output_file_path = temp_file.name
            
            # Build the OCRmyPDF command with financial document optimizations
            cmd = [
                "ocrmypdf",
                "-l", "eng+heb",  # English and Hebrew languages
                "--deskew",       # Straighten crooked pages
                "--clean",        # Clean the image before OCR
                "--optimize", "3", # Maximum optimization
                "--force-ocr",    # Force OCR even if text is already present
                "--skip-big", "100", # Skip very large pages (100 MP)
                "--pdfa-image-compression", "jpeg", # Use JPEG compression for images
                "--output-type", "pdfa", # Output as PDF/A for archiving
                "--rotate-pages", # Automatically rotate pages
                input_file_path,
                output_file_path
            ]
            
            # Run OCRmyPDF
            logger.info(f"Running OCRmyPDF for financial document with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Financial document OCR completed successfully: {result.stdout}")
            return output_file_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Financial document OCR failed: {e.stderr}")
            # If the process fails, try with simpler options
            logger.info("Retrying with simpler options...")
            return OCRProcessor.process_pdf(input_file_path, output_file_path, language="eng+heb", deskew=True, clean=True)
        except Exception as e:
            logger.error(f"Error processing financial PDF: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """
        Extract text from a PDF file using pdfminer.six.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        from pdfminer.high_level import extract_text
        
        try:
            text = extract_text(pdf_path)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

def main():
    """
    Main function for testing the OCR processor.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process a PDF file with OCRmyPDF")
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output-file", help="Path to save the output PDF file")
    parser.add_argument("--financial", action="store_true", help="Use financial document optimizations")
    parser.add_argument("--language", default="eng+heb", help="Language(s) to use for OCR")
    parser.add_argument("--no-deskew", action="store_true", help="Disable deskewing")
    parser.add_argument("--no-clean", action="store_true", help="Disable cleaning")
    
    args = parser.parse_args()
    
    try:
        if args.financial:
            output_path = OCRProcessor.process_financial_pdf(args.input_file, args.output_file)
        else:
            output_path = OCRProcessor.process_pdf(
                args.input_file, 
                args.output_file,
                language=args.language,
                deskew=not args.no_deskew,
                clean=not args.no_clean
            )
        
        print(f"PDF processed successfully. Output saved to: {output_path}")
        
        # Extract and print some text from the processed PDF
        text = OCRProcessor.extract_text_from_pdf(output_path)
        print("\nExtracted text sample:")
        print(text[:500] + "..." if len(text) > 500 else text)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
