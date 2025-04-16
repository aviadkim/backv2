import React, { useState } from 'react';
import { Box, Tabs } from '@chakra-ui/react';

// Create custom tab components
const TabList = ({ children, ...props }) => (
  <Box
    as="div"
    display="flex"
    borderBottom="1px"
    borderColor="gray.200"
    {...props}
  >
    {children}
  </Box>
);

const Tab = ({ children, isSelected, onClick, ...props }) => (
  <Box
    as="button"
    px="4"
    py="2"
    fontWeight={isSelected ? "bold" : "normal"}
    borderBottom={isSelected ? "2px solid" : "none"}
    borderColor={isSelected ? "blue.500" : "transparent"}
    color={isSelected ? "blue.500" : "gray.600"}
    _hover={{ color: "blue.400" }}
    onClick={onClick}
    {...props}
  >
    {children}
  </Box>
);

const TabPanels = ({ children, ...props }) => (
  <Box pt="4" {...props}>
    {children}
  </Box>
);

const TabPanel = ({ children, ...props }) => (
  <Box {...props}>
    {children}
  </Box>
);
import FinancialAnalysisDashboard from '../components/FinancialAnalysisDashboard';
import FinancialDocumentUploader from '../components/FinancialDocumentUploader';
import FinancialDataAnalyzer from '../components/FinancialDataAnalyzer';
import FinancialQueryEngine from '../components/FinancialQueryEngine';
import FinancialNotifications from '../components/FinancialNotifications';
import DataExportTool from '../components/DataExportTool';
import DocumentComparisonTool from '../components/DocumentComparisonTool';
import FinancialAdvisorTool from '../components/FinancialAdvisorTool';

const FinancialAnalysisPage = () => {
  const [documentData, setDocumentData] = useState(null);
  const [processedDocuments, setProcessedDocuments] = useState([]);

  const handleDocumentProcessed = (data) => {
    const processedData = data.integrated_data || data;
    setDocumentData(processedData);

    // Add to processed documents history
    if (processedData && processedData.document_id) {
      const docDate = processedData.processing_date || new Date().toISOString();
      const docName = processedData.metadata?.document_type || 'Document';

      // Check if document already exists in history
      const existingIndex = processedDocuments.findIndex(doc => doc.id === processedData.document_id);

      if (existingIndex >= 0) {
        // Update existing document
        const updatedDocs = [...processedDocuments];
        updatedDocs[existingIndex] = {
          id: processedData.document_id,
          name: docName,
          date: docDate,
          data: processedData
        };
        setProcessedDocuments(updatedDocs);
      } else {
        // Add new document
        setProcessedDocuments([
          ...processedDocuments,
          {
            id: processedData.document_id,
            name: docName,
            date: docDate,
            data: processedData
          }
        ]);
      }
    }
  };

  return (
    <Box p={4}>
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>Dashboard</Tab>
          <Tab>Upload Document</Tab>
          <Tab>Analyze Data</Tab>
          <Tab>Query Engine</Tab>
          <Tab>Notifications</Tab>
          <Tab>Export Data</Tab>
          <Tab>Compare Documents</Tab>
          <Tab>Financial Advisor</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <FinancialAnalysisDashboard />
          </TabPanel>

          <TabPanel>
            <FinancialDocumentUploader onDocumentProcessed={handleDocumentProcessed} />
          </TabPanel>

          <TabPanel>
            <FinancialDataAnalyzer />
          </TabPanel>

          <TabPanel>
            <FinancialQueryEngine documentData={documentData} />
          </TabPanel>

          <TabPanel>
            <FinancialNotifications documentData={documentData} />
          </TabPanel>

          <TabPanel>
            <DataExportTool documentData={documentData} />
          </TabPanel>

          <TabPanel>
            <DocumentComparisonTool
              documentData={documentData}
              previousDocuments={processedDocuments.filter(doc => doc.id !== documentData?.document_id)}
            />
          </TabPanel>

          <TabPanel>
            <FinancialAdvisorTool documentData={documentData} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default FinancialAnalysisPage;
