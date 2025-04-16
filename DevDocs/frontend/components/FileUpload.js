import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload, FaFile, FaFileAlt, FaFilePdf, FaFileImage, FaFileExcel, FaTimes } from 'react-icons/fa';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'text/csv': ['.csv'],
};

const FileUpload = ({ onUpload, maxFiles = 5, maxSize = MAX_FILE_SIZE, acceptedTypes = ACCEPTED_FILE_TYPES }) => {
  const [files, setFiles] = useState([]);
  const [errors, setErrors] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle accepted files
    if (acceptedFiles?.length) {
      // Check if adding these files would exceed the maxFiles limit
      if (files.length + acceptedFiles.length > maxFiles) {
        setErrors(prev => [...prev, `You can only upload a maximum of ${maxFiles} files`]);
        // Only add files up to the limit
        const remainingSlots = maxFiles - files.length;
        if (remainingSlots > 0) {
          const newFiles = acceptedFiles.slice(0, remainingSlots).map(file => 
            Object.assign(file, { preview: URL.createObjectURL(file) })
          );
          setFiles(prev => [...prev, ...newFiles]);
        }
      } else {
        // Add all accepted files
        const newFiles = acceptedFiles.map(file => 
          Object.assign(file, { preview: URL.createObjectURL(file) })
        );
        setFiles(prev => [...prev, ...newFiles]);
      }
    }

    // Handle rejected files
    if (rejectedFiles?.length) {
      const newErrors = rejectedFiles.map(({ file, errors }) => {
        const errorMessages = errors.map(e => {
          if (e.code === 'file-too-large') {
            return `File "${file.name}" is too large. Max size is ${formatBytes(maxSize)}.`;
          }
          if (e.code === 'file-invalid-type') {
            return `File "${file.name}" has an invalid file type.`;
          }
          return `File "${file.name}" - ${e.message}`;
        });
        return errorMessages.join(', ');
      });
      
      setErrors(prev => [...prev, ...newErrors]);
    }
  }, [files, maxFiles, maxSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    maxSize,
    maxFiles,
  });

  const removeFile = (index) => {
    setFiles(files => {
      const newFiles = [...files];
      // Release the object URL to avoid memory leaks
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const clearErrors = (index) => {
    setErrors(errors => {
      const newErrors = [...errors];
      newErrors.splice(index, 1);
      return newErrors;
    });
  };

  const handleUpload = () => {
    if (files.length === 0) {
      setErrors(prev => [...prev, 'Please select at least one file to upload']);
      return;
    }
    
    onUpload(files);
  };

  // Helper function to format bytes
  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  // Get file icon based on file type
  const getFileIcon = (file) => {
    const type = file.type;
    
    if (type.includes('pdf')) return <FaFilePdf className="text-red-500" />;
    if (type.includes('image')) return <FaFileImage className="text-blue-500" />;
    if (type.includes('excel') || type.includes('spreadsheet') || type.includes('csv')) {
      return <FaFileExcel className="text-green-500" />;
    }
    
    return <FaFileAlt className="text-gray-500" />;
  };

  return (
    <AccessibilityWrapper>
      
    <div className="space-y-4">
      {/* Dropzone */}
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
        }`}
      >
        <input {...getInputProps()} />
        <FaUpload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm font-medium text-gray-900">
          {isDragActive ? 'Drop the files here' : 'Drag and drop files here, or click to select files'}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Accepted file types: PDF, JPG, PNG, XLSX, XLS, CSV
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Maximum file size: {formatBytes(maxSize)}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Maximum files: {maxFiles}
        </p>
      </div>

      {/* Error messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <FaTimes className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                There {errors.length === 1 ? 'was an error' : `were ${errors.length} errors`} with your submission
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc pl-5 space-y-1">
                  {errors.map((error, index) => (
                    <li key={index} className="flex justify-between items-center">
                      <span>{error}</span>
                      <button 
                        onClick={() => clearErrors(index)}
                        className="ml-2 text-red-500 hover:text-red-700"
                      >
                        <FaTimes className="h-4 w-4" />
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-md overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {files.map((file, index) => (
              <li key={index} className="px-4 py-3 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {getFileIcon(file)}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900 truncate" style={{ maxWidth: '200px' }}>
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatBytes(file.size)}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="ml-2 text-gray-400 hover:text-gray-500"
                >
                  <FaTimes className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload button */}
      {files.length > 0 && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleUpload}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Upload {files.length} {files.length === 1 ? 'file' : 'files'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
