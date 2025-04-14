import React from 'react';
import { Box, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react';
import FinancialAnalysisDashboard from '../components/FinancialAnalysisDashboard';
import FinancialDocumentUploader from '../components/FinancialDocumentUploader';
import FinancialDataAnalyzer from '../components/FinancialDataAnalyzer';

const FinancialAnalysisPage = () => {
  return (
    <Box p={4}>
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>Dashboard</Tab>
          <Tab>Upload Document</Tab>
          <Tab>Analyze Data</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <FinancialAnalysisDashboard />
          </TabPanel>
          
          <TabPanel>
            <FinancialDocumentUploader />
          </TabPanel>
          
          <TabPanel>
            <FinancialDataAnalyzer />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default FinancialAnalysisPage;
