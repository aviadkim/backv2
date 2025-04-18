import React from 'react';
import Layout from '../components/Layout';
import { Box, Heading, Text, SimpleGrid, Flex, Icon, Button } from '@chakra-ui/react';
import { FiFileText, FiBriefcase, FiSearch, FiBarChart2 } from 'react-icons/fi';
import Link from 'next/link';

export default function Home() {
  return (
    <Layout>
      <Box p={5}>
        <Heading as="h1" size="xl" mb={2}>Financial Document Dashboard</Heading>
        <Text color="gray.600" mb={6}>
          Welcome to the FinDoc Analyzer dashboard. Here you can manage and analyze your financial documents.
        </Text>
        
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={6}>
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="white">
            <Flex justify="space-between" align="center" mb={3}>
              <Heading as="h2" size="md">Recent Documents</Heading>
              <Icon as={FiFileText} boxSize={6} color="blue.500" />
            </Flex>
            <Text mb={4}>You have 3 recently processed documents.</Text>
            <Link href="/documents" passHref>
              <Button as="a" colorScheme="blue" variant="link">View All Documents</Button>
            </Link>
          </Box>
          
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="white">
            <Flex justify="space-between" align="center" mb={3}>
              <Heading as="h2" size="md">Portfolio Summary</Heading>
              <Icon as={FiBriefcase} boxSize={6} color="blue.500" />
            </Flex>
            <Text mb={4}>Total portfolio value: $19,510,599</Text>
            <Link href="/portfolio" passHref>
              <Button as="a" colorScheme="blue" variant="link">View Portfolio</Button>
            </Link>
          </Box>
          
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="white">
            <Flex justify="space-between" align="center" mb={3}>
              <Heading as="h2" size="md">Document Analysis</Heading>
              <Icon as={FiSearch} boxSize={6} color="blue.500" />
            </Flex>
            <Text mb={4}>Run analysis on your financial documents.</Text>
            <Link href="/analysis" passHref>
              <Button as="a" colorScheme="blue" variant="link">Start Analysis</Button>
            </Link>
          </Box>
          
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="white">
            <Flex justify="space-between" align="center" mb={3}>
              <Heading as="h2" size="md">Data Export</Heading>
              <Icon as={FiBarChart2} boxSize={6} color="blue.500" />
            </Flex>
            <Text mb={4}>Export your financial data in various formats.</Text>
            <Link href="/export" passHref>
              <Button as="a" colorScheme="blue" variant="link">Export Data</Button>
            </Link>
          </Box>
        </SimpleGrid>
      </Box>
    </Layout>
  );
}
