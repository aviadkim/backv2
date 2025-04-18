import React from 'react';
import { Box, Container, Heading, Text, VStack } from '@chakra-ui/react';
import DocumentProcessor from './components/DocumentProcessor';

function App() {
  return (
    <Box minH="100vh" bg="gray.50">
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          <Box textAlign="center">
            <Heading as="h1" size="2xl" mb={2}>
              Financial Document Processor
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Process financial documents with AI-powered analysis
            </Text>
          </Box>
          
          <DocumentProcessor />
        </VStack>
      </Container>
    </Box>
  );
}

export default App;
