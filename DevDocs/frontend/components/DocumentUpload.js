import React, { useState, useCallback, useRef } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiFile, FiX, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { useDocument } from '../providers/DocumentProvider';

const DocumentUpload = ({ onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadErrors, setUploadErrors] = useState({});
  const [uploadSuccess, setUploadSuccess] = useState({});
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');

  const { uploadDocument } = useDocument();
  const fileInputRef = useRef(null);

  // Maximum file size (10MB)
  const MAX_FILE_SIZE = 10 * 1024 * 1024;

  // Accepted file types
  const ACCEPTED_FILE_TYPES = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'text/csv': ['.csv']
  };

  // Handle file drop
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle accepted files
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: `${file.name}-${Date.now()}`,
      title: file.name.split('.')[0] // Default title is filename without extension
    }));

    setFiles(prevFiles => [...prevFiles, ...newFiles]);

    // Handle rejected files
    rejectedFiles.forEach(rejected => {
      const { file, errors } = rejected;
      const errorMessages = errors.map(e => e.message).join(', ');

      setUploadErrors(prev => ({
        ...prev,
        [`${file.name}-${Date.now()}`]: errorMessages
      }));
    });
  }, []);

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true
  });

  // Handle file removal
  const removeFile = (id) => {
    setFiles(files.filter(file => file.id !== id));

    // Also remove any progress, errors, or success states
    const newProgress = { ...uploadProgress };
    const newErrors = { ...uploadErrors };
    const newSuccess = { ...uploadSuccess };

    delete newProgress[id];
    delete newErrors[id];
    delete newSuccess[id];

    setUploadProgress(newProgress);
    setUploadErrors(newErrors);
    setUploadSuccess(newSuccess);
  };

  // Handle title change
  const handleTitleChange = (id, newTitle) => {
    setFiles(files.map(file =>
      file.id === id ? { ...file, title: newTitle } : file
    ));
  };

  // Handle tag input
  const handleTagInputChange = (e) => {
    setTagInput(e.target.value);
  };

  // Add tag
  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  // Handle tag input key press
  const handleTagKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  // Remove tag
  const removeTag = (tag) => {
    setTags(tags.filter(t => t !== tag));
  };

  // Upload files
  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);

    // Process files sequentially
    for (const fileObj of files) {
      try {
        // Create a new XMLHttpRequest to track progress
        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(prev => ({
              ...prev,
              [fileObj.id]: progress
            }));
          }
        });

        // Create form data
        const formData = new FormData();
        formData.append('file', fileObj.file);
        formData.append('title', fileObj.title);

        if (tags.length > 0) {
          formData.append('tags', JSON.stringify(tags));
        }

        // Upload the file
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData,
          xhr: xhr
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();

        // Mark as success
        setUploadSuccess(prev => ({
          ...prev,
          [fileObj.id]: true
        }));

        // Call the callback if provided
        if (onUploadComplete) {
          onUploadComplete(result.document);
        }
      } catch (error) {
        console.error(`Error uploading ${fileObj.file.name}:`, error);

        // Mark as error
        setUploadErrors(prev => ({
          ...prev,
          [fileObj.id]: error.message || 'Upload failed'
        }));
      }
    }

    setUploading(false);
  };

  // Get file icon based on type
  const getFileIcon = (file) => {
    const type = file.type;

    if (type.includes('pdf')) {
      return <FiFile className="text-red-500" />;
    } else if (type.includes('word') || type.includes('doc')) {
      return <FiFile className="text-blue-500" />;
    } else if (type.includes('excel') || type.includes('sheet') || type.includes('csv')) {
      return <FiFile className="text-green-500" />;
    } else {
      return <FiFile className="text-gray-500" />;
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="space-y-6">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
        }`}
      >
        <input {...getInputProps()} ref={fileInputRef} />

        <div className="flex flex-col items-center justify-center space-y-3">
          <FiUpload className="h-12 w-12 text-gray-400" />
          <p className="text-lg font-medium text-gray-700">
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </p>
          <p className="text-sm text-gray-500">or</p>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Browse Files
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX, CSV (max 10MB per file)
          </p>
        </div>
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Tags</label>
        <div className="flex flex-wrap gap-2 mb-2">
          {tags.map(tag => (
            <span
              key={tag}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1.5 inline-flex items-center justify-center h-4 w-4 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none"
              >
                <FiX className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
        <div className="flex">
          <input
            type="text"
            value={tagInput}
            onChange={handleTagInputChange}
            onKeyPress={handleTagKeyPress}
            placeholder="Add a tag"
            className="flex-grow px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={addTag}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Add
          </button>
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Selected Files</h3>
          <ul className="divide-y divide-gray-200 border border-gray-200 rounded-md">
            {files.map(fileObj => (
              <li key={fileObj.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <div className="flex-shrink-0">
                      {getFileIcon(fileObj.file)}
                    </div>
                    <div className="ml-3 min-w-0 flex-1">
                      <div className="flex items-center">
                        <input
                          type="text"
                          value={fileObj.title}
                          onChange={(e) => handleTitleChange(fileObj.id, e.target.value)}
                          className="block w-full border-0 p-0 text-gray-900 placeholder-gray-500 focus:ring-0 sm:text-sm"
                          placeholder="Enter title"
                        />
                      </div>
                      <div className="text-xs text-gray-500">
                        {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                    {uploadSuccess[fileObj.id] && (
                      <FiCheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {uploadErrors[fileObj.id] && (
                      <div className="flex items-center">
                        <FiAlertCircle className="h-5 w-5 text-red-500" />
                        <span className="ml-1 text-xs text-red-500">{uploadErrors[fileObj.id]}</span>
                      </div>
                    )}
                    {uploadProgress[fileObj.id] !== undefined && !uploadSuccess[fileObj.id] && !uploadErrors[fileObj.id] && (
                      <div className="w-16 bg-gray-200 rounded-full h-2.5">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full"
                          style={{ width: `${uploadProgress[fileObj.id]}%` }}
                        ></div>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => removeFile(fileObj.id)}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <FiX className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={uploadFiles}
              disabled={uploading || files.length === 0}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                uploading || files.length === 0
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
              }`}
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}
    </div>
    </AccessibilityWrapper>
  );
};

export default DocumentUpload;
