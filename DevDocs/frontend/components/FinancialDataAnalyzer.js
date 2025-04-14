import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Textarea, 
  Select, 
  Text, 
  VStack, 
  HStack, 
  useToast, 
  Heading,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer
} from '@chakra-ui/react';
import { FiSearch, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';
import axios from 'axios';

const FinancialDataAnalyzer = () => {
  const [tableData, setTableData] = useState('');
  const [tableType, setTableType] = useState('unknown');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  const toast = useToast();
  
  const handleTableDataChange = (e) => {
    setTableData(e.target.value);
    setError(null);
  };
  
  const handleTableTypeChange = (e) => {
    setTableType(e.target.value);
  };
  
  const parseTableData = (data) => {
    try {
      // Try to parse as JSON
      return JSON.parse(data);
    } catch (e) {
      // Try to parse as CSV
      const rows = data.trim().split('\n');
      const headers = rows[0].split(',').map(h => h.trim());
      
      const result = [];
      for (let i = 1; i < rows.length; i++) {
        const values = rows[i].split(',').map(v => v.trim());
        const row = {};
        
        for (let j = 0; j < headers.length; j++) {
          row[headers[j]] = values[j];
        }
        
        result.push(row);
      }
      
      return result;
    }
  };
  
  const handleAnalyze = async () => {
    if (!tableData) {
      setError('Please enter table data');
      return;
    }
    
    setIsAnalyzing(true);
    setResults(null);
    setError(null);
    
    try {
      // Parse the table data
      const parsedData = parseTableData(tableData);
      
      // Send the data for analysis
      const response = await axios.post('/api/financial/analyze-data', {
        table_data: parsedData,
        table_type: tableType
      });
      
      setResults(response.data);
      toast({
        title: 'Data analyzed successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error analyzing data:', err);
      setError(err.response?.data?.detail || 'Error analyzing data');
      toast({
        title: 'Error analyzing data',
        description: err.response?.data?.detail || 'An error occurred while analyzing the data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
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
              <Text fontWeight="bold">Table Type:</Text>
              <Text>{results.table_type}</Text>
            </Box>
            
            {results.summary && (
              <Box width="100%">
                <Text fontWeight="bold">Summary:</Text>
                <Box pl={4}>
                  {Object.entries(results.summary).map(([key, value]) => (
                    <Text key={key}>
                      {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                    </Text>
                  ))}
                </Box>
              </Box>
            )}
            
            {results.securities && results.securities.length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Securities ({results.securities.length}):</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        {Object.keys(results.securities[0]).map(key => (
                          <Th key={key}>{key}</Th>
                        ))}
                      </Tr>
                    </Thead>
                    <Tbody>
                      {results.securities.map((security, index) => (
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
            
            {results.assets && Object.keys(results.assets).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Assets:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.assets).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {results.liabilities && Object.keys(results.liabilities).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Liabilities:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.liabilities).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {results.equity && Object.keys(results.equity).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Equity:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.equity).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {results.revenues && Object.keys(results.revenues).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Revenues:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.revenues).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {results.expenses && Object.keys(results.expenses).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Expenses:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.expenses).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {results.profits && Object.keys(results.profits).length > 0 && (
              <Box width="100%">
                <Text fontWeight="bold">Profits:</Text>
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Item</Th>
                        <Th>Value</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(results.profits).map(([key, value]) => (
                        <Tr key={key}>
                          <Td>{key}</Td>
                          <Td>{value}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
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
        <Heading size="lg">Financial Data Analysis</Heading>
        <Text>Enter financial table data to analyze.</Text>
        
        <Card width="100%">
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl isRequired>
                <FormLabel>Table Data</FormLabel>
                <Textarea
                  value={tableData}
                  onChange={handleTableDataChange}
                  placeholder="Enter table data in CSV or JSON format"
                  rows={10}
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Enter data in CSV format (comma-separated values) or JSON format
                </Text>
              </FormControl>
              
              <FormControl>
                <FormLabel>Table Type</FormLabel>
                <Select value={tableType} onChange={handleTableTypeChange}>
                  <option value="unknown">Auto-detect</option>
                  <option value="portfolio">Portfolio</option>
                  <option value="balance_sheet">Balance Sheet</option>
                  <option value="income_statement">Income Statement</option>
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Select the type of financial table or let the system auto-detect
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
                onClick={handleAnalyze}
                isLoading={isAnalyzing}
                loadingText="Analyzing..."
                width="full"
                mt={2}
              >
                Analyze Data
              </Button>
            </VStack>
          </CardBody>
        </Card>
        
        {renderResults()}
      </VStack>
    </Box>
  );
};

export default FinancialDataAnalyzer;
