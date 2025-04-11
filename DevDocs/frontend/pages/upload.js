import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import FinDocLayout from '../components/FinDocLayout';

export default function UploadDocument() {
  const router = useRouter();
  const [files, setFiles] = useState([]);
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileType, setFileType] = useState('financial'); // Default file type

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files);
    }
  };

  const handleFileChange = (fileList) => {
    const newFiles = Array.from(fileList);

    // Filter for allowed file types
    const allowedExtensions = ['.pdf', '.docx', '.xlsx', '.csv', '.xls'];
    const filteredFiles = newFiles.filter(file => {
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      return allowedExtensions.includes(extension);
    });

    if (filteredFiles.length !== newFiles.length) {
      setError(`Some files were not added. Allowed formats: PDF, DOCX, XLSX, XLS, CSV`);
    }

    if (filteredFiles.length > 0) {
      // Check file sizes (max 10MB per file)
      const maxSize = 10 * 1024 * 1024; // 10MB
      const oversizedFiles = filteredFiles.filter(file => file.size > maxSize);

      if (oversizedFiles.length > 0) {
        setError(`Some files exceed the maximum size of 10MB: ${oversizedFiles.map(f => f.name).join(', ')}`);
        // Remove oversized files
        const validSizeFiles = filteredFiles.filter(file => file.size <= maxSize);
        if (validSizeFiles.length === 0) return;
        setFiles(validSizeFiles);
      } else {
        setFiles(filteredFiles);
      }

      // Auto-fill title from first filename (remove extension)
      const fileName = filteredFiles[0].name.replace(/\.[^/.]+$/, "");
      setTitle(fileName);

      // Auto-detect file type based on extension
      const firstFileExt = filteredFiles[0].name.toLowerCase().substring(filteredFiles[0].name.lastIndexOf('.'));
      if (['.xlsx', '.xls', '.csv'].includes(firstFileExt)) {
        setFileType('financial'); // Default to financial for spreadsheets
      } else if (firstFileExt === '.pdf') {
        // Keep current selection for PDFs
      }

      // Clear any previous errors
      setError(null);
    }
  };

  const removeFile = (index) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);

    if (newFiles.length === 0) {
      setTitle('');
    } else if (index === 0) {
      // If the first file was removed, update title based on the new first file
      const fileName = newFiles[0].name.replace(/\.[^/.]+$/, "");
      setTitle(fileName);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (files.length === 0) {
      setError("Please select at least one file to upload");
      return;
    }

    if (!title.trim() && files.length === 1) {
      setError("Please enter a document title");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setUploadProgress(0);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:24125';

      // Upload each file
      const uploadResults = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', fileType);

        // Add tags if provided
        if (tags.trim()) {
          const tagsArray = tags.split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0);
          formData.append('tags', JSON.stringify(tagsArray));
        }

        // Add title for single file upload
        if (files.length === 1 && title.trim()) {
          formData.append('title', title);
        } else {
          // For multiple files, use the filename as title
          const fileTitle = file.name.replace(/\.[^/.]+$/, "");
          formData.append('title', fileTitle);
        }

        // Add file processing options based on file type
        const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        if (['.xlsx', '.xls', '.csv'].includes(fileExt)) {
          formData.append('processing_options', JSON.stringify({
            extract_tables: true,
            detect_headers: true,
            sheet_names: 'all',
            convert_formulas: true
          }));
        } else if (fileExt === '.pdf') {
          formData.append('processing_options', JSON.stringify({
            ocr_enabled: true,
            extract_tables: true,
            extract_text: true,
            extract_metadata: true
          }));
        }

        // Upload the file with progress tracking
        const xhr = new XMLHttpRequest();

        // Create a promise to handle the XHR request
        const uploadPromise = new Promise((resolve, reject) => {
          xhr.open('POST', `${API_URL}/api/documents/upload`);

          xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
              // Calculate file progress percentage
              // Calculate overall progress based on current file and previous files
              const overallProgress = Math.round(((i + (event.loaded / event.total)) / files.length) * 100);
              setUploadProgress(overallProgress);
            }
          };

          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const result = JSON.parse(xhr.responseText);
                resolve(result);
              } catch (e) {
                reject(new Error('Invalid response format'));
              }
            } else {
              reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
            }
          };

          xhr.onerror = () => reject(new Error('Network error during upload'));
          xhr.onabort = () => reject(new Error('Upload aborted'));

          xhr.send(formData);
        });

        try {
          const result = await uploadPromise;
          console.log('Document uploaded:', result);
          uploadResults.push(result);
        } catch (uploadError) {
          throw uploadError;
        }
      }

      // Show success message
      setSuccess(`Successfully uploaded ${files.length} file${files.length > 1 ? 's' : ''}`);

      // Clear form
      setFiles([]);
      setTitle('');
      setTags('');

      // Redirect to dashboard after a delay
      setTimeout(() => {
        router.push('/');
      }, 2000);

    } catch (error) {
      console.error('Error uploading document:', error);
      setError("Failed to upload document. Please try again.");
      setUploadProgress(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FinDocLayout>
      <Head>
        <title>Upload Document | FinDoc Analyzer</title>
      </Head>

      <div className="upload-page">
        <h1 className="page-title">Upload Document</h1>

        <div className="upload-card">
          <form onSubmit={handleSubmit}>
            {/* File type selection */}
            <div className="form-group">
              <label className="form-label">Document Type</label>
              <div className="file-type-selector">
                <button
                  type="button"
                  className={`file-type-btn ${fileType === 'financial' ? 'active' : ''}`}
                  onClick={() => setFileType('financial')}
                >
                  <span className="file-type-icon">💰</span>
                  <span className="file-type-name">Financial</span>
                </button>
                <button
                  type="button"
                  className={`file-type-btn ${fileType === 'report' ? 'active' : ''}`}
                  onClick={() => setFileType('report')}
                >
                  <span className="file-type-icon">📊</span>
                  <span className="file-type-name">Report</span>
                </button>
                <button
                  type="button"
                  className={`file-type-btn ${fileType === 'contract' ? 'active' : ''}`}
                  onClick={() => setFileType('contract')}
                >
                  <span className="file-type-icon">📝</span>
                  <span className="file-type-name">Contract</span>
                </button>
                <button
                  type="button"
                  className={`file-type-btn ${fileType === 'other' ? 'active' : ''}`}
                  onClick={() => setFileType('other')}
                >
                  <span className="file-type-icon">📄</span>
                  <span className="file-type-name">Other</span>
                </button>
              </div>
            </div>

            {/* File upload area */}
            <div
              className={`upload-area ${dragActive ? 'drag-active' : ''} ${files.length > 0 ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
            >
              {files.length > 0 ? (
                <div className="files-list">
                  {files.map((file, index) => (
                    <div key={index} className="file-info">
                      <div className="file-icon">📄</div>
                      <div className="file-details">
                        <div className="file-name">{file.name}</div>
                        <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                      </div>
                      <button
                        type="button"
                        className="remove-file-btn"
                        onClick={() => removeFile(index)}
                      >
                        &times;
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className="add-more-files-btn"
                    onClick={() => document.getElementById('file-input').click()}
                  >
                    + Add More Files
                  </button>
                </div>
              ) : (
                <>
                  <div className="upload-icon">📁</div>
                  <div className="upload-text">
                    <p className="primary-text">Drag & drop your files here</p>
                    <p className="secondary-text">or</p>
                    <label className="browse-btn">
                      Browse files
                      <input
                        id="file-input"
                        type="file"
                        className="visually-hidden"
                        multiple
                        onChange={(e) => handleFileChange(e.target.files)}
                        accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.csv"
                      />
                    </label>
                  </div>
                  <p className="upload-hint">Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX, CSV (max 10MB per file)</p>
                </>
              )}
            </div>

            {/* Document info fields */}
            <div className="form-group">
              <label className="form-label" htmlFor="title">Document Title</label>
              <input
                type="text"
                id="title"
                className="form-control"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="tags">Tags (comma separated)</label>
              <input
                type="text"
                id="tags"
                className="form-control"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="financial, report, quarterly"
              />
            </div>

            {/* Progress bar */}
            {loading && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <div className="progress-text">{uploadProgress}% Uploaded</div>
              </div>
            )}

            {/* Success message */}
            {success && (
              <div className="alert alert-success">
                {success}
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className="alert alert-danger">
                {error}
              </div>
            )}

            {/* Submit button */}
            <div className="form-actions">
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => router.push('/')}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Uploading...' : 'Upload Document'}
              </button>
            </div>
          </form>
        </div>

        <div className="upload-help">
          <h3>Document Analysis Features</h3>
          <ul className="feature-list">
            <li>Automatic ISIN extraction</li>
            <li>Financial data recognition</li>
            <li>Document categorization</li>
            <li>Text searchable PDFs</li>
            <li>Metadata extraction</li>
          </ul>

          <h3>File Type Processing</h3>
          <div className="file-type-processing">
            <div className="processing-item">
              <h4>PDF Files</h4>
              <ul className="feature-list">
                <li>OCR for scanned documents</li>
                <li>Table extraction</li>
                <li>Text content analysis</li>
                <li>Metadata extraction</li>
              </ul>
            </div>

            <div className="processing-item">
              <h4>Excel Files</h4>
              <ul className="feature-list">
                <li>Multi-sheet processing</li>
                <li>Table structure detection</li>
                <li>Formula evaluation</li>
                <li>Financial data extraction</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .upload-page {
          max-width: 900px;
          margin: 0 auto;
        }

        .page-title {
          margin-bottom: 1.5rem;
          font-size: 1.75rem;
          color: #2d3748;
        }

        .upload-card {
          background-color: white;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
          margin-bottom: 2rem;
        }

        .file-type-selector {
          display: flex;
          gap: 10px;
          margin-bottom: 15px;
          flex-wrap: wrap;
        }

        .file-type-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 10px;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s ease;
          flex: 1;
          min-width: 80px;
        }

        .file-type-btn:hover {
          border-color: #4299e1;
          background-color: #f7fafc;
        }

        .file-type-btn.active {
          border-color: #4299e1;
          background-color: #ebf8ff;
        }

        .file-type-icon {
          font-size: 1.5rem;
          margin-bottom: 5px;
        }

        .file-type-name {
          font-size: 0.8rem;
        }

        .upload-area {
          border: 2px dashed #cbd5e0;
          border-radius: 8px;
          padding: 2rem;
          text-align: center;
          margin-bottom: 1.5rem;
          transition: all 0.3s;
        }

        .upload-area.drag-active {
          border-color: #3498db;
          background-color: rgba(52, 152, 219, 0.05);
        }

        .upload-area.has-file {
          border-style: solid;
          border-color: #3498db;
          background-color: rgba(52, 152, 219, 0.05);
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          color: #a0aec0;
        }

        .primary-text {
          font-size: 1.25rem;
          font-weight: 500;
          margin-bottom: 0.5rem;
          color: #4a5568;
        }

        .secondary-text {
          margin-bottom: 0.5rem;
          color: #718096;
        }

        .browse-btn {
          display: inline-block;
          background-color: #3498db;
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.3s;
        }

        .browse-btn:hover {
          background-color: #2980b9;
        }

        .upload-hint {
          margin-top: 1rem;
          font-size: 0.875rem;
          color: #a0aec0;
        }

        .files-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          width: 100%;
        }

        .file-info {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.5rem 1rem;
          background-color: white;
          border-radius: 4px;
        }

        .add-more-files-btn {
          margin-top: 10px;
          padding: 10px;
          border: 1px dashed #e2e8f0;
          border-radius: 8px;
          background-color: #f7fafc;
          color: #4299e1;
          cursor: pointer;
          transition: all 0.2s ease;
          width: 100%;
        }

        .add-more-files-btn:hover {
          background-color: #ebf8ff;
          border-color: #4299e1;
        }

        .file-icon {
          font-size: 2rem;
          margin-right: 1rem;
          color: #3498db;
        }

        .file-details {
          flex: 1;
          text-align: left;
        }

        .file-name {
          font-weight: 500;
          color: #4a5568;
          margin-bottom: 0.25rem;
        }

        .file-size {
          font-size: 0.875rem;
          color: #718096;
        }

        .remove-file-btn {
          background: none;
          border: none;
          color: #e53e3e;
          font-size: 1.5rem;
          cursor: pointer;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .upload-help {
          background-color: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .upload-help h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          color: #2d3748;
          font-size: 1.25rem;
        }

        .feature-list {
          list-style-type: none;
          padding: 0;
        }

        .feature-list li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
          color: #4a5568;
        }

        .feature-list li:before {
          content: "✓";
          color: #38a169;
          position: absolute;
          left: 0;
        }

        .file-type-processing {
          display: flex;
          gap: 20px;
          margin-top: 20px;
        }

        .processing-item {
          flex: 1;
          background-color: #f7fafc;
          border-radius: 8px;
          padding: 15px;
          border: 1px solid #e2e8f0;
        }

        .processing-item h4 {
          margin-top: 0;
          margin-bottom: 10px;
          color: #4a5568;
          font-size: 1rem;
        }

        @media (max-width: 640px) {
          .file-type-processing {
            flex-direction: column;
          }
        }

        .upload-progress {
          margin: 20px 0;
        }

        .progress-bar {
          height: 8px;
          background-color: #edf2f7;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 5px;
        }

        .progress-bar-fill {
          height: 100%;
          background-color: #4299e1;
          transition: width 0.3s ease;
        }

        .progress-text {
          font-size: 0.8rem;
          color: #718096;
          text-align: right;
        }

        .alert-success {
          background-color: #f0fff4;
          border: 1px solid #c6f6d5;
          color: #2f855a;
          padding: 0.75rem 1rem;
          border-radius: 0.25rem;
          margin-bottom: 1rem;
        }

        .alert-danger {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          color: #e53e3e;
          padding: 0.75rem 1rem;
          border-radius: 0.25rem;
          margin-bottom: 1rem;
        }
      `}</style>
    </FinDocLayout>
  );
}
