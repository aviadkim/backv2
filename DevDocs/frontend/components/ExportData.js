import React, { useState } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiDownload, FiFileText, FiDatabase, FiList } from 'react-icons/fi';
import exportController from '../controllers/exportController';

const ExportData = ({ portfolio, documents, selectedDocuments }) => {
  const [exportType, setExportType] = useState('portfolio');
  const [exportFormat, setExportFormat] = useState('csv');
  const [options, setOptions] = useState({
    includeMetadata: true,
    includeContent: false,
    fileName: '',
    dateFormat: 'YYYY-MM-DD'
  });
  const [exporting, setExporting] = useState(false);

  const handleOptionChange = (key, value) => {
    setOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleExport = async () => {
    if (exportType === 'portfolio' && !portfolio) {
      alert('No portfolio selected');
      return;
    }

    if ((exportType === 'document' || exportType === 'selectedDocuments') &&
        (!documents || documents.length === 0) &&
        (!selectedDocuments || selectedDocuments.length === 0)) {
      alert('No documents available');
      return;
    }

    setExporting(true);

    try {
      let blob;
      let fileName = options.fileName || 'export';

      switch (exportType) {
        case 'portfolio':
          blob = await exportController.exportPortfolio(portfolio, exportFormat, options);
          fileName = options.fileName || `${portfolio.name}_export`;
          break;

        case 'portfolioHoldings':
          blob = await exportController.exportPortfolioHoldings(portfolio, exportFormat, options);
          fileName = options.fileName || `${portfolio.name}_holdings`;
          break;

        case 'document':
          if (documents && documents.length > 0) {
            blob = await exportController.exportDocument(documents[0], exportFormat, options);
            fileName = options.fileName || `${documents[0].title}_export`;
          }
          break;

        case 'allDocuments':
          if (documents && documents.length > 0) {
            blob = await exportController.exportDocuments(documents, exportFormat, options);
            fileName = options.fileName || 'all_documents_export';
          }
          break;

        case 'selectedDocuments':
          if (selectedDocuments && selectedDocuments.length > 0) {
            blob = await exportController.exportDocuments(selectedDocuments, exportFormat, options);
            fileName = options.fileName || 'selected_documents_export';
          }
          break;

        default:
          throw new Error(`Unsupported export type: ${exportType}`);
      }

      if (blob) {
        // Create a download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName}.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Error exporting data');
    } finally {
      setExporting(false);
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Export Data</h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Export Type</label>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            <label className={`flex items-center p-3 rounded-md ${
              exportType === 'portfolio' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportType === 'portfolio'}
                onChange={() => setExportType('portfolio')}
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-700">Portfolio</span>
                <span className="block text-xs text-gray-500">Export portfolio summary</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportType === 'portfolioHoldings' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportType === 'portfolioHoldings'}
                onChange={() => setExportType('portfolioHoldings')}
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-700">Holdings</span>
                <span className="block text-xs text-gray-500">Export portfolio holdings</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportType === 'document' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportType === 'document'}
                onChange={() => setExportType('document')}
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-700">Document</span>
                <span className="block text-xs text-gray-500">Export single document</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportType === 'allDocuments' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportType === 'allDocuments'}
                onChange={() => setExportType('allDocuments')}
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-700">All Documents</span>
                <span className="block text-xs text-gray-500">Export all documents</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportType === 'selectedDocuments' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportType === 'selectedDocuments'}
                onChange={() => setExportType('selectedDocuments')}
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-700">Selected Documents</span>
                <span className="block text-xs text-gray-500">Export selected documents</span>
              </div>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Export Format</label>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <label className={`flex items-center p-3 rounded-md ${
              exportFormat === 'csv' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportFormat === 'csv'}
                onChange={() => setExportFormat('csv')}
              />
              <div className="ml-3 flex items-center">
                <FiFileText className="h-5 w-5 text-gray-400 mr-2" />
                <span className="block text-sm font-medium text-gray-700">CSV</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportFormat === 'excel' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportFormat === 'excel'}
                onChange={() => setExportFormat('excel')}
              />
              <div className="ml-3 flex items-center">
                <FiList className="h-5 w-5 text-gray-400 mr-2" />
                <span className="block text-sm font-medium text-gray-700">Excel</span>
              </div>
            </label>

            <label className={`flex items-center p-3 rounded-md ${
              exportFormat === 'json' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
            }`}>
              <input
                type="radio"
                className="form-radio h-4 w-4 text-blue-600"
                checked={exportFormat === 'json'}
                onChange={() => setExportFormat('json')}
              />
              <div className="ml-3 flex items-center">
                <FiDatabase className="h-5 w-5 text-gray-400 mr-2" />
                <span className="block text-sm font-medium text-gray-700">JSON</span>
              </div>
            </label>
          </div>
        </div>

        <div>
          <label htmlFor="file-name" className="block text-sm font-medium text-gray-700 mb-1">
            File Name (optional)
          </label>
          <input
            type="text"
            id="file-name"
            value={options.fileName}
            onChange={(e) => handleOptionChange('fileName', e.target.value)}
            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="export_data"
          />
          <p className="mt-1 text-xs text-gray-500">
            File extension will be added automatically
          </p>
        </div>

        <div className="flex flex-col space-y-2">
          <label className="block text-sm font-medium text-gray-700">Options</label>

          <div className="flex items-center">
            <input
              id="include-metadata"
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              checked={options.includeMetadata}
              onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
            />
            <label htmlFor="include-metadata" className="ml-2 block text-sm text-gray-700">
              Include Metadata
            </label>
          </div>

          {(exportType === 'document' || exportType === 'allDocuments' || exportType === 'selectedDocuments') && (
            <div className="flex items-center">
              <input
                id="include-content"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={options.includeContent}
                onChange={(e) => handleOptionChange('includeContent', e.target.checked)}
              />
              <label htmlFor="include-content" className="ml-2 block text-sm text-gray-700">
                Include Document Content
              </label>
            </div>
          )}
        </div>

        <div className="pt-4">
          <button
            type="button"
            onClick={handleExport}
            disabled={exporting}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              exporting ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
          >
            <FiDownload className="mr-2 -ml-1 h-5 w-5" />
            {exporting ? 'Exporting...' : 'Export Data'}
          </button>
        </div>
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default ExportData;
