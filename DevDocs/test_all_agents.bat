@echo off
echo Running all agent tests...

echo.
echo Testing DocumentPreprocessorAgent...
python DevDocs/test_document_preprocessor.py

echo.
echo Testing HebrewOCRAgent...
python DevDocs/test_hebrew_ocr.py

echo.
echo Testing ISINExtractorAgent...
python DevDocs/test_isin_extractor.py

echo.
echo Testing DocumentMergeAgent...
python DevDocs/test_document_merge.py

echo.
echo All tests completed.
