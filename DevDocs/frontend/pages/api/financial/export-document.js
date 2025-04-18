// API endpoint for exporting financial document data

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { document_id, format, options } = req.body;

    if (!document_id) {
      return res.status(400).json({ error: 'Document ID is required' });
    }

    if (!format) {
      return res.status(400).json({ error: 'Export format is required' });
    }

    // In a real implementation, we would fetch the document from the database
    // and generate the export file in the requested format
    // For now, we'll return mock data

    // Set the appropriate content type based on the format
    const contentType = getContentType(format);
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename=document-${document_id}.${getFileExtension(format)}`);

    // Generate mock export data based on the format
    const exportData = generateMockExportData(format, options);
    
    // Send the export data
    res.status(200).send(exportData);
  } catch (error) {
    console.error('Error exporting document:', error);
    return res.status(500).json({ 
      error: 'Error exporting document', 
      detail: error.message 
    });
  }
}

/**
 * Get the content type for the export format
 * @param {string} format - Export format
 * @returns {string} - Content type
 */
function getContentType(format) {
  switch (format) {
    case 'json':
      return 'application/json';
    case 'csv':
      return 'text/csv';
    case 'excel':
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    case 'pdf':
      return 'application/pdf';
    default:
      return 'application/octet-stream';
  }
}

/**
 * Get the file extension for the export format
 * @param {string} format - Export format
 * @returns {string} - File extension
 */
function getFileExtension(format) {
  switch (format) {
    case 'json':
      return 'json';
    case 'csv':
      return 'csv';
    case 'excel':
      return 'xlsx';
    case 'pdf':
      return 'pdf';
    default:
      return 'txt';
  }
}

/**
 * Generate mock export data based on the format
 * @param {string} format - Export format
 * @param {Object} options - Export options
 * @returns {Buffer|string} - Export data
 */
function generateMockExportData(format, options) {
  // Mock document data
  const documentData = {
    id: '123456',
    filename: 'sample-portfolio.pdf',
    processed_at: '2023-04-15T00:00:00Z',
    document_type: 'portfolio',
    portfolio_value: 1950000,
    asset_allocation: {
      'Equities': 0.40,
      'Fixed Income': 0.35,
      'Cash': 0.05,
      'Alternative Investments': 0.20
    },
    securities: [
      {
        isin: 'US0378331005',
        name: 'Apple Inc.',
        quantity: 500,
        price: 190,
        value: 95000
      },
      {
        isin: 'US88160R1014',
        name: 'Tesla Inc.',
        quantity: 500,
        price: 210,
        value: 105000
      },
      {
        isin: 'US5949181045',
        name: 'Microsoft Corp.',
        quantity: 600,
        price: 300,
        value: 180000
      },
      {
        isin: 'US0231351067',
        name: 'Amazon.com Inc.',
        quantity: 300,
        price: 300,
        value: 90000
      },
      {
        isin: 'US30303M1027',
        name: 'Meta Platforms Inc.',
        quantity: 250,
        price: 300,
        value: 75000
      }
    ],
    tables: [
      {
        page: 1,
        extraction_method: 'camelot',
        table_number: 1,
        headers: ['Security', 'ISIN', 'Quantity', 'Price', 'Value'],
        rows: [
          ['Apple Inc.', 'US0378331005', '500', '$190.00', '$95,000.00'],
          ['Tesla Inc.', 'US88160R1014', '500', '$210.00', '$105,000.00'],
          ['Microsoft Corp.', 'US5949181045', '600', '$300.00', '$180,000.00'],
          ['Amazon.com Inc.', 'US0231351067', '300', '$300.00', '$90,000.00'],
          ['Meta Platforms Inc.', 'US30303M1027', '250', '$300.00', '$75,000.00']
        ]
      },
      {
        page: 2,
        extraction_method: 'camelot',
        table_number: 2,
        headers: ['Asset Class', 'Allocation', 'Value'],
        rows: [
          ['Equities', '40%', '$780,000.00'],
          ['Fixed Income', '35%', '$682,500.00'],
          ['Cash', '5%', '$97,500.00'],
          ['Alternative Investments', '20%', '$390,000.00']
        ]
      }
    ],
    isins: [
      {
        code: 'US0378331005',
        name: 'Apple Inc.',
        value: 95000
      },
      {
        code: 'US88160R1014',
        name: 'Tesla Inc.',
        value: 105000
      },
      {
        code: 'US5949181045',
        name: 'Microsoft Corp.',
        value: 180000
      },
      {
        code: 'US0231351067',
        name: 'Amazon.com Inc.',
        value: 90000
      },
      {
        code: 'US30303M1027',
        name: 'Meta Platforms Inc.',
        value: 75000
      }
    ],
    extracted_text: 'This is a sample portfolio statement with a total value of $1,950,000. The portfolio includes investments in equities, fixed income, cash, and alternative investments.'
  };

  // Filter data based on options
  const filteredData = {};
  
  if (options.includeText) {
    filteredData.extracted_text = documentData.extracted_text;
  }
  
  if (options.includeTables) {
    filteredData.tables = documentData.tables;
  }
  
  if (options.includeISINs) {
    filteredData.isins = documentData.isins;
  }
  
  if (options.includeFinancialData) {
    filteredData.portfolio_value = documentData.portfolio_value;
    filteredData.asset_allocation = documentData.asset_allocation;
    filteredData.securities = documentData.securities;
  }
  
  // Add basic document info
  filteredData.id = documentData.id;
  filteredData.filename = documentData.filename;
  filteredData.processed_at = documentData.processed_at;
  filteredData.document_type = documentData.document_type;

  // Generate export data based on format
  switch (format) {
    case 'json':
      return JSON.stringify(filteredData, null, 2);
    
    case 'csv':
      return generateCSV(filteredData);
    
    case 'excel':
      // In a real implementation, we would generate an Excel file
      // For now, we'll return a CSV file
      return generateCSV(filteredData);
    
    case 'pdf':
      // In a real implementation, we would generate a PDF file
      // For now, we'll return a text representation
      return generateTextReport(filteredData);
    
    default:
      return JSON.stringify(filteredData, null, 2);
  }
}

/**
 * Generate a CSV export
 * @param {Object} data - Document data
 * @returns {string} - CSV data
 */
function generateCSV(data) {
  let csv = '';
  
  // Add document info
  csv += 'Document Information\n';
  csv += 'ID,Filename,Processed At,Document Type\n';
  csv += `${data.id},${data.filename},${data.processed_at},${data.document_type}\n\n`;
  
  // Add portfolio value if available
  if (data.portfolio_value) {
    csv += 'Portfolio Value\n';
    csv += `$${data.portfolio_value.toLocaleString()}\n\n`;
  }
  
  // Add asset allocation if available
  if (data.asset_allocation) {
    csv += 'Asset Allocation\n';
    csv += 'Asset Class,Allocation,Value\n';
    
    for (const [assetClass, allocation] of Object.entries(data.asset_allocation)) {
      const value = data.portfolio_value * allocation;
      csv += `${assetClass},${(allocation * 100).toFixed(2)}%,$${value.toLocaleString()}\n`;
    }
    
    csv += '\n';
  }
  
  // Add securities if available
  if (data.securities) {
    csv += 'Securities\n';
    csv += 'Name,ISIN,Quantity,Price,Value\n';
    
    for (const security of data.securities) {
      csv += `${security.name},${security.isin},${security.quantity.toLocaleString()},$${security.price.toLocaleString()},$${security.value.toLocaleString()}\n`;
    }
    
    csv += '\n';
  }
  
  // Add ISINs if available
  if (data.isins && !data.securities) {
    csv += 'ISINs\n';
    csv += 'Code,Name,Value\n';
    
    for (const isin of data.isins) {
      csv += `${isin.code},${isin.name},$${isin.value.toLocaleString()}\n`;
    }
    
    csv += '\n';
  }
  
  // Add extracted text if available
  if (data.extracted_text) {
    csv += 'Extracted Text\n';
    csv += `"${data.extracted_text.replace(/"/g, '""')}"\n\n`;
  }
  
  // Add tables if available
  if (data.tables) {
    for (let i = 0; i < data.tables.length; i++) {
      const table = data.tables[i];
      
      csv += `Table ${i + 1} (Page ${table.page})\n`;
      
      // Add headers
      csv += table.headers.join(',') + '\n';
      
      // Add rows
      for (const row of table.rows) {
        csv += row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',') + '\n';
      }
      
      csv += '\n';
    }
  }
  
  return csv;
}

/**
 * Generate a text report
 * @param {Object} data - Document data
 * @returns {string} - Text report
 */
function generateTextReport(data) {
  let report = '';
  
  // Add document info
  report += '=== Document Information ===\n';
  report += `ID: ${data.id}\n`;
  report += `Filename: ${data.filename}\n`;
  report += `Processed At: ${new Date(data.processed_at).toLocaleString()}\n`;
  report += `Document Type: ${data.document_type}\n\n`;
  
  // Add portfolio value if available
  if (data.portfolio_value) {
    report += '=== Portfolio Value ===\n';
    report += `$${data.portfolio_value.toLocaleString()}\n\n`;
  }
  
  // Add asset allocation if available
  if (data.asset_allocation) {
    report += '=== Asset Allocation ===\n';
    
    for (const [assetClass, allocation] of Object.entries(data.asset_allocation)) {
      const value = data.portfolio_value * allocation;
      report += `${assetClass}: ${(allocation * 100).toFixed(2)}% ($${value.toLocaleString()})\n`;
    }
    
    report += '\n';
  }
  
  // Add securities if available
  if (data.securities) {
    report += '=== Securities ===\n';
    
    for (const security of data.securities) {
      report += `${security.name} (${security.isin})\n`;
      report += `  Quantity: ${security.quantity.toLocaleString()}\n`;
      report += `  Price: $${security.price.toLocaleString()}\n`;
      report += `  Value: $${security.value.toLocaleString()}\n\n`;
    }
  }
  
  // Add ISINs if available
  if (data.isins && !data.securities) {
    report += '=== ISINs ===\n';
    
    for (const isin of data.isins) {
      report += `${isin.code}: ${isin.name} ($${isin.value.toLocaleString()})\n`;
    }
    
    report += '\n';
  }
  
  // Add extracted text if available
  if (data.extracted_text) {
    report += '=== Extracted Text ===\n';
    report += data.extracted_text + '\n\n';
  }
  
  // Add tables if available
  if (data.tables) {
    for (let i = 0; i < data.tables.length; i++) {
      const table = data.tables[i];
      
      report += `=== Table ${i + 1} (Page ${table.page}) ===\n`;
      
      // Calculate column widths
      const columnWidths = [];
      
      // Initialize with header widths
      for (let j = 0; j < table.headers.length; j++) {
        columnWidths[j] = table.headers[j].length;
      }
      
      // Update with row cell widths
      for (const row of table.rows) {
        for (let j = 0; j < row.length; j++) {
          if (j < columnWidths.length) {
            columnWidths[j] = Math.max(columnWidths[j], row[j].length);
          } else {
            columnWidths[j] = row[j].length;
          }
        }
      }
      
      // Add headers
      for (let j = 0; j < table.headers.length; j++) {
        report += table.headers[j].padEnd(columnWidths[j] + 2);
      }
      report += '\n';
      
      // Add separator
      for (let j = 0; j < table.headers.length; j++) {
        report += '-'.repeat(columnWidths[j]) + '  ';
      }
      report += '\n';
      
      // Add rows
      for (const row of table.rows) {
        for (let j = 0; j < row.length; j++) {
          if (j < columnWidths.length) {
            report += row[j].padEnd(columnWidths[j] + 2);
          } else {
            report += row[j] + '  ';
          }
        }
        report += '\n';
      }
      
      report += '\n';
    }
  }
  
  return report;
}
