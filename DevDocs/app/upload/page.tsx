'use client'; // Needed for useState and event handlers

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast"; // Import useToast
import { Progress } from "@/components/ui/progress"; // Import Progress

// Placeholder Icon
const UploadCloudIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-10 w-10 text-slate-400"}><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>
);
const CheckCircleIcon = ({ className }: { className?: string }) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
);
const AlertCircleIcon = ({ className }: { className?: string }) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
);


export default function UploadPage() {
  const [language, setLanguage] = useState<string>('heb+eng'); // Default to Hebrew + English
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0); // Progress for single file or overall
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const { toast } = useToast(); // Initialize toast

  const handleFileDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    setUploadStatus('idle'); // Reset status on new drop
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const pdfFiles = Array.from(event.dataTransfer.files).filter(file => file.type === 'application/pdf');
      if (pdfFiles.length !== event.dataTransfer.files.length) {
         toast({
            variant: "destructive",
            title: "Invalid File Type",
            description: "Only PDF files are allowed.",
          });
      }
      setFiles(pdfFiles);
      event.dataTransfer.clearData();
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
     setUploadStatus('idle'); // Reset status on new selection
     if (event.target.files && event.target.files.length > 0) {
       const pdfFiles = Array.from(event.target.files).filter(file => file.type === 'application/pdf');
       if (pdfFiles.length !== event.target.files.length) {
         toast({
            variant: "destructive",
            title: "Invalid File Type",
            description: "Only PDF files are allowed.",
          });
       }
       setFiles(pdfFiles);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };
  const handleDragEnter = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };
  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        variant: "destructive",
        title: "No Files Selected",
        description: "Please select one or more PDF files to upload.",
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus('uploading');
    setUploadProgress(0); // Reset progress

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    // Simulate successful upload after a delay
    setTimeout(() => {
      clearInterval(progressInterval);
      setUploadProgress(100);
      setIsUploading(false);
      setUploadStatus('success');
      toast({
        title: "Upload Complete",
        description: `${files.length} file(s) uploaded successfully. Processing started.`,
      });

      // Redirect to document analysis page after successful upload
      window.location.href = '/doc-test';
    }, 3000);

    // The rest of the function is handled in the setTimeout above
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-slate-800">Upload Documents</h1>

      <Card>
        <CardHeader>
          <CardTitle>Select Language and Files</CardTitle>
          <CardDescription>Choose the document language and upload your PDF files for analysis.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Language Selection */}
          <div className="space-y-2">
            <Label htmlFor="language-select">Document Language</Label>
            <Select value={language} onValueChange={setLanguage} disabled={isUploading}>
              <SelectTrigger id="language-select" className="w-[180px]">
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="he">Hebrew</SelectItem>
                <SelectItem value="heb+eng">Hebrew + English</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Drag and Drop Area */}
          <div
            className={`relative flex flex-col items-center justify-center w-full p-8 border-2 border-dashed rounded-lg cursor-pointer hover:border-slate-400 transition-colors ${isDragging ? 'border-indigo-600 bg-indigo-50' : 'border-slate-300 bg-slate-50'} ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onDrop={!isUploading ? handleFileDrop : undefined}
            onDragOver={!isUploading ? handleDragOver : undefined}
            onDragEnter={!isUploading ? handleDragEnter : undefined}
            onDragLeave={!isUploading ? handleDragLeave : undefined}
          >
             {/* Input is always present but visually hidden */}
             <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" // Make input cover the area
                accept=".pdf"
                multiple
                onChange={handleFileSelect}
                disabled={isUploading}
              />
            <UploadCloudIcon />
            <p className="mt-2 text-sm text-slate-600">
              <span className="font-semibold">Click to upload</span> or drag and drop PDFs here
            </p>
            <p className="text-xs text-slate-500">Supports batch uploads (PDF only)</p>
          </div>

           {/* Display Selected Files */}
           {files.length > 0 && !isUploading && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Selected files ({files.length}):</p>
              <ul className="list-disc list-inside text-sm text-slate-600 max-h-32 overflow-y-auto">
                {files.map((file, index) => (
                  <li key={index}>{file.name} ({(file.size / 1024).toFixed(1)} KB)</li>
                ))}
              </ul>
            </div>
          )}

          {/* Upload Progress and Status */}
          {uploadStatus === 'uploading' && (
            <div className="space-y-2">
               <Label>Uploading...</Label>
               <Progress value={uploadProgress} className="w-full" />
               <p className="text-sm text-slate-500">{Math.round(uploadProgress)}% complete</p>
            </div>
          )}
           {uploadStatus === 'success' && (
            <div className="flex items-center gap-2 text-green-600">
               <CheckCircleIcon className="h-5 w-5" />
               <p className="text-sm font-medium">Upload successful! Documents are processing.</p>
            </div>
          )}
           {uploadStatus === 'error' && (
             <div className="flex items-center gap-2 text-red-600">
               <AlertCircleIcon className="h-5 w-5" />
               <p className="text-sm font-medium">Upload failed. Please check errors and try again.</p>
            </div>
          )}


          {/* Upload Button */}
          <Button onClick={handleUpload} disabled={files.length === 0 || isUploading}>
            {isUploading ? 'Uploading...' : `Start Processing (${files.length})`}
          </Button>

        </CardContent>
      </Card>
    </div>
  );
}