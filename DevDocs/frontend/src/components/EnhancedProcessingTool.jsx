import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Progress,
  Select,
  Text,
  VStack,
  HStack,
  useToast,
  Code,
  Badge,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { FiUpload, FiDownload, FiCheck, FiX } from 'react-icons/fi';

const EnhancedProcessingTool = () => {
  const [file, setFile] = useState(null);
  const [languages, setLanguages] = useState(['eng', 'heb']);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const toast = useToast();
  const statusCheckInterval = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a valid PDF file');
      toast({
        title: 'Invalid file',
        description: 'Please select a valid PDF file',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleLanguageChange = (e) => {
    const value = Array.from(e.target.selectedOptions, (option) => option.value);
    setLanguages(value);
  };

  const handleProcessClick = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      languages.forEach(lang => {
        formData.append('languages', lang);
      });

      const response = await fetch('/api/enhanced/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setTaskId(data.task_id);

      // Start polling for status
      statusCheckInterval.current = setInterval(() => {
        checkStatus(data.task_id);
      }, 2000);
    } catch (err) {
      setError(err.message);
      setIsProcessing(false);
      toast({
        title: 'Processing failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const checkStatus = async (id) => {
    try {
      const response = await fetch(`/api/enhanced/status/${id}`);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setProgress(data.progress * 100);

      if (data.status === 'completed') {
        clearInterval(statusCheckInterval.current);
        setIsProcessing(false);
        
        // Fetch the result
        const resultResponse = await fetch(`/api/enhanced/result/${id}`);
        if (resultResponse.ok) {
          const resultData = await resultResponse.json();
          setResult(resultData);
          toast({
            title: 'Processing complete',
            description: `Successfully processed ${file.name}`,
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
        }
      } else if (data.status === 'failed') {
        clearInterval(statusCheckInterval.current);
        setIsProcessing(false);
        setError(data.error || 'Processing failed');
        toast({
          title: 'Processing failed',
          description: data.error || 'Unknown error',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (err) {
      console.error('Error checking status:', err);
    }
  };

  const handleDownloadResult = () => {
    if (!result) return;

    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file.name.replace('.pdf', '')}_processed.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderResultSummary = () => {
    if (!result) return null;

    const securities = result.portfolio?.securities || [];
    const assetAllocation = result.portfolio?.asset_allocation || {};
    const totalValue = result.portfolio?.total_value;
    const currency = result.portfolio?.currency;

    return (
      <Box mt={4} p={4} borderWidth={1} borderRadius="md" bg="gray.50">
        <Heading size="md" mb={2}>Processing Results</Heading>
        
        <HStack spacing={4} mb={2}>
          <Badge colorScheme="blue" p={2} borderRadius="md">
            {securities.length} Securities
          </Badge>
          <Badge colorScheme="green" p={2} borderRadius="md">
            {Object.keys(assetAllocation).length} Asset Classes
          </Badge>
          <Badge colorScheme="purple" p={2} borderRadius="md">
            {totalValue?.toLocaleString()} {currency}
          </Badge>
        </HStack>

        <Accordion allowToggle mt={4}>
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box flex="1" textAlign="left">
                  Securities
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4} maxH="300px" overflowY="auto">
              {securities.map((security, index) => (
                <Box key={index} p={2} mb={2} borderWidth={1} borderRadius="md" bg="white">
                  <Text fontWeight="bold">{security.name || 'Unnamed Security'}</Text>
                  <Text fontSize="sm">ISIN: {security.isin}</Text>
                  {security.value && (
                    <Text fontSize="sm">
                      {security.quantity?.toLocaleString() || '?'} × {security.price?.toLocaleString() || '?'} = {security.value?.toLocaleString() || '?'} {security.currency}
                    </Text>
                  )}
                  {security.asset_class && (
                    <Badge mt={1} colorScheme="teal">{security.asset_class}</Badge>
                  )}
                </Box>
              ))}
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box flex="1" textAlign="left">
                  Asset Allocation
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              {Object.entries(assetAllocation).map(([assetClass, data], index) => (
                <Box key={index} p={2} mb={2} borderWidth={1} borderRadius="md" bg="white">
                  <Text fontWeight="bold">{assetClass}</Text>
                  <Text fontSize="sm">
                    {data.value?.toLocaleString() || '?'} {currency} ({(data.weight * 100).toFixed(2)}%)
                  </Text>
                </Box>
              ))}
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box flex="1" textAlign="left">
                  Raw JSON
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              <Box maxH="300px" overflowY="auto">
                <Code p={2} w="100%" display="block" whiteSpace="pre" fontSize="xs">
                  {JSON.stringify(result, null, 2)}
                </Code>
              </Box>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>

        <Button 
          mt={4} 
          leftIcon={<FiDownload />} 
          colorScheme="blue" 
          onClick={handleDownloadResult}
        >
          Download JSON
        </Button>
      </Box>
    );
  };

  return (
    <Container maxW="container.lg" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading as="h1" size="xl" textAlign="center">
          Enhanced Financial Document Processing
        </Heading>
        
        <Text textAlign="center" color="gray.600">
          Process financial documents with high accuracy using our enhanced processing pipeline.
        </Text>

        <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="md">
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Upload PDF Document</FormLabel>
              <Input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                ref={fileInputRef}
                display="none"
              />
              <Button
                leftIcon={<FiUpload />}
                onClick={() => fileInputRef.current.click()}
                w="100%"
                h="60px"
                variant={file ? "solid" : "outline"}
                colorScheme={file ? "green" : "blue"}
              >
                {file ? (
                  <Flex align="center">
                    <FiCheck mr={2} />
                    <Text>{file.name}</Text>
                  </Flex>
                ) : (
                  "Select PDF File"
                )}
              </Button>
              {error && (
                <Text color="red.500" mt={2} fontSize="sm">
                  {error}
                </Text>
              )}
            </FormControl>

            <FormControl>
              <FormLabel>Languages</FormLabel>
              <Select 
                multiple 
                value={languages} 
                onChange={handleLanguageChange}
                h="100px"
              >
                <option value="eng">English</option>
                <option value="heb">Hebrew</option>
                <option value="ara">Arabic</option>
                <option value="fra">French</option>
                <option value="deu">German</option>
                <option value="spa">Spanish</option>
                <option value="rus">Russian</option>
              </Select>
            </FormControl>

            <Button
              colorScheme="blue"
              size="lg"
              onClick={handleProcessClick}
              isLoading={isProcessing}
              loadingText="Processing..."
              isDisabled={!file || isProcessing}
            >
              Process Document
            </Button>

            {isProcessing && (
              <Box>
                <Text mb={2}>Processing... {Math.round(progress)}%</Text>
                <Progress value={progress} size="sm" colorScheme="blue" />
              </Box>
            )}

            {result && renderResultSummary()}
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default EnhancedProcessingTool;
