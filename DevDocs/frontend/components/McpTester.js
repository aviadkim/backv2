import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  VStack,
  Heading,
  Text,
  Code,
  useToast,
  Divider,
  Container,
  Card,
  CardHeader,
  CardBody,
  CardFooter
} from '@chakra-ui/react';
import mcpClient from '../utils/mcpClient';

const McpTester = () => {
  const [selectedServer, setSelectedServer] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [params, setParams] = useState('{}');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  // Only show this component in development mode
  if (!mcpClient.isDevelopment) {
    return null;
  }

  const serverOptions = [
    { value: mcpClient.MCP_SERVERS.braveSearch, label: 'Brave Search', methods: ['search'] },
    { value: mcpClient.MCP_SERVERS.github, label: 'GitHub', methods: ['getRepository', 'getIssues', 'getPullRequests'] },
    { value: mcpClient.MCP_SERVERS.sqlite, label: 'SQLite', methods: ['query'] },
    { value: mcpClient.MCP_SERVERS.magic, label: 'Magic', methods: ['generate'] },
    { value: mcpClient.MCP_SERVERS.supabase, label: 'Supabase', methods: ['list_projects', 'query'] },
    { value: mcpClient.MCP_SERVERS.browserTools, label: 'Browser Tools', methods: ['getConsoleLogs', 'getConsoleErrors'] },
    { value: mcpClient.MCP_SERVERS.firecrawl, label: 'Firecrawl', methods: ['firecrawl_scrape'] },
    { value: mcpClient.MCP_SERVERS.puppeteer, label: 'Puppeteer', methods: ['puppeteer_navigate'] },
    { value: mcpClient.MCP_SERVERS.sequentialThinking, label: 'Sequential Thinking', methods: ['solve'] }
  ];

  const getMethodsForServer = (server) => {
    const serverOption = serverOptions.find(option => option.value === server);
    return serverOption ? serverOption.methods : [];
  };

  const handleServerChange = (e) => {
    const server = e.target.value;
    setSelectedServer(server);
    setSelectedMethod('');
  };

  const handleMethodChange = (e) => {
    setSelectedMethod(e.target.value);
  };

  const handleParamsChange = (e) => {
    setParams(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedServer || !selectedMethod) {
      toast({
        title: 'Error',
        description: 'Please select a server and method',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    try {
      setLoading(true);
      const parsedParams = JSON.parse(params);
      const response = await mcpClient.callMcp(selectedServer, selectedMethod, parsedParams);
      setResult(response);
      toast({
        title: 'Success',
        description: 'MCP call completed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error calling MCP:', error);
      setResult({ error: error.message });
      toast({
        title: 'Error',
        description: `Error calling MCP: ${error.message}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTest = async () => {
    try {
      setLoading(true);
      let response;
      
      switch (selectedServer) {
        case mcpClient.MCP_SERVERS.braveSearch:
          response = await mcpClient.searchWeb('FinDoc Analyzer');
          break;
        case mcpClient.MCP_SERVERS.github:
          response = await mcpClient.getGithubRepo('aviadkim', 'backv2');
          break;
        case mcpClient.MCP_SERVERS.sqlite:
          response = await mcpClient.executeSqlQuery('SELECT * FROM sqlite_master');
          break;
        case mcpClient.MCP_SERVERS.supabase:
          response = await mcpClient.listSupabaseProjects();
          break;
        case mcpClient.MCP_SERVERS.browserTools:
          response = await mcpClient.getWebConsoleLogs('https://example.com');
          break;
        case mcpClient.MCP_SERVERS.firecrawl:
          response = await mcpClient.scrapeWebpage('https://example.com');
          break;
        case mcpClient.MCP_SERVERS.puppeteer:
          response = await mcpClient.navigateWithPuppeteer('https://example.com');
          break;
        case mcpClient.MCP_SERVERS.sequentialThinking:
          response = await mcpClient.solveWithSequentialThinking('How to improve financial document analysis?');
          break;
        default:
          throw new Error('Please select a server first');
      }
      
      setResult(response);
      toast({
        title: 'Success',
        description: 'Quick test completed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error in quick test:', error);
      setResult({ error: error.message });
      toast({
        title: 'Error',
        description: `Error in quick test: ${error.message}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="container.lg" py={8}>
      <Card mb={6}>
        <CardHeader>
          <Heading size="lg">MCP Tester (Development Only)</Heading>
          <Text mt={2} color="gray.600">
            Test MCP server functionality during development
          </Text>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl id="server">
              <FormLabel>MCP Server</FormLabel>
              <Select 
                placeholder="Select MCP server" 
                value={selectedServer} 
                onChange={handleServerChange}
              >
                {serverOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl id="method">
              <FormLabel>Method</FormLabel>
              <Select 
                placeholder="Select method" 
                value={selectedMethod} 
                onChange={handleMethodChange}
                isDisabled={!selectedServer}
              >
                {getMethodsForServer(selectedServer).map(method => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl id="params">
              <FormLabel>Parameters (JSON)</FormLabel>
              <Textarea 
                value={params} 
                onChange={handleParamsChange}
                placeholder='{"key": "value"}'
                rows={5}
              />
            </FormControl>
            
            <Box display="flex" justifyContent="space-between">
              <Button 
                colorScheme="blue" 
                onClick={handleSubmit}
                isLoading={loading}
                isDisabled={!selectedServer || !selectedMethod}
              >
                Execute MCP Call
              </Button>
              
              <Button 
                colorScheme="green" 
                onClick={handleQuickTest}
                isLoading={loading}
                isDisabled={!selectedServer}
              >
                Quick Test
              </Button>
            </Box>
          </VStack>
        </CardBody>
      </Card>
      
      {result && (
        <Card>
          <CardHeader>
            <Heading size="md">Result</Heading>
          </CardHeader>
          <CardBody>
            <Box 
              bg="gray.50" 
              p={4} 
              borderRadius="md" 
              overflowX="auto"
            >
              <pre>
                <Code>{JSON.stringify(result, null, 2)}</Code>
              </pre>
            </Box>
          </CardBody>
        </Card>
      )}
    </Container>
  );
};

export default McpTester;
