import React from 'react';
import { ChakraProvider, Box, Flex } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import FinancialAnalysisPage from './pages/FinancialAnalysisPage';
import UploadPage from './pages/UploadPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

const App = () => {
  return (
    <ChakraProvider>
      <Router>
        <Flex direction="column" minH="100vh">
          <Navigation />
          <Box flex="1" p={4}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/financial" element={<FinancialAnalysisPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Box>
        </Flex>
      </Router>
    </ChakraProvider>
  );
};

export default App;
