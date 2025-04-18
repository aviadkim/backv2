import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Container,
  Divider,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Progress,
  SimpleGrid,
  Spinner,
  Stack,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Image,
  Badge,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { FiUpload, FiDownload, FiBarChart2, FiList, FiPieChart, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

const DocumentProcessor = () => {
  const [file, setFile] = useState(null);
  const [languages, setLanguages] = useState('eng,heb');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  
  const toast = useToast();
  const { isOpen: isSecuritiesOpen, onOpen: onSecuritiesOpen, onClose: onSecuritiesClose } = useDisclosure();
  const { isOpen: isVisualizationsOpen, onOpen: onVisualizationsOpen, onClose: onVisualizationsClose } = useDisclosure();
  
  const [visualizations, setVisualizations] = useState([]);
  
  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);
  
  // Handle file change
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      toast({
        title: 'No file selected',
        description: 'Please select a PDF file to process',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    
    try {
      setIsProcessing(true);
      setProgress(0);
      setResult(null);
      setError(null);
      
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      formData.append('languages', languages);
      
      // Upload file and start processing
      const response = await fetch(`${API_URL}/api/process`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Failed to process document: ${response.statusText}`);
      }
      
      const data = await response.json();
      setTaskId(data.task_id);
      
      // Start polling for status
      const interval = setInterval(() => {
        checkStatus(data.task_id);
      }, 2000);
      
      setPollingInterval(interval);
    } catch (err) {
      setError(err.message);
      setIsProcessing(false);
      
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  // Check processing status
  const checkStatus = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/status/${id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get status: ${response.statusText}`);
      }
      
      const data = await response.json();
      setProgress(data.progress * 100);
      
      if (data.status === 'completed') {
        clearInterval(pollingInterval);
        setPollingInterval(null);
        getResult(id);
      } else if (data.status === 'failed') {
        clearInterval(pollingInterval);
        setPollingInterval(null);
        setIsProcessing(false);
        setError(data.error || 'Processing failed');
        
        toast({
          title: 'Processing failed',
          description: data.error || 'An error occurred during processing',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (err) {
      console.error('Error checking status:', err);
    }
  };
  
  // Get processing result
  const getResult = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/result/${id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get result: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResult(data);
      setIsProcessing(false);
      
      toast({
        title: 'Processing complete',
        description: `Extracted ${data.metrics.total_securities} securities with total value ${data.portfolio.total_value.toLocaleString()} ${data.portfolio.currency}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      setError(err.message);
      setIsProcessing(false);
      
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  // Get visualizations
  const getVisualizations = async () => {
    if (!taskId) return;
    
    try {
      const response = await fetch(`${API_URL}/api/visualizations/${taskId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get visualizations: ${response.statusText}`);
      }
      
      const data = await response.json();
      setVisualizations(data.files);
      onVisualizationsOpen();
    } catch (err) {
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  // Download result as JSON
  const downloadJson = () => {
    if (!result) return;
    
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.document_info.document_id}_processed.json`;
    a.click();
    
    URL.revokeObjectURL(url);
  };
  
  // Format currency
  const formatCurrency = (value, currency) => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    return `${value.toLocaleString()} ${currency}`;
  };
  
  // Format percentage
  const formatPercentage = (value) => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    return `${(value * 100).toFixed(2)}%`;
  };
  
  // Format key
  const formatKey = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };
  
  return (
    <Container maxW="container.xl" py={8}>
      <Heading as="h1" mb={8} textAlign="center">
        Financial Document Processor
      </Heading>
      
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        {/* Upload Form */}
        <Card>
          <CardHeader>
            <Heading size="md">Upload Document</Heading>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit}>
              <Stack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>PDF Document</FormLabel>
                  <Input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    p={1}
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Languages</FormLabel>
                  <Input
                    type="text"
                    value={languages}
                    onChange={(e) => setLanguages(e.target.value)}
                    placeholder="eng,heb"
                  />
                </FormControl>
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  leftIcon={<FiUpload />}
                  isLoading={isProcessing}
                  loadingText="Processing..."
                  isDisabled={!file || isProcessing}
                >
                  Process Document
                </Button>
              </Stack>
            </form>
            
            {isProcessing && (
              <Box mt={6}>
                <Text mb={2}>Processing: {Math.round(progress)}%</Text>
                <Progress value={progress} size="sm" colorScheme="blue" />
              </Box>
            )}
            
            {error && (
              <Box mt={6} p={4} bg="red.50" borderRadius="md">
                <Flex align="center">
                  <FiAlertCircle color="red" />
                  <Text ml={2} color="red.500">{error}</Text>
                </Flex>
              </Box>
            )}
          </CardBody>
        </Card>
        
        {/* Results */}
        {result && (
          <Card>
            <CardHeader>
              <Heading size="md">Results</Heading>
            </CardHeader>
            <CardBody>
              <Stack spacing={6}>
                <Box>
                  <Heading size="sm" mb={2}>Document Information</Heading>
                  <Table size="sm" variant="simple">
                    <Tbody>
                      <Tr>
                        <Th>Document Name</Th>
                        <Td>{result.document_info.document_name}</Td>
                      </Tr>
                      <Tr>
                        <Th>Document Date</Th>
                        <Td>{result.document_info.document_date}</Td>
                      </Tr>
                      <Tr>
                        <Th>Processing Date</Th>
                        <Td>{result.document_info.processing_date}</Td>
                      </Tr>
                      <Tr>
                        <Th>Processing Time</Th>
                        <Td>{result.document_info.processing_time.toFixed(2)} seconds</Td>
                      </Tr>
                    </Tbody>
                  </Table>
                </Box>
                
                <Divider />
                
                <Box>
                  <Heading size="sm" mb={2}>Portfolio Summary</Heading>
                  <Table size="sm" variant="simple">
                    <Tbody>
                      <Tr>
                        <Th>Total Value</Th>
                        <Td>{formatCurrency(result.portfolio.total_value, result.portfolio.currency)}</Td>
                      </Tr>
                      <Tr>
                        <Th>Currency</Th>
                        <Td>{result.portfolio.currency}</Td>
                      </Tr>
                      <Tr>
                        <Th>Securities</Th>
                        <Td>{result.metrics.total_securities}</Td>
                      </Tr>
                      <Tr>
                        <Th>Asset Classes</Th>
                        <Td>{result.metrics.total_asset_classes}</Td>
                      </Tr>
                    </Tbody>
                  </Table>
                </Box>
                
                <Divider />
                
                <Box>
                  <Heading size="sm" mb={2}>Asset Allocation</Heading>
                  <Table size="sm" variant="simple">
                    <Thead>
                      <Tr>
                        <Th>Asset Class</Th>
                        <Th>Value</Th>
                        <Th>Weight</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(result.portfolio.asset_allocation).map(([assetClass, allocation]) => (
                        <Tr key={assetClass}>
                          <Td>{assetClass}</Td>
                          <Td>{allocation.value ? formatCurrency(allocation.value, result.portfolio.currency) : 'N/A'}</Td>
                          <Td>{allocation.weight ? formatPercentage(allocation.weight) : 'N/A'}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </Box>
                
                {result.accuracy && (
                  <>
                    <Divider />
                    
                    <Box>
                      <Heading size="sm" mb={2}>Accuracy</Heading>
                      <Stack spacing={2}>
                        {Object.entries(result.accuracy).map(([key, value]) => (
                          <Flex key={key} align="center">
                            <Text width="150px" fontWeight="bold">{formatKey(key)}</Text>
                            <Text width="80px" textAlign="right">{formatPercentage(value)}</Text>
                            <Box
                              ml={2}
                              height="10px"
                              width={`${value * 100}px`}
                              bg="blue.500"
                              borderRadius="full"
                            />
                          </Flex>
                        ))}
                      </Stack>
                    </Box>
                  </>
                )}
                
                <Divider />
                
                <Flex justify="space-between">
                  <Button
                    leftIcon={<FiList />}
                    colorScheme="teal"
                    onClick={onSecuritiesOpen}
                  >
                    View Securities
                  </Button>
                  
                  <Button
                    leftIcon={<FiBarChart2 />}
                    colorScheme="purple"
                    onClick={getVisualizations}
                  >
                    View Visualizations
                  </Button>
                  
                  <Button
                    leftIcon={<FiDownload />}
                    colorScheme="gray"
                    onClick={downloadJson}
                  >
                    Download JSON
                  </Button>
                </Flex>
              </Stack>
            </CardBody>
          </Card>
        )}
      </SimpleGrid>
      
      {/* Securities Modal */}
      <Modal isOpen={isSecuritiesOpen} onClose={onSecuritiesClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Securities</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Box overflowX="auto">
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>ISIN</Th>
                    <Th>Name</Th>
                    <Th>Quantity</Th>
                    <Th>Price</Th>
                    <Th>Value</Th>
                    <Th>Currency</Th>
                    <Th>Asset Class</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {result?.portfolio.securities.map((security) => (
                    <Tr key={security.isin}>
                      <Td>{security.isin}</Td>
                      <Td>{security.name}</Td>
                      <Td>{security.quantity ? security.quantity.toLocaleString() : 'N/A'}</Td>
                      <Td>{security.price ? security.price.toLocaleString() : 'N/A'}</Td>
                      <Td>{security.value ? security.value.toLocaleString() : 'N/A'}</Td>
                      <Td>{security.currency || 'N/A'}</Td>
                      <Td>
                        <Badge colorScheme={
                          security.asset_class === 'Equities' ? 'green' :
                          security.asset_class === 'Bonds' ? 'blue' :
                          security.asset_class === 'Liquidity' ? 'gray' :
                          security.asset_class === 'Structured products' ? 'purple' :
                          'orange'
                        }>
                          {security.asset_class}
                        </Badge>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onSecuritiesClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Visualizations Modal */}
      <Modal isOpen={isVisualizationsOpen} onClose={onVisualizationsClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Visualizations</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {visualizations.length > 0 ? (
              <Tabs isFitted variant="enclosed">
                <TabList>
                  {visualizations.map((viz, index) => (
                    <Tab key={index}>Visualization {index + 1}</Tab>
                  ))}
                </TabList>
                <TabPanels>
                  {visualizations.map((viz, index) => (
                    <TabPanel key={index}>
                      <Box textAlign="center">
                        <Image src={`${API_URL}${viz}`} alt={`Visualization ${index + 1}`} mx="auto" />
                      </Box>
                    </TabPanel>
                  ))}
                </TabPanels>
              </Tabs>
            ) : (
              <Text>No visualizations available</Text>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onVisualizationsClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default DocumentProcessor;
