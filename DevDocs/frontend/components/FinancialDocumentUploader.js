import React, { useState } from 'react';
import {
  Box,
  Button,
  Input,
  Select,
  Text,
  VStack,
  HStack,
  Progress,
  Heading,
  Card,
  CardBody,
  CardHeader,
  Icon
} from '@chakra-ui/react';

// Import components that need to be imported separately



import { FiUpload, FiFile, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import axios from 'axios';
import { FormControl, FormLabel, Divider, useToast } from '../components/chakra-components';

const FinancialDocumentUploader = ({ onDocumentProcessed }) => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('heb+eng');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const toast = useToast();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setResults(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang', language);

    try {
      const response = await axios.post('/api/financial/process-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      setResults(response.data);

      // Call the callback if provided
      if (onDocumentProcessed) {
        onDocumentProcessed(response.data);
      }

      toast({
        title: 'Document processed successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error uploading document:', err);
      setError(err.response?.data?.detail || 'Error processing document');
      toast({
        title: 'Error processing document',
        description: err.response?.data?.detail || 'An error occurred while processing the document',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <Card mt={6} width="100%">
        <CardHeader>
          <Heading size="md">Analysis Results</Heading>
        </CardHeader>
        <CardBody>
          <VStack align="start" spacing={4}>
            <Box>
              <Text fontWeight="bold">File Name:</Text>
              <Text>{results.file_name}</Text>
            </Box>

            {results.detection && (
              <Box width="100%">
                <Text fontWeight="bold">Detected Tables: {results.detection.num_tables}</Text>
                {results.detection.num_tables === 0 && (
                  <Text color="orange.500">No tables detected in the document</Text>
                )}
              </Box>
            )}

            {results.analysis && results.analysis.length > 0 ? (
              <VStack align="start" width="100%" spacing={4}>
                <Text fontWeight="bold">Analysis:</Text>
                {results.analysis.map((item, index) => (
                  <Card key={index} width="100%" variant="outline">
                    <CardHeader>
                      <Heading size="sm">Table {index + 1} ({item.analysis.table_type})</Heading>
                    </CardHeader>
                    <CardBody>
                      <VStack align="start" spacing={2}>
                        {item.analysis.summary && (
                          <Box width="100%">
                            <Text fontWeight="bold">Summary:</Text>
                            <Box pl={4}>
                              {Object.entries(item.analysis.summary).map(([key, value]) => (
                                <Text key={key}>
                                  {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                                </Text>
                              ))}
                            </Box>
                          </Box>
                        )}

                        {item.analysis.securities && item.analysis.securities.length > 0 && (
                          <Box width="100%">
                            <Text fontWeight="bold">Securities ({item.analysis.securities.length}):</Text>
                            <Box pl={4}>
                              {item.analysis.securities.slice(0, 5).map((security, secIndex) => (
                                <Box key={secIndex} mb={2}>
                                  <Text fontWeight="semibold">Security {secIndex + 1}:</Text>
                                  <Box pl={4}>
                                    {Object.entries(security).map(([key, value]) => (
                                      <Text key={key}>
                                        {key}: {value}
                                      </Text>
                                    ))}
                                  </Box>
                                </Box>
                              ))}
                              {item.analysis.securities.length > 5 && (
                                <Text color="blue.500">
                                  ... and {item.analysis.securities.length - 5} more securities
                                </Text>
                              )}
                            </Box>
                          </Box>
                        )}
                      </VStack>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            ) : (
              results.analysis && (
                <Box width="100%">
                  <Text fontWeight="bold">Analysis:</Text>
                  <Card width="100%" variant="outline">
                    <CardHeader>
                      <Heading size="sm">{results.analysis.table_type}</Heading>
                    </CardHeader>
                    <CardBody>
                      <VStack align="start" spacing={2}>
                        {results.analysis.summary && (
                          <Box width="100%">
                            <Text fontWeight="bold">Summary:</Text>
                            <Box pl={4}>
                              {Object.entries(results.analysis.summary).map(([key, value]) => (
                                <Text key={key}>
                                  {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                                </Text>
                              ))}
                            </Box>
                          </Box>
                        )}
                      </VStack>
                    </CardBody>
                  </Card>
                </Box>
              )
            )}
          </VStack>
        </CardBody>
      </Card>
    );
  };

  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Financial Document Analysis</Heading>
        <Text>Upload a financial document to detect tables and analyze the data.</Text>

        <Card width="100%">
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl isRequired>
                <FormLabel>Upload Document</FormLabel>
                <Input
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf,.csv"
                  onChange={handleFileChange}
                  p={1}
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Supported formats: JPG, PNG, PDF, CSV
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>OCR Language</FormLabel>
                <Select value={language} onChange={handleLanguageChange}>
                  <option value="heb+eng">Hebrew + English</option>
                  <option value="eng">English</option>
                  <option value="heb">Hebrew</option>
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Select the language(s) in the document for better OCR results
                </Text>
              </FormControl>

              {file && (
                <HStack width="100%">
                  <Icon as={FiFile} color="blue.500" />
                  <Text>{file.name}</Text>
                </HStack>
              )}

              {error && (
                <HStack width="100%" color="red.500">
                  <Icon as={FiAlertCircle} />
                  <Text>{error}</Text>
                </HStack>
              )}

              <Button
                leftIcon={<FiUpload />}
                colorScheme="blue"
                onClick={handleUpload}
                isLoading={isUploading}
                loadingText="Processing..."
                width="full"
                mt={2}
              >
                Upload & Analyze
              </Button>

              {isUploading && (
                <Box width="100%">
                  <Text mb={2}>Uploading and processing document...</Text>
                  <Progress value={uploadProgress} size="sm" colorScheme="blue" />
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        {renderResults()}
      </VStack>
    </Box>
  );
};

export default FinancialDocumentUploader;
