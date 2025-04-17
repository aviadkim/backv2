import React from 'react';
import FinDocLayout from '../components/FinDocLayout';
import McpTester from '../components/McpTester';
import { Box, Heading, Text, Alert, AlertIcon, AlertTitle, AlertDescription } from '@chakra-ui/react';
import mcpClient from '../utils/mcpClient';

const McpTestPage = () => {
  return (
    <FinDocLayout>
      {mcpClient.isDevelopment ? (
        <McpTester />
      ) : (
        <Box p={8}>
          <Alert status="warning" variant="solid" borderRadius="md">
            <AlertIcon />
            <Box>
              <AlertTitle>Development Mode Only</AlertTitle>
              <AlertDescription>
                The MCP testing functionality is only available in development mode.
              </AlertDescription>
            </Box>
          </Alert>
          
          <Box mt={8} textAlign="center">
            <Heading size="lg">MCP Testing</Heading>
            <Text mt={4}>
              This page allows developers to test MCP server functionality during development.
              To use this feature, please run the application in development mode.
            </Text>
          </Box>
        </Box>
      )}
    </FinDocLayout>
  );
};

export default McpTestPage;
