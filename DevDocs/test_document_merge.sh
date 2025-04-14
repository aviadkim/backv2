#!/bin/bash
echo "Running DocumentMergeAgent tests..."
python DevDocs/test_document_merge.py "$@"
echo "Test completed."
