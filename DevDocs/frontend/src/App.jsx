import React from 'react';
import { ChakraProvider, Box, Flex, VStack, Heading, Text } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import EnhancedProcessingTool from './components/EnhancedProcessingTool';

// Import other components as needed
// import DocumentUploader from './components/DocumentUploader';
// import DocumentViewer from './components/DocumentViewer';
// import FinancialAnalysisDashboard from './components/FinancialAnalysisDashboard';

const Navigation = () => {
  return (
    <Box as="nav" bg="blue.600" color="white" p={4} width="100%">
      <Flex maxW="container.xl" mx="auto" justify="space-between" align="center">
        <Heading size="md">Financial Document Processor</Heading>
        <Flex as="ul" listStyleType="none" gap={6}>
          <Box as="li">
            <Link to="/">Home</Link>
          </Box>
          <Box as="li">
            <Link to="/enhanced">Enhanced Processing</Link>
          </Box>
          {/* Add more navigation items as needed */}
        </Flex>
      </Flex>
    </Box>
  );
};

const Home = () => {
  return (
    <VStack spacing={8} p={8} align="stretch">
      <Heading as="h1" size="xl">Financial Document Processing</Heading>
      <Text>
        Welcome to the Financial Document Processing application. This application helps you process
        financial documents with high accuracy, extract data, and analyze financial information.
      </Text>
      <Box p={6} borderWidth={1} borderRadius="lg" bg="blue.50">
        <Heading as="h2" size="md" mb={4}>Features</Heading>
        <VStack align="start" spacing={3}>
          <Text>✅ Process financial documents with high accuracy</Text>
          <Text>✅ Extract securities, ISINs, and values</Text>
          <Text>✅ Analyze asset allocation</Text>
          <Text>✅ Generate structured data output</Text>
          <Text>✅ Support for multiple languages including Hebrew</Text>
        </VStack>
      </Box>
    </VStack>
  );
};

function App() {
  return (
    <ChakraProvider>
      <Router>
        <Box minH="100vh" bg="gray.50">
          <Navigation />
          <Box maxW="container.xl" mx="auto" p={4}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/enhanced" element={<EnhancedProcessingTool />} />
              {/* Add more routes as needed */}
            </Routes>
          </Box>
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App;
