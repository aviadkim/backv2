document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const uploadForm = document.getElementById('upload-form');
  const uploadButton = document.getElementById('upload-button');
  const progressCard = document.getElementById('progress-card');
  const progressBar = document.getElementById('progress-bar');
  const statusInput = document.getElementById('status');
  const errorContainer = document.getElementById('error-container');
  const errorElement = document.getElementById('error');
  const resultCard = document.getElementById('result-card');
  
  const documentName = document.getElementById('document-name');
  const documentDate = document.getElementById('document-date');
  const processingTime = document.getElementById('processing-time');
  const totalValue = document.getElementById('total-value');
  const currency = document.getElementById('currency');
  const securitiesCount = document.getElementById('securities-count');
  const assetClassesCount = document.getElementById('asset-classes-count');
  const accuracyContainer = document.getElementById('accuracy-container');
  
  const viewSecuritiesButton = document.getElementById('view-securities-button');
  const viewVisualizationsButton = document.getElementById('view-visualizations-button');
  const downloadJsonButton = document.getElementById('download-json-button');
  
  const securitiesModal = new bootstrap.Modal(document.getElementById('securities-modal'));
  const securitiesTable = document.getElementById('securities-table').querySelector('tbody');
  
  const visualizationsModal = new bootstrap.Modal(document.getElementById('visualizations-modal'));
  const visualizationsContainer = document.getElementById('visualizations-container');
  
  // Current task
  let currentTask = null;
  let currentResult = null;
  let pollingInterval = null;
  
  // Event listeners
  uploadForm.addEventListener('submit', handleUpload);
  viewSecuritiesButton.addEventListener('click', showSecurities);
  viewVisualizationsButton.addEventListener('click', showVisualizations);
  downloadJsonButton.addEventListener('click', downloadJson);
  
  // Handle file upload
  async function handleUpload(event) {
    event.preventDefault();
    
    // Get form data
    const formData = new FormData(uploadForm);
    
    // Disable form
    uploadButton.disabled = true;
    uploadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
    
    try {
      // Upload file
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Show progress card
      progressCard.classList.remove('d-none');
      errorContainer.classList.add('d-none');
      resultCard.classList.add('d-none');
      
      // Set current task
      currentTask = data.task_id;
      
      // Start polling
      startPolling();
    } catch (error) {
      showError(error.message);
    } finally {
      // Enable form
      uploadButton.disabled = false;
      uploadButton.textContent = 'Process Document';
    }
  }
  
  // Start polling for task status
  function startPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    // Update status immediately
    updateStatus();
    
    // Poll every 2 seconds
    pollingInterval = setInterval(updateStatus, 2000);
  }
  
  // Update task status
  async function updateStatus() {
    if (!currentTask) {
      return;
    }
    
    try {
      const response = await fetch(`/api/status/${currentTask}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get status: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Update progress
      const progress = Math.round(data.progress * 100);
      progressBar.style.width = `${progress}%`;
      progressBar.textContent = `${progress}%`;
      progressBar.setAttribute('aria-valuenow', progress);
      
      // Update status
      statusInput.value = data.status;
      
      // Handle completed or failed status
      if (data.status === 'completed') {
        clearInterval(pollingInterval);
        getResult();
      } else if (data.status === 'failed') {
        clearInterval(pollingInterval);
        showError(data.error || 'Processing failed');
      }
    } catch (error) {
      showError(error.message);
      clearInterval(pollingInterval);
    }
  }
  
  // Get result
  async function getResult() {
    try {
      const response = await fetch(`/api/result/${currentTask}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get result: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Store result
      currentResult = data;
      
      // Show result
      showResult(data);
    } catch (error) {
      showError(error.message);
    }
  }
  
  // Show result
  function showResult(result) {
    // Show result card
    resultCard.classList.remove('d-none');
    
    // Update document info
    documentName.textContent = result.document_info.document_name;
    documentDate.textContent = result.document_info.document_date;
    processingTime.textContent = `${result.document_info.processing_time.toFixed(2)} seconds`;
    
    // Update portfolio summary
    totalValue.textContent = formatCurrency(result.portfolio.total_value, result.portfolio.currency);
    currency.textContent = result.portfolio.currency;
    securitiesCount.textContent = result.metrics.total_securities;
    assetClassesCount.textContent = result.metrics.total_asset_classes;
    
    // Update accuracy
    if (result.accuracy) {
      accuracyContainer.innerHTML = '';
      
      for (const [key, value] of Object.entries(result.accuracy)) {
        const accuracyItem = document.createElement('div');
        accuracyItem.className = 'accuracy-item';
        
        const label = document.createElement('span');
        label.className = 'accuracy-label';
        label.textContent = formatKey(key);
        
        const valueSpan = document.createElement('span');
        valueSpan.className = 'accuracy-value';
        valueSpan.textContent = `${(value * 100).toFixed(2)}%`;
        
        const bar = document.createElement('span');
        bar.className = 'accuracy-bar';
        bar.style.width = `${value * 100}px`;
        
        accuracyItem.appendChild(label);
        accuracyItem.appendChild(valueSpan);
        accuracyItem.appendChild(bar);
        
        accuracyContainer.appendChild(accuracyItem);
      }
    }
  }
  
  // Show securities
  function showSecurities() {
    if (!currentResult) {
      return;
    }
    
    // Clear table
    securitiesTable.innerHTML = '';
    
    // Add securities
    for (const security of currentResult.portfolio.securities) {
      const row = document.createElement('tr');
      
      row.innerHTML = `
        <td>${security.isin}</td>
        <td>${security.name}</td>
        <td>${security.quantity ? security.quantity.toLocaleString() : 'N/A'}</td>
        <td>${security.price ? security.price.toLocaleString() : 'N/A'}</td>
        <td>${security.value ? security.value.toLocaleString() : 'N/A'}</td>
        <td>${security.currency || 'N/A'}</td>
        <td>${security.asset_class || 'N/A'}</td>
      `;
      
      securitiesTable.appendChild(row);
    }
    
    // Show modal
    securitiesModal.show();
  }
  
  // Show visualizations
  async function showVisualizations() {
    if (!currentTask) {
      return;
    }
    
    try {
      const response = await fetch(`/api/visualizations/${currentTask}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get visualizations: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Clear container
      visualizationsContainer.innerHTML = '';
      
      // Add visualizations
      if (data.files && data.files.length > 0) {
        for (const file of data.files) {
          const item = document.createElement('div');
          item.className = 'visualization-item';
          
          const img = document.createElement('img');
          img.src = file;
          img.alt = 'Visualization';
          
          item.appendChild(img);
          visualizationsContainer.appendChild(item);
        }
      } else {
        visualizationsContainer.innerHTML = '<p>No visualizations available</p>';
      }
      
      // Show modal
      visualizationsModal.show();
    } catch (error) {
      alert(`Error loading visualizations: ${error.message}`);
    }
  }
  
  // Download JSON
  function downloadJson() {
    if (!currentResult) {
      return;
    }
    
    const json = JSON.stringify(currentResult, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentResult.document_info.document_id}_processed.json`;
    a.click();
    
    URL.revokeObjectURL(url);
  }
  
  // Show error
  function showError(message) {
    errorContainer.classList.remove('d-none');
    errorElement.textContent = message;
  }
  
  // Format currency
  function formatCurrency(value, currencyCode) {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    return `${value.toLocaleString()} ${currencyCode}`;
  }
  
  // Format key
  function formatKey(key) {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }
});
