import React, { useState } from 'react';
import { Box, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react';
import FinancialAnalysisDashboard from '../components/FinancialAnalysisDashboard';
import FinancialDocumentUploader from '../components/FinancialDocumentUploader';
import FinancialDataAnalyzer from '../components/FinancialDataAnalyzer';
import FinancialQueryEngine from '../components/FinancialQueryEngine';
import FinancialNotifications from '../components/FinancialNotifications';

const FinancialAnalysisPage = () => {
  const [documentData, setDocumentData] = useState(null);

  const handleDocumentProcessed = (data) => {
    setDocumentData(data.integrated_data || data);
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
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default FinancialAnalysisPage;
