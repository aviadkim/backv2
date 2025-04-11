'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';

interface DocumentUploaderProps {
  onUploadComplete: (documentId: string, documentName: string) => void;
}

export default function DocumentUploader({ onUploadComplete }: DocumentUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Only render on client-side to avoid hydration issues
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];

      // Check if file is a PDF
      if (selectedFile.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];

      // Check if file is a PDF
      if (droppedFile.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }

      setFile(droppedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', 'en');

    try {
      // Make a fetch request to upload the file
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      // Simulate upload progress (in a real implementation, you would use XMLHttpRequest with progress events)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      if (!response.ok) {
        throw new Error(`Upload failed with status ${response.status}`);
      }

      const data = await response.json();

      // Complete the progress
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Pass the document ID to the parent component
      onUploadComplete(data.id, file.name);

      // Reset the uploader
      setTimeout(() => {
        setUploading(false);
        setFile(null);
        setUploadProgress(0);
      }, 1000);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload document. Please try again.');
      setUploading(false);
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Return a loading state or simplified UI during server-side rendering
  if (!mounted) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="border-2 border-dashed rounded-lg p-8 text-center border-gray-300">
            <p className="mb-4">Loading document uploader...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardContent className="pt-6">
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center ${
            error ? 'border-red-400 bg-red-50' : 'border-gray-300 hover:border-blue-400'
          }`}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {!file ? (
            <>
              <div className="mb-4">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <p className="mb-4 text-lg font-medium">Drag and drop your PDF file here, or</p>
              <Button onClick={handleBrowseClick}>Browse Files</Button>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept="application/pdf"
                onChange={handleFileChange}
              />
              {error && <p className="mt-4 text-red-500">{error}</p>}
            </>
          ) : (
            <div>
              <p className="mb-2 text-lg font-medium">Selected file:</p>
              <p className="mb-4 text-gray-600">{file.name}</p>

              {uploading ? (
                <div className="w-full">
                  <Progress value={uploadProgress} className="h-2 mb-2" />
                  <p className="text-sm text-gray-500">Uploading... {uploadProgress}%</p>
                </div>
              ) : (
                <div className="flex justify-center space-x-4">
                  <Button onClick={() => setFile(null)} variant="outline">
                    Cancel
                  </Button>
                  <Button onClick={handleUpload}>Upload Document</Button>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mt-6">
          <h3 className="font-semibold mb-2">Supported Document Types:</h3>
          <ul className="list-disc pl-5 text-gray-600">
            <li>PDF Financial Statements</li>
            <li>PDF Reports and Analysis</li>
            <li>PDF Invoices and Receipts</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
