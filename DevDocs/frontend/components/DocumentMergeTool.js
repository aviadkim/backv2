import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Select,
  VStack,
  HStack,
  Flex,
  Divider,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Badge,
  List,
  ListItem,
  ListIcon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { FiFileText, FiBarChart2, FiPieChart, FiDollarSign, FiTrendingUp, FiChevronRight } from 'react-icons/fi';

// ComparisonResultView component
const ComparisonResultView = ({ comparisonResult }) => {
  return (
    <VStack align="start" spacing={4} width="100%">
      <Heading size="sm">Comparison Summary</Heading>

      <Box p={4} borderWidth={1} borderRadius="md" width="100%">
        <VStack align="start" spacing={3} width="100%">
          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Comparison Date:</Text>
            <Text>{new Date(comparisonResult.comparison_date).toLocaleString()}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Period:</Text>
            <Text>
              {new Date(comparisonResult.period_start).toLocaleDateString()} to {new Date(comparisonResult.period_end).toLocaleDateString()}
            </Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Document Count:</Text>
            <Text>{comparisonResult.document_count}</Text>
          </Flex>
        </VStack>
      </Box>

      <Divider />

      <Heading size="sm">Significant Changes</Heading>

      {comparisonResult.summary?.significant_changes?.length > 0 ? (
        <VStack align="start" spacing={3} width="100%">
          {comparisonResult.summary.significant_changes.map((change, index) => (
            <Alert
              key={index}
              status={change.change_pct > 0 ? "success" : "warning"}
              variant="left-accent"
              borderRadius="md"
            >
              <AlertIcon />
              <Box>
                <AlertTitle>{change.type.charAt(0).toUpperCase() + change.type.slice(1)}</AlertTitle>
                <AlertDescription>
                  {change.description}
                </AlertDescription>
              </Box>
            </Alert>
          ))}
        </VStack>
      ) : (
        <Text>No significant changes detected</Text>
      )}

      <Divider />

      <Heading size="sm">Trends</Heading>

      <Accordion allowMultiple width="100%">
        {/* Portfolio Trends */}
        {comparisonResult.trends?.portfolio && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiPieChart />
                  <Text fontWeight="bold" ml={2}>Portfolio Trends</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                {comparisonResult.summary?.portfolio?.portfolio_value_change && (
                  <Alert
                    status={comparisonResult.summary.portfolio.portfolio_value_change.change_pct > 0 ? "success" : "warning"}
                    borderRadius="md"
                  >
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Portfolio Value Change</AlertTitle>
                      <AlertDescription>
                        {comparisonResult.summary.portfolio.portfolio_value_change.description}
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}

                {comparisonResult.trends.portfolio.top_performers?.length > 0 && (
                  <Box width="100%">
                    <Heading size="xs" mb={2}>Top Performers</Heading>
                    <Table size="sm" variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Name</Th>
                          <Th isNumeric>Return</Th>
                          <Th isNumeric>Value</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {comparisonResult.trends.portfolio.top_performers.map((performer, index) => (
                          <Tr key={index}>
                            <Td>{performer.name}</Td>
                            <Td isNumeric color={performer.average_return > 0 ? "green.500" : "red.500"}>
                              {performer.average_return > 0 ? '+' : ''}{performer.average_return.toFixed(2)}%
                            </Td>
                            <Td isNumeric>${performer.value?.toLocaleString()}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                )}
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}

        {/* Financial Health Trends */}
        {comparisonResult.trends?.balance_sheet && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiBarChart2 />
                  <Text fontWeight="bold" ml={2}>Financial Health Trends</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                {comparisonResult.summary?.financial_health?.assets_change && (
                  <Alert
                    status={comparisonResult.summary.financial_health.assets_change.change_pct > 0 ? "success" : "warning"}
                    borderRadius="md"
                  >
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Assets Change</AlertTitle>
                      <AlertDescription>
                        {comparisonResult.summary.financial_health.assets_change.description}
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}

                {comparisonResult.trends.balance_sheet.major_changes?.length > 0 && (
                  <Box width="100%">
                    <Heading size="xs" mb={2}>Major Changes</Heading>
                    <Table size="sm" variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Item</Th>
                          <Th isNumeric>Old Value</Th>
                          <Th isNumeric>New Value</Th>
                          <Th isNumeric>Change %</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {comparisonResult.trends.balance_sheet.major_changes.map((change, index) => (
                          <Tr key={index}>
                            <Td>{change.name}</Td>
                            <Td isNumeric>${change.old_value?.toLocaleString()}</Td>
                            <Td isNumeric>${change.new_value?.toLocaleString()}</Td>
                            <Td isNumeric color={change.change_pct > 0 ? "green.500" : "red.500"}>
                              {change.change_pct > 0 ? '+' : ''}{change.change_pct.toFixed(2)}%
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                )}
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}
      </Accordion>
    </VStack>
  );
};

// ComprehensiveReportView component
const ComprehensiveReportView = ({ report }) => {
  return (
    <VStack align="start" spacing={4} width="100%">
      <Heading size="sm">Comprehensive Financial Report</Heading>

      <Box p={4} borderWidth={1} borderRadius="md" width="100%">
        <VStack align="start" spacing={3} width="100%">
          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Report Date:</Text>
            <Text>{new Date(report.report_date).toLocaleString()}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Report Type:</Text>
            <Text>{report.report_type}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Data Sources:</Text>
            <Text>{report.data_sources.join(', ')}</Text>
          </Flex>
        </VStack>
      </Box>

      <Divider />

      <Heading size="sm">Financial Snapshot</Heading>

      <Box p={4} borderWidth={1} borderRadius="md" width="100%">
        <VStack align="start" spacing={3} width="100%">
          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Total Assets:</Text>
            <Text>${report.financial_snapshot?.total_assets?.toLocaleString() || 'N/A'}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Total Liabilities:</Text>
            <Text>${report.financial_snapshot?.total_liabilities?.toLocaleString() || 'N/A'}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Net Worth:</Text>
            <Text>${report.financial_snapshot?.net_worth?.toLocaleString() || 'N/A'}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Monthly Income:</Text>
            <Text>${report.financial_snapshot?.monthly_income?.toLocaleString() || 'N/A'}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Monthly Expenses:</Text>
            <Text>${report.financial_snapshot?.monthly_expenses?.toLocaleString() || 'N/A'}</Text>
          </Flex>
        </VStack>
      </Box>

      <Divider />

      <Heading size="sm">Recommendations</Heading>

      {report.recommendations?.length > 0 ? (
        <VStack align="start" spacing={3} width="100%">
          {report.recommendations.map((recommendation, index) => (
            <Alert
              key={index}
              status={recommendation.priority === 'high' ? "error" :
                     recommendation.priority === 'medium' ? "warning" : "info"}
              variant="left-accent"
              borderRadius="md"
            >
              <Box>
                <AlertTitle>{recommendation.title}</AlertTitle>
                <AlertDescription>
                  <Text mt={2}>{recommendation.description}</Text>
                  <Text mt={2} fontWeight="bold">Recommended Action:</Text>
                  <Text>{recommendation.action}</Text>
                </AlertDescription>
              </Box>
            </Alert>
          ))}
        </VStack>
      ) : (
        <Text>No recommendations available</Text>
      )}
    </VStack>
  );
};

// MergedDocumentView component
const MergedDocumentView = ({ mergedDocument }) => {
  return (
    <VStack align="start" spacing={4} width="100%">
      <Heading size="sm">Merged Document Summary</Heading>

      <Box p={4} borderWidth={1} borderRadius="md" width="100%">
        <VStack align="start" spacing={3} width="100%">
          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Merge Date:</Text>
            <Text>{new Date(mergedDocument.merge_date).toLocaleString()}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Original Documents:</Text>
            <Text>{mergedDocument.original_documents}</Text>
          </Flex>

          <Flex justify="space-between" width="100%">
            <Text fontWeight="bold">Document Types:</Text>
            <Text>{mergedDocument.document_types.join(', ')}</Text>
          </Flex>
        </VStack>
      </Box>

      <Divider />

      <Heading size="sm">Financial Overview</Heading>

      <Accordion allowMultiple width="100%">
        {/* Portfolio Section */}
        {mergedDocument.merged_data.portfolio && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiPieChart />
                  <Text fontWeight="bold" ml={2}>Portfolio</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                <Heading size="xs">Portfolio Summary</Heading>
                <Box p={3} borderWidth={1} borderRadius="md" width="100%">
                  <Flex justify="space-between">
                    <Text fontWeight="bold">Total Value:</Text>
                    <Text>${mergedDocument.merged_data.portfolio.summary?.total_value?.toLocaleString() || 'N/A'}</Text>
                  </Flex>
                </Box>

                <Heading size="xs">Securities ({mergedDocument.merged_data.portfolio.securities?.length || 0})</Heading>
                {mergedDocument.merged_data.portfolio.securities?.length > 0 ? (
                  <Box overflowX="auto" width="100%">
                    <Table size="sm" variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Name</Th>
                          <Th>Type</Th>
                          <Th isNumeric>Quantity</Th>
                          <Th isNumeric>Price</Th>
                          <Th isNumeric>Value</Th>
                          <Th isNumeric>Return</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {mergedDocument.merged_data.portfolio.securities.map((security, index) => (
                          <Tr key={index}>
                            <Td>{security.name}</Td>
                            <Td>{security.type}</Td>
                            <Td isNumeric>{security.quantity}</Td>
                            <Td isNumeric>${security.price?.toLocaleString()}</Td>
                            <Td isNumeric>${security.value?.toLocaleString()}</Td>
                            <Td isNumeric>{security.return}%</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                ) : (
                  <Text>No securities found</Text>
                )}
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}

        {/* Balance Sheet Section */}
        {mergedDocument.merged_data.balance_sheet && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiBarChart2 />
                  <Text fontWeight="bold" ml={2}>Balance Sheet</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                <Heading size="xs">Balance Sheet Summary</Heading>
                <Box p={3} borderWidth={1} borderRadius="md" width="100%">
                  <VStack align="start" spacing={2} width="100%">
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Assets:</Text>
                      <Text>${mergedDocument.merged_data.balance_sheet.summary?.total_assets?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Liabilities:</Text>
                      <Text>${mergedDocument.merged_data.balance_sheet.summary?.total_liabilities?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Equity:</Text>
                      <Text>${mergedDocument.merged_data.balance_sheet.summary?.total_equity?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                  </VStack>
                </Box>
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}

        {/* Income Statement Section */}
        {mergedDocument.merged_data.income_statement && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiTrendingUp />
                  <Text fontWeight="bold" ml={2}>Income Statement</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                <Heading size="xs">Income Statement Summary</Heading>
                <Box p={3} borderWidth={1} borderRadius="md" width="100%">
                  <VStack align="start" spacing={2} width="100%">
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Revenue:</Text>
                      <Text>${mergedDocument.merged_data.income_statement.summary?.total_revenue?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Expenses:</Text>
                      <Text>${mergedDocument.merged_data.income_statement.summary?.total_expenses?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Net Profit:</Text>
                      <Text>${mergedDocument.merged_data.income_statement.summary?.net_profit?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                  </VStack>
                </Box>
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}

        {/* Salary Section */}
        {mergedDocument.merged_data.salary && (
          <AccordionItem>
            <AccordionButton>
              <Box flex="1" textAlign="left">
                <Flex align="center">
                  <FiDollarSign />
                  <Text fontWeight="bold" ml={2}>Salary</Text>
                </Flex>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel>
              <VStack align="start" spacing={3} width="100%">
                <Heading size="xs">Salary Summary</Heading>
                <Box p={3} borderWidth={1} borderRadius="md" width="100%">
                  <VStack align="start" spacing={2} width="100%">
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Average Gross:</Text>
                      <Text>${mergedDocument.merged_data.salary.summary?.average_gross?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Average Net:</Text>
                      <Text>${mergedDocument.merged_data.salary.summary?.average_net?.toLocaleString() || 'N/A'}</Text>
                    </Flex>
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Salary Slips:</Text>
                      <Text>{mergedDocument.merged_data.salary.summary?.salary_slips_count || 0}</Text>
                    </Flex>
                  </VStack>
                </Box>
              </VStack>
            </AccordionPanel>
          </AccordionItem>
        )}
      </Accordion>
    </VStack>
  );
};

const DocumentMergeTool = ({ documentData, previousDocuments }) => {
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [mergedDocument, setMergedDocument] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [comprehensiveReport, setComprehensiveReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const toast = useToast();

  // Add current document to available documents
  const availableDocuments = [...(previousDocuments || [])];
  if (documentData) {
    availableDocuments.unshift(documentData);
  }

  // Handle document selection
  const handleDocumentSelection = (documentId) => {
    if (selectedDocuments.includes(documentId)) {
      setSelectedDocuments(selectedDocuments.filter(id => id !== documentId));
    } else {
      setSelectedDocuments([...selectedDocuments, documentId]);
    }
  };

  // Handle merging documents
  const handleMergeDocuments = async () => {
    if (selectedDocuments.length < 2) {
      toast({
        title: "Selection Error",
        description: "Please select at least two documents to merge.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);

    try {
      // Get the selected documents
      const documentsToMerge = availableDocuments.filter(doc =>
        selectedDocuments.includes(doc.document_id)
      );

      // Call the API to merge documents
      const response = await fetch('/api/financial/merge-documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documents: documentsToMerge
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      setMergedDocument(result);

      toast({
        title: "Documents Merged",
        description: `Successfully merged ${documentsToMerge.length} documents.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error merging documents:", error);
      toast({
        title: "Merge Failed",
        description: error.message || "Failed to merge documents. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle comparing documents over time
  const handleCompareOverTime = async () => {
    if (!mergedDocument) {
      toast({
        title: "No Merged Document",
        description: "Please merge documents first.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);

    try {
      // Create a second merged document with a different date for testing
      const testMergedDocument = {
        ...mergedDocument,
        merge_date: new Date(new Date(mergedDocument.merge_date).getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
      };

      // Call the API to compare documents over time
      const response = await fetch('/api/financial/compare-over-time', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          merged_documents: [testMergedDocument, mergedDocument]
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      setComparisonResult(result);

      toast({
        title: "Comparison Complete",
        description: "Successfully compared documents over time.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error comparing documents:", error);
      toast({
        title: "Comparison Failed",
        description: error.message || "Failed to compare documents. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle generating comprehensive report
  const handleGenerateReport = async () => {
    if (!mergedDocument) {
      toast({
        title: "No Merged Document",
        description: "Please merge documents first.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);

    try {
      // Call the API to generate comprehensive report
      const response = await fetch('/api/financial/comprehensive-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          merged_document: mergedDocument
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      setComprehensiveReport(result);

      toast({
        title: "Report Generated",
        description: "Successfully generated comprehensive report.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error generating report:", error);
      toast({
        title: "Report Generation Failed",
        description: error.message || "Failed to generate report. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Reset state when documents change
  useEffect(() => {
    setSelectedDocuments([]);
    setMergedDocument(null);
    setComparisonResult(null);
    setComprehensiveReport(null);
    setActiveTab(0);
  }, [documentData, previousDocuments]);

  return (
    <Box width="100%">
      <Card>
        <CardHeader bg="teal.50">
          <Flex align="center">
            <FiFileText size="24px" color="teal" />
            <Heading size="md" ml={2}>Document Merge Tool</Heading>
          </Flex>
        </CardHeader>
        <CardBody>
          <Text mb={4}>
            This tool allows you to merge multiple financial documents, compare them over time, and generate comprehensive reports.
          </Text>

          {/* Document selection */}
          <Box mb={6}>
            <Heading size="sm" mb={3}>Select Documents to Merge</Heading>
            <VStack align="start" spacing={2} maxH="300px" overflowY="auto" p={2} borderWidth={1} borderRadius="md">
              {availableDocuments.length > 0 ? (
                availableDocuments.map((doc) => (
                  <Flex
                    key={doc.document_id}
                    width="100%"
                    p={2}
                    borderWidth={1}
                    borderRadius="md"
                    bg={selectedDocuments.includes(doc.document_id) ? "teal.50" : "white"}
                    _hover={{ bg: "gray.50" }}
                    cursor="pointer"
                    onClick={() => handleDocumentSelection(doc.document_id)}
                  >
                    <Box flex={1}>
                      <Text fontWeight="bold">{doc.file_name || `Document ${doc.document_id}`}</Text>
                      <Text fontSize="sm" color="gray.600">
                        {doc.document_date || 'No date'} |
                        {doc.document_types?.join(', ') || 'Unknown type'}
                      </Text>
                    </Box>
                    <Badge colorScheme={selectedDocuments.includes(doc.document_id) ? "teal" : "gray"}>
                      {selectedDocuments.includes(doc.document_id) ? "Selected" : "Select"}
                    </Badge>
                  </Flex>
                ))
              ) : (
                <Text>No documents available. Please upload documents first.</Text>
              )}
            </VStack>

            <Flex justify="space-between" mt={4}>
              <Button
                colorScheme="teal"
                isDisabled={selectedDocuments.length < 2}
                onClick={handleMergeDocuments}
                isLoading={isLoading && activeTab === 0}
              >
                Merge Selected Documents
              </Button>

              <HStack>
                <Button
                  variant="outline"
                  onClick={() => setSelectedDocuments([])}
                  isDisabled={selectedDocuments.length === 0}
                >
                  Clear Selection
                </Button>

                <Button
                  variant="outline"
                  onClick={() => setSelectedDocuments(availableDocuments.map(doc => doc.document_id))}
                  isDisabled={availableDocuments.length === 0}
                >
                  Select All
                </Button>
              </HStack>
            </Flex>
          </Box>

          {/* Tabs for different functionalities */}
          <Tabs variant="enclosed" colorScheme="teal" index={activeTab} onChange={setActiveTab}>
            <TabList>
              <Tab>Merge Documents</Tab>
              <Tab isDisabled={!mergedDocument}>Compare Over Time</Tab>
              <Tab isDisabled={!mergedDocument}>Comprehensive Report</Tab>
            </TabList>

            <TabPanels>
              {/* Merge Documents Tab */}
              <TabPanel>
                {isLoading && activeTab === 0 ? (
                  <Flex justify="center" align="center" direction="column" py={10}>
                    <Spinner size="xl" color="teal.500" mb={4} />
                    <Text>Merging documents...</Text>
                  </Flex>
                ) : mergedDocument ? (
                  <MergedDocumentView mergedDocument={mergedDocument} />
                ) : (
                  <Alert status="info" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <AlertTitle>No merged document</AlertTitle>
                      <AlertDescription>
                        Select at least two documents and click "Merge Selected Documents" to create a merged document.
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}
              </TabPanel>

              {/* Compare Over Time Tab */}
              <TabPanel>
                {isLoading && activeTab === 1 ? (
                  <Flex justify="center" align="center" direction="column" py={10}>
                    <Spinner size="xl" color="teal.500" mb={4} />
                    <Text>Comparing documents over time...</Text>
                  </Flex>
                ) : comparisonResult ? (
                  <ComparisonResultView comparisonResult={comparisonResult} />
                ) : (
                  <VStack spacing={4} align="start" width="100%">
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      <Box>
                        <AlertTitle>No comparison data</AlertTitle>
                        <AlertDescription>
                          Click the button below to compare the merged document over time.
                        </AlertDescription>
                      </Box>
                    </Alert>

                    <Button
                      colorScheme="teal"
                      onClick={handleCompareOverTime}
                      isDisabled={!mergedDocument}
                    >
                      Compare Over Time
                    </Button>
                  </VStack>
                )}
              </TabPanel>

              {/* Comprehensive Report Tab */}
              <TabPanel>
                {isLoading && activeTab === 2 ? (
                  <Flex justify="center" align="center" direction="column" py={10}>
                    <Spinner size="xl" color="teal.500" mb={4} />
                    <Text>Generating comprehensive report...</Text>
                  </Flex>
                ) : comprehensiveReport ? (
                  <ComprehensiveReportView report={comprehensiveReport} />
                ) : (
                  <VStack spacing={4} align="start" width="100%">
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      <Box>
                        <AlertTitle>No report data</AlertTitle>
                        <AlertDescription>
                          Click the button below to generate a comprehensive financial report.
                        </AlertDescription>
                      </Box>
                    </Alert>

                    <Button
                      colorScheme="teal"
                      onClick={handleGenerateReport}
                      isDisabled={!mergedDocument}
                    >
                      Generate Comprehensive Report
                    </Button>
                  </VStack>
                )}
              </TabPanel>
            </TabPanels>
          </Tabs>
        </CardBody>
      </Card>
    </Box>
  );
};

export default DocumentMergeTool;
