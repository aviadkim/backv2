/**
 * Data Export Service
 * 
 * Provides functionality for exporting financial data to various formats.
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const ExcelJS = require('exceljs');
const { Parser } = require('json2csv');
const PDFDocument = require('pdfkit');
const logger = require('../../utils/logger');
const config = require('../../config');
const supabase = require('../../db/supabase');
const { v4: uuidv4 } = require('uuid');

// Promisify fs functions
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const unlink = promisify(fs.unlink);

/**
 * Export data to Excel
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 * @returns {Promise<string>} Path to exported file
 */
async function exportToExcel(data, options = {}) {
  try {
    // Create export directory if it doesn't exist
    const exportDir = path.join(config.upload.exportDir, uuidv4());
    await mkdir(exportDir, { recursive: true });
    
    // Create Excel workbook
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'FinDoc Analyzer';
    workbook.lastModifiedBy = 'FinDoc Analyzer';
    workbook.created = new Date();
    workbook.modified = new Date();
    
    // Add portfolio summary sheet
    if (data.portfolio) {
      const summarySheet = workbook.addWorksheet('Portfolio Summary');
      
      // Add header
      summarySheet.addRow(['Portfolio Summary']);
      summarySheet.addRow([]);
      
      // Add portfolio details
      summarySheet.addRow(['Total Value', data.portfolio.total_value]);
      summarySheet.addRow(['Currency', data.portfolio.currency]);
      summarySheet.addRow(['Total Securities', data.metrics.total_securities]);
      summarySheet.addRow(['Total Asset Classes', data.metrics.total_asset_classes]);
      summarySheet.addRow([]);
      
      // Add asset allocation
      summarySheet.addRow(['Asset Allocation']);
      summarySheet.addRow(['Asset Class', 'Percentage', 'Value']);
      
      for (const [assetClass, allocation] of Object.entries(data.portfolio.asset_allocation)) {
        summarySheet.addRow([
          assetClass,
          allocation.percentage,
          allocation.value
        ]);
      }
      
      // Format cells
      summarySheet.getCell('A1').font = { bold: true, size: 16 };
      summarySheet.getCell('A8').font = { bold: true, size: 14 };
      
      // Format percentage column
      const percentageColumn = summarySheet.getColumn(2);
      percentageColumn.numFmt = '0.00%';
      
      // Format value column
      const valueColumn = summarySheet.getColumn(3);
      valueColumn.numFmt = '#,##0.00';
      
      // Adjust column widths
      summarySheet.columns.forEach(column => {
        column.width = 20;
      });
    }
    
    // Add securities sheet
    if (data.portfolio && data.portfolio.securities) {
      const securitiesSheet = workbook.addWorksheet('Securities');
      
      // Add header
      securitiesSheet.addRow(['Securities']);
      securitiesSheet.addRow([]);
      
      // Add securities table
      securitiesSheet.addRow(['Name', 'ISIN', 'Quantity', 'Price', 'Value', 'Percentage']);
      
      // Calculate total value
      const totalValue = data.portfolio.total_value;
      
      // Add securities
      for (const security of data.portfolio.securities) {
        securitiesSheet.addRow([
          security.name,
          security.isin,
          security.quantity,
          security.price,
          security.value,
          security.value / totalValue
        ]);
      }
      
      // Format cells
      securitiesSheet.getCell('A1').font = { bold: true, size: 16 };
      securitiesSheet.getRow(3).font = { bold: true };
      
      // Format percentage column
      const percentageColumn = securitiesSheet.getColumn(6);
      percentageColumn.numFmt = '0.00%';
      
      // Format value column
      const valueColumn = securitiesSheet.getColumn(5);
      valueColumn.numFmt = '#,##0.00';
      
      // Format price column
      const priceColumn = securitiesSheet.getColumn(4);
      priceColumn.numFmt = '#,##0.00';
      
      // Adjust column widths
      securitiesSheet.columns.forEach(column => {
        column.width = 20;
      });
    }
    
    // Add comparison sheet if comparison data is provided
    if (data.comparison) {
      const comparisonSheet = workbook.addWorksheet('Comparison');
      
      // Add header
      comparisonSheet.addRow(['Portfolio Comparison']);
      comparisonSheet.addRow([]);
      
      // Add comparison details
      comparisonSheet.addRow(['Document 1', data.comparison.document1.name]);
      comparisonSheet.addRow(['Document 2', data.comparison.document2.name]);
      comparisonSheet.addRow(['Comparison Date', data.comparison.comparison_date]);
      comparisonSheet.addRow([]);
      
      // Add portfolio value comparison
      comparisonSheet.addRow(['Portfolio Value Comparison']);
      comparisonSheet.addRow(['Metric', 'Value']);
      comparisonSheet.addRow(['Total Value Difference', data.comparison.portfolio_comparison.total_value_difference]);
      comparisonSheet.addRow(['Total Value Percentage Change', data.comparison.portfolio_comparison.total_value_percentage_change / 100]);
      comparisonSheet.addRow([]);
      
      // Add significant changes
      comparisonSheet.addRow(['Significant Changes']);
      comparisonSheet.addRow(['Type', 'Description', 'Percentage Change']);
      
      for (const change of data.comparison.summary.significant_changes) {
        comparisonSheet.addRow([
          change.type,
          change.description,
          change.percentage_change ? change.percentage_change / 100 : change.percentage ? change.percentage / 100 : 0
        ]);
      }
      
      // Format cells
      comparisonSheet.getCell('A1').font = { bold: true, size: 16 };
      comparisonSheet.getCell('A7').font = { bold: true, size: 14 };
      comparisonSheet.getCell('A11').font = { bold: true, size: 14 };
      
      // Format percentage columns
      comparisonSheet.getCell('B10').numFmt = '0.00%';
      
      // Format percentage change column
      const percentageColumn = comparisonSheet.getColumn(3);
      percentageColumn.numFmt = '0.00%';
      
      // Adjust column widths
      comparisonSheet.columns.forEach(column => {
        column.width = 30;
      });
    }
    
    // Save workbook
    const filePath = path.join(exportDir, `export_${Date.now()}.xlsx`);
    await workbook.xlsx.writeFile(filePath);
    
    return filePath;
  } catch (error) {
    logger.error('Error exporting to Excel:', error);
    throw error;
  }
}

/**
 * Export data to CSV
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 * @returns {Promise<string>} Path to exported file
 */
async function exportToCsv(data, options = {}) {
  try {
    // Create export directory if it doesn't exist
    const exportDir = path.join(config.upload.exportDir, uuidv4());
    await mkdir(exportDir, { recursive: true });
    
    // Create CSV files
    const files = [];
    
    // Export portfolio summary
    if (data.portfolio) {
      // Create asset allocation CSV
      const assetAllocationData = Object.entries(data.portfolio.asset_allocation).map(([assetClass, allocation]) => ({
        AssetClass: assetClass,
        Percentage: allocation.percentage,
        Value: allocation.value
      }));
      
      const assetAllocationParser = new Parser({
        fields: ['AssetClass', 'Percentage', 'Value']
      });
      
      const assetAllocationCsv = assetAllocationParser.parse(assetAllocationData);
      const assetAllocationPath = path.join(exportDir, 'asset_allocation.csv');
      
      await writeFile(assetAllocationPath, assetAllocationCsv);
      files.push(assetAllocationPath);
    }
    
    // Export securities
    if (data.portfolio && data.portfolio.securities) {
      // Calculate total value
      const totalValue = data.portfolio.total_value;
      
      // Create securities CSV
      const securitiesData = data.portfolio.securities.map(security => ({
        Name: security.name,
        ISIN: security.isin,
        Quantity: security.quantity,
        Price: security.price,
        Value: security.value,
        Percentage: security.value / totalValue
      }));
      
      const securitiesParser = new Parser({
        fields: ['Name', 'ISIN', 'Quantity', 'Price', 'Value', 'Percentage']
      });
      
      const securitiesCsv = securitiesParser.parse(securitiesData);
      const securitiesPath = path.join(exportDir, 'securities.csv');
      
      await writeFile(securitiesPath, securitiesCsv);
      files.push(securitiesPath);
    }
    
    // Export comparison data
    if (data.comparison) {
      // Create significant changes CSV
      const changesData = data.comparison.summary.significant_changes.map(change => ({
        Type: change.type,
        Description: change.description,
        PercentageChange: change.percentage_change || change.percentage || 0
      }));
      
      const changesParser = new Parser({
        fields: ['Type', 'Description', 'PercentageChange']
      });
      
      const changesCsv = changesParser.parse(changesData);
      const changesPath = path.join(exportDir, 'significant_changes.csv');
      
      await writeFile(changesPath, changesCsv);
      files.push(changesPath);
    }
    
    // Create a zip file with all CSV files
    // For simplicity, we'll just return the first file for now
    return files[0];
  } catch (error) {
    logger.error('Error exporting to CSV:', error);
    throw error;
  }
}

/**
 * Export data to PDF
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 * @returns {Promise<string>} Path to exported file
 */
async function exportToPdf(data, options = {}) {
  try {
    // Create export directory if it doesn't exist
    const exportDir = path.join(config.upload.exportDir, uuidv4());
    await mkdir(exportDir, { recursive: true });
    
    // Create PDF document
    const filePath = path.join(exportDir, `export_${Date.now()}.pdf`);
    const doc = new PDFDocument({ margin: 50 });
    
    // Pipe output to file
    const stream = fs.createWriteStream(filePath);
    doc.pipe(stream);
    
    // Add title
    doc.fontSize(25).text('Financial Data Export', { align: 'center' });
    doc.moveDown();
    
    // Add portfolio summary
    if (data.portfolio) {
      doc.fontSize(18).text('Portfolio Summary');
      doc.moveDown();
      
      doc.fontSize(12).text(`Total Value: ${data.portfolio.total_value} ${data.portfolio.currency}`);
      doc.text(`Total Securities: ${data.metrics.total_securities}`);
      doc.text(`Total Asset Classes: ${data.metrics.total_asset_classes}`);
      doc.moveDown();
      
      // Add asset allocation
      doc.fontSize(16).text('Asset Allocation');
      doc.moveDown();
      
      // Create a table-like structure
      const assetAllocationTable = {
        headers: ['Asset Class', 'Percentage', 'Value'],
        rows: []
      };
      
      for (const [assetClass, allocation] of Object.entries(data.portfolio.asset_allocation)) {
        assetAllocationTable.rows.push([
          assetClass,
          `${(allocation.percentage * 100).toFixed(2)}%`,
          allocation.value.toFixed(2)
        ]);
      }
      
      // Draw table
      drawTable(doc, assetAllocationTable);
      doc.moveDown(2);
    }
    
    // Add securities
    if (data.portfolio && data.portfolio.securities) {
      doc.fontSize(18).text('Securities');
      doc.moveDown();
      
      // Create a table-like structure
      const securitiesTable = {
        headers: ['Name', 'ISIN', 'Quantity', 'Price', 'Value'],
        rows: []
      };
      
      // Add top 10 securities by value
      const topSecurities = [...data.portfolio.securities]
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);
      
      for (const security of topSecurities) {
        securitiesTable.rows.push([
          security.name,
          security.isin,
          security.quantity.toString(),
          security.price.toFixed(2),
          security.value.toFixed(2)
        ]);
      }
      
      // Draw table
      drawTable(doc, securitiesTable);
      doc.moveDown(2);
    }
    
    // Add comparison data
    if (data.comparison) {
      doc.fontSize(18).text('Portfolio Comparison');
      doc.moveDown();
      
      doc.fontSize(12).text(`Document 1: ${data.comparison.document1.name}`);
      doc.text(`Document 2: ${data.comparison.document2.name}`);
      doc.text(`Comparison Date: ${new Date(data.comparison.comparison_date).toLocaleDateString()}`);
      doc.moveDown();
      
      doc.text(`Total Value Difference: ${data.comparison.portfolio_comparison.total_value_difference.toFixed(2)}`);
      doc.text(`Total Value Percentage Change: ${data.comparison.portfolio_comparison.total_value_percentage_change.toFixed(2)}%`);
      doc.moveDown();
      
      // Add significant changes
      doc.fontSize(16).text('Significant Changes');
      doc.moveDown();
      
      // Create a table-like structure
      const changesTable = {
        headers: ['Type', 'Description', 'Percentage Change'],
        rows: []
      };
      
      for (const change of data.comparison.summary.significant_changes) {
        changesTable.rows.push([
          change.type,
          change.description,
          `${(change.percentage_change || change.percentage || 0).toFixed(2)}%`
        ]);
      }
      
      // Draw table
      drawTable(doc, changesTable);
    }
    
    // Add footer
    const pageCount = doc.bufferedPageRange().count;
    for (let i = 0; i < pageCount; i++) {
      doc.switchToPage(i);
      
      // Add page number
      doc.fontSize(10).text(
        `Page ${i + 1} of ${pageCount}`,
        50,
        doc.page.height - 50,
        { align: 'center' }
      );
      
      // Add timestamp
      doc.fontSize(10).text(
        `Generated on ${new Date().toLocaleString()}`,
        50,
        doc.page.height - 30,
        { align: 'center' }
      );
    }
    
    // Finalize PDF
    doc.end();
    
    // Wait for stream to finish
    return new Promise((resolve, reject) => {
      stream.on('finish', () => resolve(filePath));
      stream.on('error', reject);
    });
  } catch (error) {
    logger.error('Error exporting to PDF:', error);
    throw error;
  }
}

/**
 * Draw a table in the PDF document
 * @param {Object} doc - PDF document
 * @param {Object} table - Table data
 */
function drawTable(doc, table) {
  // Calculate column widths
  const pageWidth = doc.page.width - 100;
  const columnWidth = pageWidth / table.headers.length;
  
  // Draw headers
  doc.fontSize(10).font('Helvetica-Bold');
  
  table.headers.forEach((header, i) => {
    doc.text(header, 50 + (i * columnWidth), doc.y, {
      width: columnWidth,
      align: 'left'
    });
  });
  
  doc.moveDown();
  doc.font('Helvetica');
  
  // Draw rows
  table.rows.forEach(row => {
    const rowHeight = 20;
    const y = doc.y;
    
    // Check if we need a new page
    if (y + rowHeight > doc.page.height - 100) {
      doc.addPage();
    }
    
    // Draw cells
    row.forEach((cell, i) => {
      doc.text(cell, 50 + (i * columnWidth), doc.y, {
        width: columnWidth,
        align: 'left'
      });
    });
    
    doc.moveDown();
  });
}

/**
 * Export data to JSON
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 * @returns {Promise<string>} Path to exported file
 */
async function exportToJson(data, options = {}) {
  try {
    // Create export directory if it doesn't exist
    const exportDir = path.join(config.upload.exportDir, uuidv4());
    await mkdir(exportDir, { recursive: true });
    
    // Create JSON file
    const filePath = path.join(exportDir, `export_${Date.now()}.json`);
    await writeFile(filePath, JSON.stringify(data, null, 2));
    
    return filePath;
  } catch (error) {
    logger.error('Error exporting to JSON:', error);
    throw error;
  }
}

/**
 * Export data to a specific format
 * @param {string} documentId - Document ID
 * @param {string} format - Export format
 * @param {Object} options - Export options
 * @returns {Promise<string>} Path to exported file
 */
async function exportData(documentId, format, options = {}) {
  try {
    // Get document data
    const client = supabase.getClient();
    const { data: documentData, error } = await client
      .from('document_data')
      .select('*')
      .eq('document_id', documentId)
      .in('data_type', ['financial_data', 'comparison'])
      .order('created_at', { ascending: false });
    
    if (error) {
      logger.error('Error getting document data:', error);
      throw new Error('Error getting document data');
    }
    
    // Get financial data
    const financialData = documentData.find(data => data.data_type === 'financial_data');
    
    if (!financialData) {
      throw new Error('No financial data found for this document');
    }
    
    // Get comparison data if available
    const comparisonData = documentData.find(data => data.data_type === 'comparison');
    
    // Prepare data for export
    const exportData = {
      ...financialData.content
    };
    
    if (comparisonData) {
      exportData.comparison = comparisonData.content;
    }
    
    // Export data to specified format
    let filePath;
    
    switch (format.toLowerCase()) {
      case 'excel':
      case 'xlsx':
        filePath = await exportToExcel(exportData, options);
        break;
      case 'csv':
        filePath = await exportToCsv(exportData, options);
        break;
      case 'pdf':
        filePath = await exportToPdf(exportData, options);
        break;
      case 'json':
        filePath = await exportToJson(exportData, options);
        break;
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
    
    return filePath;
  } catch (error) {
    logger.error('Error exporting data:', error);
    throw error;
  }
}

module.exports = {
  exportData,
  exportToExcel,
  exportToCsv,
  exportToPdf,
  exportToJson
};
