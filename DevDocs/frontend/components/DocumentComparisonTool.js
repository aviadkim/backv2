import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
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
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  FormControl,
  FormLabel
} from '@chakra-ui/react';
import { 
  FiActivity, 
  FiAlertCircle, 
  FiCheckCircle, 
  FiTrendingUp, 
  FiTrendingDown,
  FiPlus,
  FiMinus,
  FiEdit,
  FiFileText,
  FiBarChart2,
  FiList,
  FiRefreshCw
} from 'react-icons/fi';
import axios from 'axios';

const DocumentComparisonTool = ({ documentData, previousDocuments = [] }) => {
  const [isComparing, setIsComparing] = useState(false);
  const [selectedPreviousDoc, setSelectedPreviousDoc] = useState('');
  const [previousDocData, setPreviousDocData] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [error, setError] = useState(null);
  
  const toast = useToast();
  
  // Effect to set the first previous document as selected by default
  useEffect(() => {
    if (previousDocuments.length > 0 && !selectedPreviousDoc) {
      setSelectedPreviousDoc(previousDocuments[0].id);
      setPreviousDocData(previousDocuments[0].data);
    }
  }, [previousDocuments, selectedPreviousDoc]);
  
  const handlePreviousDocChange = (e) => {
    const docId = e.target.value;
    setSelectedPreviousDoc(docId);
    
    // Find the selected document data
    const selectedDoc = previousDocuments.find(doc => doc.id === docId);
    if (selectedDoc) {
      setPreviousDocData(selectedDoc.data);
    }
  };
  
  const handleCompare = async () => {
    if (!documentData) {
      setError('No current document data available. Please upload and process a document first.');
      return;
    }
    
    if (!previousDocData) {
      setError('No previous document data available for comparison.');
      return;
    }
    
    setIsComparing(true);
    setError(null);
    setComparisonResult(null);
    
    try {
      // Send the comparison request to the API
      const response = await axios.post('/api/financial/compare-documents', {
        current_doc: documentData,
        previous_doc: previousDocData
      });
      
      setComparisonResult(response.data.comparison_result);
      toast({
        title: 'Comparison successful',
        description: 'Documents compared successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error comparing documents:', err);
      setError(err.response?.data?.detail || 'Error comparing documents');
      toast({
        title: 'Comparison failed',
        description: err.response?.data?.detail || 'An error occurred while comparing documents',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsComparing(false);
    }
  };
  
  const formatPercentChange = (value) => {
    if (value === null || value === undefined) return 'N/A';
    
    const formattedValue = value.toFixed(2);
    const isPositive = value > 0;
    
    return (
      <HStack>
        <StatArrow type={isPositive ? 'increase' : 'decrease'} />
        <Text color={isPositive ? 'green.500' : 'red.500'}>
          {formattedValue}%
        </Text>
      </HStack>
    );
  };
  
  const renderPortfolioComparison = () => {
    if (!comparisonResult || !comparisonResult.portfolio_comparison) return null;
    
    const portfolioComp = comparisonResult.portfolio_comparison;
    
    return (
      <Box>
        <StatGroup mb={4}>
          <Stat>
            <StatLabel>Total Value Change</StatLabel>
            <StatNumber>
              {portfolioComp.total_value_change ? portfolioComp.total_value_change.toFixed(2) : 'N/A'}
            </StatNumber>
            <StatHelpText>
              {formatPercentChange(portfolioComp.total_value_change_percent)}
            </StatHelpText>
          </Stat>
        </StatGroup>
        
        <Tabs variant="enclosed" colorScheme="blue" size="sm">
          <TabList>
            <Tab>Security Changes</Tab>
            <Tab>New Securities</Tab>
            <Tab>Removed Securities</Tab>
            <Tab>Type Distribution</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              {portfolioComp.security_changes && portfolioComp.security_changes.length > 0 ? (
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Security</Th>
                        <Th>ISIN</Th>
                        <Th>Field</Th>
                        <Th>Previous</Th>
                        <Th>Current</Th>
                        <Th>Change</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {portfolioComp.security_changes.map((security, secIndex) => (
                        Object.entries(security.changes).map(([field, change], fieldIndex) => (
                          <Tr key={`${secIndex}-${fieldIndex}`}>
                            {fieldIndex === 0 && (
                              <>
                                <Td rowSpan={Object.keys(security.changes).length}>
                                  {security.security_name}
                                </Td>
                                <Td rowSpan={Object.keys(security.changes).length}>
                                  {security.isin}
                                </Td>
                              </>
                            )}
                            <Td>{field}</Td>
                            <Td>{change.previous}</Td>
                            <Td>{change.current}</Td>
                            <Td>
                              {change.percent_change !== null ? (
                                formatPercentChange(change.percent_change)
                              ) : (
                                change.change
                              )}
                            </Td>
                          </Tr>
                        ))
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              ) : (
                <Text>No security changes detected</Text>
              )}
            </TabPanel>
            
            <TabPanel>
              {portfolioComp.new_securities && portfolioComp.new_securities.length > 0 ? (
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Security</Th>
                        <Th>ISIN</Th>
                        <Th>Quantity</Th>
                        <Th>Price</Th>
                        <Th>Value</Th>
                        <Th>Return</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {portfolioComp.new_securities.map((security, index) => (
                        <Tr key={index}>
                          <Td>{security.security_name || security.name}</Td>
                          <Td>{security.isin}</Td>
                          <Td>{security.quantity}</Td>
                          <Td>{security.price}</Td>
                          <Td>{security.value}</Td>
                          <Td>{security.return}%</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              ) : (
                <Text>No new securities added</Text>
              )}
            </TabPanel>
            
            <TabPanel>
              {portfolioComp.removed_securities && portfolioComp.removed_securities.length > 0 ? (
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Security</Th>
                        <Th>ISIN</Th>
                        <Th>Quantity</Th>
                        <Th>Price</Th>
                        <Th>Value</Th>
                        <Th>Return</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {portfolioComp.removed_securities.map((security, index) => (
                        <Tr key={index}>
                          <Td>{security.security_name || security.name}</Td>
                          <Td>{security.isin}</Td>
                          <Td>{security.quantity}</Td>
                          <Td>{security.price}</Td>
                          <Td>{security.value}</Td>
                          <Td>{security.return}%</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              ) : (
                <Text>No securities removed</Text>
              )}
            </TabPanel>
            
            <TabPanel>
              {portfolioComp.type_distribution_changes && Object.keys(portfolioComp.type_distribution_changes).length > 0 ? (
                <TableContainer>
                  <Table variant="simple" size="sm">
                    <Thead>
                      <Tr>
                        <Th>Asset Type</Th>
                        <Th>Previous</Th>
                        <Th>Current</Th>
                        <Th>Change</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {Object.entries(portfolioComp.type_distribution_changes).map(([type, change], index) => (
                        <Tr key={index}>
                          <Td>{type}</Td>
                          <Td>{change.previous}%</Td>
                          <Td>{change.current}%</Td>
                          <Td>{formatPercentChange(change.percent_change)}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              ) : (
                <Text>No changes in asset type distribution</Text>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    );
  };
  
  const renderSignificantChanges = () => {
    if (!comparisonResult || !comparisonResult.summary || !comparisonResult.summary.significant_changes) return null;
    
    const significantChanges = comparisonResult.summary.significant_changes;
    
    if (significantChanges.length === 0) {
      return <Text>No significant changes detected</Text>;
    }
    
    return (
      <VStack align="start" spacing={3} width="100%">
        {significantChanges.map((change, index) => {
          let icon;
          let color;
          
          switch (change.type) {
            case 'portfolio_value':
              icon = change.change_percent > 0 ? FiTrendingUp : FiTrendingDown;
              color = change.change_percent > 0 ? 'green.500' : 'red.500';
              break;
            case 'new_securities':
              icon = FiPlus;
              color = 'green.500';
              break;
            case 'removed_securities':
              icon = FiMinus;
              color = 'red.500';
              break;
            case 'security_field_change':
              icon = FiEdit;
              color = 'blue.500';
              break;
            default:
              icon = FiActivity;
              color = 'gray.500';
          }
          
          return (
            <Alert 
              key={index}
              status={color.includes('red') ? 'error' : color.includes('green') ? 'success' : 'info'}
              variant="left-accent"
              borderRadius="md"
            >
              <Icon as={icon} color={color} mr={2} />
              <Box>
                <AlertTitle>{change.type.replace(/_/g, ' ').toUpperCase()}</AlertTitle>
                <AlertDescription>{change.description}</AlertDescription>
              </Box>
            </Alert>
          );
        })}
      </VStack>
    );
  };
  
  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Document Comparison Tool</Heading>
        <Text>Compare your current document with a previous document to identify changes and developments.</Text>
        
        <Card width="100%">
          <CardHeader>
            <Heading size="md">Comparison Options</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl>
                <FormLabel>Select Previous Document</FormLabel>
                <Select 
                  value={selectedPreviousDoc} 
                  onChange={handlePreviousDocChange}
                  placeholder="Select a previous document"
                  isDisabled={previousDocuments.length === 0}
                >
                  {previousDocuments.map(doc => (
                    <option key={doc.id} value={doc.id}>
                      {doc.name || doc.id} ({doc.date})
                    </option>
                  ))}
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Select a previous document to compare with the current document
                </Text>
              </FormControl>
              
              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>Comparison Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <Button
                leftIcon={<FiRefreshCw />}
                colorScheme="blue"
                onClick={handleCompare}
                isLoading={isComparing}
                loadingText="Comparing..."
                width="full"
                mt={2}
                isDisabled={!documentData || !previousDocData}
              >
                Compare Documents
              </Button>
              
              {!documentData && (
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>No Current Document</AlertTitle>
                  <AlertDescription>
                    Please upload and process a document first to compare.
                  </AlertDescription>
                </Alert>
              )}
              
              {documentData && previousDocuments.length === 0 && (
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>No Previous Documents</AlertTitle>
                  <AlertDescription>
                    No previous documents available for comparison. Please upload at least two documents.
                  </AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
        
        {comparisonResult && (
          <Card width="100%">
            <CardHeader>
              <Heading size="md">Comparison Results</Heading>
              <Text fontSize="sm" color="gray.500" mt={1}>
                Comparison ID: {comparisonResult.comparison_id}
              </Text>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed" colorScheme="blue">
                <TabList>
                  <Tab>Significant Changes</Tab>
                  <Tab>Portfolio Comparison</Tab>
                  <Tab>ISIN Comparison</Tab>
                  <Tab>Metadata Comparison</Tab>
                </TabList>
                
                <TabPanels>
                  <TabPanel>
                    <Heading size="sm" mb={4}>Significant Changes</Heading>
                    {renderSignificantChanges()}
                  </TabPanel>
                  
                  <TabPanel>
                    <Heading size="sm" mb={4}>Portfolio Comparison</Heading>
                    {renderPortfolioComparison()}
                  </TabPanel>
                  
                  <TabPanel>
                    <Heading size="sm" mb={4}>ISIN Comparison</Heading>
                    <Tabs variant="soft-rounded" colorScheme="green" size="sm">
                      <TabList>
                        <Tab>New Entities</Tab>
                        <Tab>Removed Entities</Tab>
                        <Tab>Changed Entities</Tab>
                      </TabList>
                      
                      <TabPanels>
                        <TabPanel>
                          {comparisonResult.isin_comparison?.new_entities?.length > 0 ? (
                            <TableContainer>
                              <Table variant="simple" size="sm">
                                <Thead>
                                  <Tr>
                                    <Th>ISIN</Th>
                                    <Th>Name</Th>
                                    <Th>Type</Th>
                                  </Tr>
                                </Thead>
                                <Tbody>
                                  {comparisonResult.isin_comparison.new_entities.map((entity, index) => (
                                    <Tr key={index}>
                                      <Td>{entity.isin}</Td>
                                      <Td>{entity.name}</Td>
                                      <Td>{entity.type}</Td>
                                    </Tr>
                                  ))}
                                </Tbody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Text>No new ISIN entities</Text>
                          )}
                        </TabPanel>
                        
                        <TabPanel>
                          {comparisonResult.isin_comparison?.removed_entities?.length > 0 ? (
                            <TableContainer>
                              <Table variant="simple" size="sm">
                                <Thead>
                                  <Tr>
                                    <Th>ISIN</Th>
                                    <Th>Name</Th>
                                    <Th>Type</Th>
                                  </Tr>
                                </Thead>
                                <Tbody>
                                  {comparisonResult.isin_comparison.removed_entities.map((entity, index) => (
                                    <Tr key={index}>
                                      <Td>{entity.isin}</Td>
                                      <Td>{entity.name}</Td>
                                      <Td>{entity.type}</Td>
                                    </Tr>
                                  ))}
                                </Tbody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Text>No removed ISIN entities</Text>
                          )}
                        </TabPanel>
                        
                        <TabPanel>
                          {comparisonResult.isin_comparison?.changed_entities?.length > 0 ? (
                            <TableContainer>
                              <Table variant="simple" size="sm">
                                <Thead>
                                  <Tr>
                                    <Th>ISIN</Th>
                                    <Th>Field</Th>
                                    <Th>Previous</Th>
                                    <Th>Current</Th>
                                  </Tr>
                                </Thead>
                                <Tbody>
                                  {comparisonResult.isin_comparison.changed_entities.map((entity, entityIndex) => (
                                    Object.entries(entity.changes).map(([field, change], fieldIndex) => (
                                      <Tr key={`${entityIndex}-${fieldIndex}`}>
                                        {fieldIndex === 0 && (
                                          <Td rowSpan={Object.keys(entity.changes).length}>
                                            {entity.isin}
                                          </Td>
                                        )}
                                        <Td>{field}</Td>
                                        <Td>{change.previous}</Td>
                                        <Td>{change.current}</Td>
                                      </Tr>
                                    ))
                                  ))}
                                </Tbody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Text>No changed ISIN entities</Text>
                          )}
                        </TabPanel>
                      </TabPanels>
                    </Tabs>
                  </TabPanel>
                  
                  <TabPanel>
                    <Heading size="sm" mb={4}>Metadata Comparison</Heading>
                    {comparisonResult.metadata_comparison?.changed_fields?.length > 0 ? (
                      <TableContainer>
                        <Table variant="simple" size="sm">
                          <Thead>
                            <Tr>
                              <Th>Field</Th>
                              <Th>Previous</Th>
                              <Th>Current</Th>
                            </Tr>
                          </Thead>
                          <Tbody>
                            {comparisonResult.metadata_comparison.changed_fields.map((field, index) => (
                              <Tr key={index}>
                                <Td>{field}</Td>
                                <Td>
                                  {typeof comparisonResult.metadata_comparison.changes[field]?.previous === 'object'
                                    ? JSON.stringify(comparisonResult.metadata_comparison.changes[field]?.previous)
                                    : comparisonResult.metadata_comparison.changes[field]?.previous}
                                </Td>
                                <Td>
                                  {typeof comparisonResult.metadata_comparison.changes[field]?.current === 'object'
                                    ? JSON.stringify(comparisonResult.metadata_comparison.changes[field]?.current)
                                    : comparisonResult.metadata_comparison.changes[field]?.current}
                                </Td>
                              </Tr>
                            ))}
                          </Tbody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Text>No metadata changes detected</Text>
                    )}
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default DocumentComparisonTool;
