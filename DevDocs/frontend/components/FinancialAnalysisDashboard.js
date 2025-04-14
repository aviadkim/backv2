import React, { useState, useEffect } from 'react';
import { 
  Box, 
  SimpleGrid, 
  Heading, 
  Text, 
  Stat, 
  StatLabel, 
  StatNumber, 
  StatHelpText, 
  StatArrow, 
  Card, 
  CardBody, 
  CardHeader,
  Button,
  Icon,
  Flex,
  Divider,
  Progress,
  useColorModeValue,
  VStack,
  HStack
} from '@chakra-ui/react';
import { FiFileText, FiPieChart, FiDollarSign, FiTrendingUp, FiTrendingDown, FiActivity } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Sample data for demonstration
const sampleData = {
  recentDocuments: [
    { id: 1, name: 'Portfolio_Q2_2023.csv', type: 'portfolio', date: '2023-06-30' },
    { id: 2, name: 'Balance_Sheet_2023.pdf', type: 'balance_sheet', date: '2023-07-15' },
    { id: 3, name: 'Income_Statement_Q2.jpg', type: 'income_statement', date: '2023-06-30' }
  ],
  portfolioSummary: {
    totalValue: 1250000,
    changePercent: 3.5,
    distribution: {
      'Stocks': 65,
      'Bonds': 20,
      'Cash': 10,
      'Other': 5
    }
  },
  financialMetrics: {
    totalAssets: 2500000,
    totalLiabilities: 1000000,
    equity: 1500000,
    revenue: 800000,
    expenses: 600000,
    profit: 200000
  }
};

const FinancialAnalysisDashboard = () => {
  const [data, setData] = useState(sampleData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.200');
  
  // Fetch data from the API (commented out for now, using sample data)
  /*
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get('/api/financial/dashboard');
        setData(response.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, []);
  */
  
  const renderRecentDocuments = () => {
    return (
      <Card bg={cardBg} shadow="md" height="100%">
        <CardHeader>
          <Flex justify="space-between" align="center">
            <Heading size="md">Recent Documents</Heading>
            <Button as={Link} to="/financial/documents" size="sm" colorScheme="blue" variant="outline">
              View All
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {data.recentDocuments.map(doc => (
              <Box key={doc.id} p={3} borderWidth="1px" borderRadius="md">
                <HStack>
                  <Icon 
                    as={FiFileText} 
                    boxSize={5} 
                    color={
                      doc.type === 'portfolio' ? 'blue.500' : 
                      doc.type === 'balance_sheet' ? 'green.500' : 'purple.500'
                    } 
                  />
                  <Box>
                    <Text fontWeight="bold">{doc.name}</Text>
                    <Text fontSize="sm" color={textColor}>
                      {doc.type.replace('_', ' ')} • {doc.date}
                    </Text>
                  </Box>
                </HStack>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>
    );
  };
  
  const renderPortfolioSummary = () => {
    return (
      <Card bg={cardBg} shadow="md" height="100%">
        <CardHeader>
          <Flex justify="space-between" align="center">
            <Heading size="md">Portfolio Summary</Heading>
            <Button as={Link} to="/financial/portfolio" size="sm" colorScheme="blue" variant="outline">
              Details
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          <Stat mb={4}>
            <StatLabel>Total Value</StatLabel>
            <StatNumber>${(data.portfolioSummary.totalValue / 1000).toFixed(1)}K</StatNumber>
            <StatHelpText>
              <StatArrow type={data.portfolioSummary.changePercent >= 0 ? 'increase' : 'decrease'} />
              {Math.abs(data.portfolioSummary.changePercent)}%
            </StatHelpText>
          </Stat>
          
          <Heading size="sm" mb={2}>Asset Allocation</Heading>
          {Object.entries(data.portfolioSummary.distribution).map(([category, percentage]) => (
            <Box key={category} mb={2}>
              <Flex justify="space-between">
                <Text>{category}</Text>
                <Text>{percentage}%</Text>
              </Flex>
              <Progress 
                value={percentage} 
                size="sm" 
                colorScheme={
                  category === 'Stocks' ? 'blue' : 
                  category === 'Bonds' ? 'green' : 
                  category === 'Cash' ? 'yellow' : 'purple'
                } 
              />
            </Box>
          ))}
        </CardBody>
      </Card>
    );
  };
  
  const renderFinancialMetrics = () => {
    return (
      <Card bg={cardBg} shadow="md" height="100%">
        <CardHeader>
          <Flex justify="space-between" align="center">
            <Heading size="md">Financial Metrics</Heading>
            <Button as={Link} to="/financial/reports" size="sm" colorScheme="blue" variant="outline">
              Reports
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={2} spacing={4}>
            <Stat>
              <StatLabel>Total Assets</StatLabel>
              <HStack>
                <Icon as={FiDollarSign} color="green.500" />
                <StatNumber>${(data.financialMetrics.totalAssets / 1000000).toFixed(1)}M</StatNumber>
              </HStack>
            </Stat>
            
            <Stat>
              <StatLabel>Total Liabilities</StatLabel>
              <HStack>
                <Icon as={FiDollarSign} color="red.500" />
                <StatNumber>${(data.financialMetrics.totalLiabilities / 1000000).toFixed(1)}M</StatNumber>
              </HStack>
            </Stat>
            
            <Stat>
              <StatLabel>Equity</StatLabel>
              <HStack>
                <Icon as={FiPieChart} color="blue.500" />
                <StatNumber>${(data.financialMetrics.equity / 1000000).toFixed(1)}M</StatNumber>
              </HStack>
            </Stat>
            
            <Stat>
              <StatLabel>Revenue</StatLabel>
              <HStack>
                <Icon as={FiTrendingUp} color="green.500" />
                <StatNumber>${(data.financialMetrics.revenue / 1000).toFixed(0)}K</StatNumber>
              </HStack>
            </Stat>
            
            <Stat>
              <StatLabel>Expenses</StatLabel>
              <HStack>
                <Icon as={FiTrendingDown} color="red.500" />
                <StatNumber>${(data.financialMetrics.expenses / 1000).toFixed(0)}K</StatNumber>
              </HStack>
            </Stat>
            
            <Stat>
              <StatLabel>Profit</StatLabel>
              <HStack>
                <Icon as={FiActivity} color="green.500" />
                <StatNumber>${(data.financialMetrics.profit / 1000).toFixed(0)}K</StatNumber>
              </HStack>
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>
    );
  };
  
  if (isLoading) {
    return (
      <Box p={5}>
        <Heading size="lg" mb={6}>Financial Analysis Dashboard</Heading>
        <Text>Loading dashboard data...</Text>
        <Progress size="xs" isIndeterminate mt={4} />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box p={5}>
        <Heading size="lg" mb={6}>Financial Analysis Dashboard</Heading>
        <Text color="red.500">{error}</Text>
        <Button mt={4} colorScheme="blue" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Box>
    );
  }
  
  return (
    <Box p={5}>
      <Heading size="lg" mb={6}>Financial Analysis Dashboard</Heading>
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={6}>
        {renderRecentDocuments()}
        {renderPortfolioSummary()}
        {renderFinancialMetrics()}
      </SimpleGrid>
      
      <Flex justify="center" mt={8}>
        <Button as={Link} to="/financial/upload" colorScheme="blue" size="lg" leftIcon={<FiFileText />}>
          Upload New Document
        </Button>
      </Flex>
    </Box>
  );
};

export default FinancialAnalysisDashboard;
