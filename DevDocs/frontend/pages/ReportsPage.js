import React from 'react';
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Button,
  Icon,
  Flex,
  Table
} from '@chakra-ui/react';

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
import { FiDownload, FiFileText, FiPieChart, FiDollarSign, FiBarChart2 } from 'react-icons/fi';

// Sample data for demonstration
const sampleReports = [
  { id: 1, name: 'Portfolio Summary', type: 'portfolio', date: '2023-06-30', icon: FiPieChart },
  { id: 2, name: 'Balance Sheet', type: 'balance_sheet', date: '2023-07-15', icon: FiDollarSign },
  { id: 3, name: 'Income Statement', type: 'income_statement', date: '2023-06-30', icon: FiBarChart2 },
  { id: 4, name: 'Securities Analysis', type: 'securities', date: '2023-07-01', icon: FiFileText }
];

const ReportsPage = () => {
  return (
    <Box>
      <Heading mb={6}>Financial Reports</Heading>
      <Text mb={6}>View and generate financial reports based on your documents and data.</Text>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={8}>
        <Card>
          <CardHeader>
            <Heading size="md">Available Reports</Heading>
          </CardHeader>
          <CardBody>
            <TableContainer>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Report</Th>
                    <Th>Type</Th>
                    <Th>Date</Th>
                    <Th>Action</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {sampleReports.map(report => (
                    <Tr key={report.id}>
                      <Td>
                        <Flex align="center">
                          <Icon as={report.icon} mr={2} color="blue.500" />
                          {report.name}
                        </Flex>
                      </Td>
                      <Td>{report.type.replace('_', ' ')}</Td>
                      <Td>{report.date}</Td>
                      <Td>
                        <Button size="sm" leftIcon={<FiDownload />} colorScheme="blue" variant="outline">
                          Download
                        </Button>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Generate New Report</Heading>
          </CardHeader>
          <CardBody>
            <Text mb={4}>Select a report type to generate a new financial report.</Text>

            <SimpleGrid columns={2} spacing={4}>
              <Button leftIcon={<FiPieChart />} colorScheme="blue" variant="outline" justifyContent="flex-start" height="auto" py={3}>
                <Box textAlign="left">
                  <Text fontWeight="bold">Portfolio Summary</Text>
                  <Text fontSize="xs">Overview of your investment portfolio</Text>
                </Box>
              </Button>

              <Button leftIcon={<FiDollarSign />} colorScheme="green" variant="outline" justifyContent="flex-start" height="auto" py={3}>
                <Box textAlign="left">
                  <Text fontWeight="bold">Balance Sheet</Text>
                  <Text fontSize="xs">Assets, liabilities, and equity</Text>
                </Box>
              </Button>

              <Button leftIcon={<FiBarChart2 />} colorScheme="purple" variant="outline" justifyContent="flex-start" height="auto" py={3}>
                <Box textAlign="left">
                  <Text fontWeight="bold">Income Statement</Text>
                  <Text fontSize="xs">Revenue, expenses, and profit</Text>
                </Box>
              </Button>

              <Button leftIcon={<FiFileText />} colorScheme="orange" variant="outline" justifyContent="flex-start" height="auto" py={3}>
                <Box textAlign="left">
                  <Text fontWeight="bold">Securities Analysis</Text>
                  <Text fontSize="xs">Detailed analysis of securities</Text>
                </Box>
              </Button>
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Text fontSize="sm" color="gray.500">
        Note: This is a demonstration page. In a production environment, you would be able to generate and download actual financial reports.
      </Text>
    </Box>
  );
};

export default ReportsPage;
