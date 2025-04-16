import React, { useState } from 'react';
import {
  Box,
  Button,
  Input,
  Textarea,
  Text,
  VStack,
  HStack,
  Heading,
  Card,
  CardBody,
  CardHeader,
  Iconle,
  Code,
  Badge
} from '@chakra-ui/react';

// Import components that need to be imported separately




// Create custom table components
const TableContainer = ({ children, ...props }) => (
  <Box overflowX="auto" {...props}>
    {children}
  </Box>
);

const Thead = ({ children, ...props }) => (
  <Box as="thead" {...props}>
    {children}
  </Box>
);

const Tbody = ({ children, ...props }) => (
  <Box as="tbody" {...props}>
    {children}
  </Box>
);

const Tr = ({ children, ...props }) => (
  <Box as="tr" display="table-row" {...props}>
    {children}
  </Box>
);

const Th = ({ children, ...props }) => (
  <Box
    as="th"
    px="4"
    py="2"
    borderBottom="1px"
    borderColor="gray.200"
    textAlign="left"
    fontWeight="bold"
    {...props}
  >
    {children}
  </Box>
);

const Td = ({ children, ...props }) => (
  <Box
    as="td"
    px="4"
    py="2"
    borderBottom="1px"
    borderColor="gray.200"
    {...props}
  >
    {children}
  </Box>
);
import { FiSearch, FiAlertCircle, FiCheckCircle, FiHelpCircle } from 'react-icons/fi';
import axios from 'axios';
import { FormControl, FormLabel, Divider, useToast } from '../components/chakra-components';

const FinancialQueryEngine = ({ documentData }) => {
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [sampleQueries, setSampleQueries] = useState([
    "What is the total value of the portfolio?",
    "What securities are in the portfolio?",
    "What is the document date?",
    "Show me information about the balance sheet",
    "What is the return on Apple stock?",
    "How many tables are in the document?"
  ]);

  const toast = useToast();

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
    setError(null);
  };

  const handleSampleQuery = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    if (!documentData) {
      setError('No document data available. Please upload and process a document first.');
      return;
    }

    setIsQuerying(true);
    setResults(null);
    setError(null);

    try {
      // Send the query to the API
      const response = await axios.post('/api/financial/query', {
        query: query,
        document_data: documentData
      });

      setResults(response.data);
      toast({
        title: 'Query processed successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error processing query:', err);
      setError(err.response?.data?.detail || 'Error processing query');
      toast({
        title: 'Error processing query',
        description: err.response?.data?.detail || 'An error occurred while processing the query',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsQuerying(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <Card mt={6} width="100%">
        <CardHeader>
          <Heading size="md">Query Results</Heading>
          <Badge colorScheme="blue" ml={2}>{results.query_type}</Badge>
        </CardHeader>
        <CardBody>
          <VStack align="start" spacing={4}>
            <Box width="100%">
              <Text fontWeight="bold">Answer:</Text>
              <Text whiteSpace="pre-line">{results.answer}</Text>
            </Box>

            <Divider />

            {results.data && Object.keys(results.data).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Data:</Text>

                {results.data.securities && results.data.securities.length > 0 && (
                  <Box mt={4} width="100%">
                    <Text fontWeight="semibold">Securities:</Text>
                    <TableContainer>
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            {Object.keys(results.data.securities[0]).map(key => (
                              <Th key={key}>{key}</Th>
                            ))}
                          </Tr>
                        </Thead>
                        <Tbody>
                          {results.data.securities.map((security, index) => (
                            <Tr key={index}>
                              {Object.values(security).map((value, i) => (
                                <Td key={i}>{typeof value === 'object' ? JSON.stringify(value) : value}</Td>
                              ))}
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}

                {results.data.returns && results.data.returns.length > 0 && (
                  <Box mt={4} width="100%">
                    <Text fontWeight="semibold">Returns:</Text>
                    <TableContainer>
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            {Object.keys(results.data.returns[0]).map(key => (
                              <Th key={key}>{key}</Th>
                            ))}
                          </Tr>
                        </Thead>
                        <Tbody>
                          {results.data.returns.map((returnItem, index) => (
                            <Tr key={index}>
                              {Object.values(returnItem).map((value, i) => (
                                <Td key={i}>{typeof value === 'object' ? JSON.stringify(value) : value}</Td>
                              ))}
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}

                {results.data.security && (
                  <Box mt={4} width="100%">
                    <Text fontWeight="semibold">Security Details:</Text>
                    <TableContainer>
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th>Property</Th>
                            <Th>Value</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {Object.entries(results.data.security).map(([key, value]) => (
                            <Tr key={key}>
                              <Td>{key}</Td>
                              <Td>{typeof value === 'object' ? JSON.stringify(value) : value}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}

                {/* Display other simple data */}
                {Object.entries(results.data).map(([key, value]) => {
                  // Skip arrays and objects that we've already rendered
                  if (
                    key === 'securities' ||
                    key === 'returns' ||
                    key === 'security' ||
                    Array.isArray(value) ||
                    (typeof value === 'object' && value !== null && Object.keys(value).length > 0)
                  ) {
                    return null;
                  }

                  return (
                    <Box key={key} mt={2}>
                      <Text>
                        <strong>{key}:</strong> {value}
                      </Text>
                    </Box>
                  );
                })}

                {/* Display nested objects */}
                {Object.entries(results.data).map(([key, value]) => {
                  if (
                    key !== 'securities' &&
                    key !== 'returns' &&
                    key !== 'security' &&
                    !Array.isArray(value) &&
                    typeof value === 'object' &&
                    value !== null &&
                    Object.keys(value).length > 0
                  ) {
                    return (
                      <Box key={key} mt={4} width="100%">
                        <Text fontWeight="semibold">{key}:</Text>
                        <TableContainer>
                          <Table variant="simple" size="sm">
                            <Thead>
                              <Tr>
                                <Th>Property</Th>
                                <Th>Value</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {Object.entries(value).map(([subKey, subValue]) => (
                                <Tr key={subKey}>
                                  <Td>{subKey}</Td>
                                  <Td>{typeof subValue === 'object' ? JSON.stringify(subValue) : subValue}</Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      </Box>
                    );
                  }
                  return null;
                })}
              </Box>
            )}
          </VStack>
        </CardBody>
      </Card>
    );
  };

  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Financial Document Query Engine</Heading>
        <Text>Ask questions about your financial documents in natural language.</Text>

        <Card width="100%">
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl isRequired>
                <FormLabel>Your Question</FormLabel>
                <Textarea
                  value={query}
                  onChange={handleQueryChange}
                  placeholder="Ask a question about your financial document..."
                  rows={3}
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Example: "What is the total value of the portfolio?" or "What securities are in the document?"
                </Text>
              </FormControl>

              {error && (
                <HStack width="100%" color="red.500">
                  <Icon as={FiAlertCircle} />
                  <Text>{error}</Text>
                </HStack>
              )}

              <Button
                leftIcon={<FiSearch />}
                colorScheme="blue"
                onClick={handleSubmit}
                isLoading={isQuerying}
                loadingText="Processing..."
                width="full"
                mt={2}
                isDisabled={!documentData}
              >
                Ask Question
              </Button>

              {!documentData && (
                <HStack width="100%" color="orange.500">
                  <Icon as={FiHelpCircle} />
                  <Text>Please upload and process a document first to use the query engine.</Text>
                </HStack>
              )}
            </VStack>
          </CardBody>
        </Card>

        <Card width="100%">
          <CardHeader>
            <Heading size="sm">Sample Questions</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={2}>
              {sampleQueries.map((sampleQuery, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSampleQuery(sampleQuery)}
                  isDisabled={!documentData}
                >
                  {sampleQuery}
                </Button>
              ))}
            </VStack>
          </CardBody>
        </Card>

        {renderResults()}
      </VStack>
    </Box>
  );
};

export default FinancialQueryEngine;
