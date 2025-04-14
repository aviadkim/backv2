import React from 'react';
import { Box, Heading, Text } from '@chakra-ui/react';
import FinancialDocumentUploader from '../components/FinancialDocumentUploader';

const UploadPage = () => {
  return (
    <Box>
      <Heading mb={6}>Upload Documents</Heading>
      <Text mb={6}>Upload financial documents for processing and analysis.</Text>
      
      <FinancialDocumentUploader />
    </Box>
  );
};

export default UploadPage;
