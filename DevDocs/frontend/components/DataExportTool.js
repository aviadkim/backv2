import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Select, 
  Input, 
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
  Radio,
  RadioGroup,
  Stack,
  Badge,
  Link,
  Code,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Flex,
  Spacer
} from '@chakra-ui/react';
import { 
  FiDownload, 
  FiFile, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiFileText,
  FiDatabase,
  FiList
} from 'react-icons/fi';
import axios from 'axios';

const DataExportTool = ({ documentData }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');
  const [exportType, setExportType] = useState('raw');
  const [filename, setFilename] = useState('');
  const [exportResult, setExportResult] = useState(null);
  const [error, setError] = useState(null);
  
  const toast = useToast();
  
  const handleExport = async () => {
    if (!documentData) {
      setError('No document data available. Please upload and process a document first.');
      return;
    }
    
    setIsExporting(true);
    setError(null);
    setExportResult(null);
    
    try {
      // Generate filename if not provided
      const actualFilename = filename || `export_${new Date().toISOString().replace(/[:.]/g, '-')}`;
      
      // Send the export request to the API
      const response = await axios.post('/api/financial/export', {
        data: documentData,
        format_type: exportFormat,
        filename: actualFilename,
        export_type: exportType
      });
      
      setExportResult(response.data);
      toast({
        title: 'Export successful',
        description: `Data exported to ${response.data.filepath}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error exporting data:', err);
      setError(err.response?.data?.detail || 'Error exporting data');
      toast({
        title: 'Export failed',
        description: err.response?.data?.detail || 'An error occurred while exporting data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsExporting(false);
    }
  };
  
  const getFormatIcon = (format) => {
    switch (format) {
      case 'json':
        return <Icon as={FiDatabase} />;
      case 'csv':
        return <Icon as={FiFileText} />;
      case 'excel':
        return <Icon as={FiFile} />;
      case 'xml':
        return <Icon as={FiList} />;
      default:
        return <Icon as={FiFile} />;
    }
  };
  
  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Data Export Tool</Heading>
        <Text>Export your financial document data to various formats for use in other systems.</Text>
        
        <Card width="100%">
          <CardHeader>
            <Heading size="md">Export Options</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl>
                <FormLabel>Export Format</FormLabel>
                <Select 
                  value={exportFormat} 
                  onChange={(e) => setExportFormat(e.target.value)}
                >
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="excel">Excel</option>
                  <option value="xml">XML</option>
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Select the format for the exported data
                </Text>
              </FormControl>
              
              <FormControl>
                <FormLabel>Export Type</FormLabel>
                <RadioGroup value={exportType} onChange={setExportType}>
                  <Stack direction="column" spacing={2}>
                    <Radio value="raw">
                      <HStack>
                        <Text>Raw Data</Text>
                        <Badge colorScheme="blue">Complete</Badge>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">Export all document data</Text>
                    </Radio>
                    <Radio value="portfolio_summary">
                      <HStack>
                        <Text>Portfolio Summary</Text>
                        <Badge colorScheme="green">Focused</Badge>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">Export only portfolio summary data</Text>
                    </Radio>
                    <Radio value="isin_list">
                      <HStack>
                        <Text>ISIN List</Text>
                        <Badge colorScheme="purple">Compact</Badge>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">Export only ISIN entities</Text>
                    </Radio>
                  </Stack>
                </RadioGroup>
              </FormControl>
              
              <FormControl>
                <FormLabel>Filename (Optional)</FormLabel>
                <Input 
                  value={filename} 
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="Leave blank for auto-generated filename"
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  The extension will be added automatically based on the format
                </Text>
              </FormControl>
              
              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>Export Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <Button
                leftIcon={<FiDownload />}
                colorScheme="blue"
                onClick={handleExport}
                isLoading={isExporting}
                loadingText="Exporting..."
                width="full"
                mt={2}
                isDisabled={!documentData}
              >
                Export Data
              </Button>
              
              {!documentData && (
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>No Data Available</AlertTitle>
                  <AlertDescription>
                    Please upload and process a document first to export data.
                  </AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
        
        {exportResult && (
          <Card width="100%" colorScheme="green" variant="outline" borderColor="green.200">
            <CardHeader bg="green.50">
              <Flex align="center">
                <Icon as={FiCheckCircle} color="green.500" boxSize={5} mr={2} />
                <Heading size="md">Export Successful</Heading>
                <Spacer />
                <Badge colorScheme="green">{exportResult.format}</Badge>
              </Flex>
            </CardHeader>
            <CardBody>
              <VStack align="start" spacing={3}>
                <HStack>
                  <Text fontWeight="bold">Status:</Text>
                  <Text>{exportResult.status}</Text>
                </HStack>
                
                <HStack>
                  <Text fontWeight="bold">Export Type:</Text>
                  <Badge>{exportResult.export_type}</Badge>
                </HStack>
                
                <HStack>
                  <Text fontWeight="bold">File Path:</Text>
                  <Code p={2} borderRadius="md">{exportResult.filepath}</Code>
                </HStack>
                
                <Text>
                  Your data has been exported successfully. You can find the file at the path above.
                </Text>
                
                <Divider />
                
                <HStack>
                  <Icon as={getFormatIcon(exportResult.format)} />
                  <Text>
                    Format: <strong>{exportResult.format.toUpperCase()}</strong>
                  </Text>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default DataExportTool;
