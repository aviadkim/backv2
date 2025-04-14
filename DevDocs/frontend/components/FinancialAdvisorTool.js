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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Flex,
  Spacer,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Progress,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react';
import {
  FiActivity,
  FiAlertCircle,
  FiCheckCircle,
  FiTrendingUp,
  FiTrendingDown,
  FiDollarSign,
  FiPieChart,
  FiBarChart2,
  FiFileText,
  FiShield,
  FiTarget,
  FiInfo,
  FiChevronRight
} from 'react-icons/fi';
import axios from 'axios';

// Portfolio Analysis Results Component
const PortfolioAnalysisResults = ({ result }) => {
  // Format percentage with arrow
  const formatPercentage = (value, includeSign = true) => {
    if (value === null || value === undefined) return 'N/A';

    const isPositive = value > 0;
    const formattedValue = Math.abs(value).toFixed(2);

    return (
      <HStack>
        {value !== 0 && <StatArrow type={isPositive ? 'increase' : 'decrease'} />}
        <Text color={isPositive ? 'green.500' : value < 0 ? 'red.500' : 'gray.500'}>
          {includeSign && isPositive ? '+' : ''}{formattedValue}%
        </Text>
      </HStack>
    );
  };

  return (
    <Card width="100%" mt={4}>
      <CardHeader bg="blue.50">
        <Flex align="center">
          <Icon as={FiPieChart} color="blue.500" boxSize={5} mr={2} />
          <Heading size="md">Portfolio Analysis Results</Heading>
          <Spacer />
          <Badge colorScheme="blue">{result.risk_analysis?.risk_profile || 'medium'} risk</Badge>
        </Flex>
      </CardHeader>
      <CardBody>
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Asset Allocation</Tab>
            <Tab>Performance</Tab>
            <Tab>Risk Analysis</Tab>
            <Tab>Recommendations</Tab>
          </TabList>

          <TabPanels>
            {/* Overview Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Portfolio Summary</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Total Value</StatLabel>
                    <StatNumber>${result.basic_analysis?.total_value?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Securities</StatLabel>
                    <StatNumber>{result.basic_analysis?.security_count || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Avg. Security Value</StatLabel>
                    <StatNumber>${result.basic_analysis?.average_security_value?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Largest Holdings</Heading>
                {result.basic_analysis?.largest_holdings?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Security</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Return</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.basic_analysis.largest_holdings.map((holding, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {holding.name || holding.security_name || 'Unknown'}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${holding.value?.toLocaleString() || 'N/A'}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {formatPercentage(holding.return)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No holdings information available</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Asset Allocation Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Current Asset Allocation</Heading>

                {Object.keys(result.asset_allocation?.current_allocation || {}).length > 0 ? (
                  <Box width="100%">
                    {Object.entries(result.asset_allocation.current_allocation).map(([assetType, percentage], index) => (
                      <Box key={index} mb={2}>
                        <Flex justify="space-between">
                          <Text>{assetType.charAt(0).toUpperCase() + assetType.slice(1)}</Text>
                          <Text>{percentage.toFixed(2)}%</Text>
                        </Flex>
                        <Progress
                          value={percentage}
                          max={100}
                          colorScheme={assetType === 'stocks' ? 'blue' :
                                      assetType === 'bonds' ? 'green' :
                                      assetType === 'cash' ? 'gray' :
                                      assetType === 'alternatives' ? 'purple' : 'teal'}
                          size="sm"
                          borderRadius="md"
                        />
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Text>No asset allocation information available</Text>
                )}

                <Divider />

                <Heading size="sm">Sector Allocation</Heading>
                {Object.keys(result.asset_allocation?.allocation_by_sector || {}).length > 0 ? (
                  <Box width="100%">
                    {Object.entries(result.asset_allocation.allocation_by_sector).map(([sector, percentage], index) => (
                      <Box key={index} mb={2}>
                        <Flex justify="space-between">
                          <Text>{sector.charAt(0).toUpperCase() + sector.slice(1)}</Text>
                          <Text>{percentage.toFixed(2)}%</Text>
                        </Flex>
                        <Progress value={percentage} max={100} colorScheme="blue" size="sm" borderRadius="md" />
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Text>No sector allocation information available</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Performance Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Performance Metrics</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Average Return</StatLabel>
                    <StatNumber>
                      {result.performance?.average_return !== null ?
                        formatPercentage(result.performance.average_return) : 'N/A'}
                    </StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Total Return</StatLabel>
                    <StatNumber>
                      {result.performance?.total_return !== null ?
                        formatPercentage(result.performance.total_return) : 'N/A'}
                    </StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Best Performers</Heading>
                {result.performance?.best_performers?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Security</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Return</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.performance.best_performers.map((security, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {security.name || security.security_name || 'Unknown'}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {formatPercentage(security.return)}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${security.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No performance information available</Text>
                )}

                <Divider />

                <Heading size="sm">Worst Performers</Heading>
                {result.performance?.worst_performers?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Security</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Return</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.performance.worst_performers.map((security, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {security.name || security.security_name || 'Unknown'}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {formatPercentage(security.return)}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${security.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No performance information available</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Risk Analysis Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Risk Assessment</Heading>

                <HStack width="100%" spacing={4}>
                  <Box p={4} borderWidth={1} borderRadius="md" width="50%">
                    <VStack align="start" spacing={2}>
                      <Text fontWeight="bold">Current Risk Level</Text>
                      <Badge
                        colorScheme={result.risk_analysis?.risk_level === 'low' ? 'green' :
                                    result.risk_analysis?.risk_level === 'medium' ? 'blue' :
                                    result.risk_analysis?.risk_level === 'high' ? 'red' : 'gray'}
                        fontSize="lg"
                        p={2}
                      >
                        {result.risk_analysis?.risk_level?.toUpperCase() || 'UNKNOWN'}
                      </Badge>
                    </VStack>
                  </Box>

                  <Box p={4} borderWidth={1} borderRadius="md" width="50%">
                    <VStack align="start" spacing={2}>
                      <Text fontWeight="bold">Target Risk Profile</Text>
                      <Badge
                        colorScheme={result.risk_analysis?.risk_profile === 'low' ? 'green' :
                                    result.risk_analysis?.risk_profile === 'medium' ? 'blue' :
                                    result.risk_analysis?.risk_profile === 'high' ? 'red' : 'gray'}
                        fontSize="lg"
                        p={2}
                      >
                        {result.risk_analysis?.risk_profile?.toUpperCase() || 'MEDIUM'}
                      </Badge>
                    </VStack>
                  </Box>
                </HStack>

                <Alert
                  status={result.risk_analysis?.risk_profile_match ? 'success' : 'warning'}
                  borderRadius="md"
                >
                  <AlertIcon />
                  {result.risk_analysis?.risk_profile_match ?
                    'Your portfolio risk level matches your target risk profile.' :
                    'Your portfolio risk level does not match your target risk profile. Consider adjusting your investments.'}
                </Alert>

                <Divider />

                <Heading size="sm">Concentration Risk</Heading>
                {result.risk_analysis?.concentration_risk?.length > 0 ? (
                  <Box width="100%">
                    <Alert status="warning" borderRadius="md" mb={4}>
                      <AlertIcon />
                      <Box>
                        <AlertTitle>Concentration Risk Detected</AlertTitle>
                        <AlertDescription>
                          The following securities exceed the recommended concentration threshold for your risk profile.
                        </AlertDescription>
                      </Box>
                    </Alert>

                    <Box width="100%" overflowX="auto">
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Security</th>
                            <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Percentage</th>
                            <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Threshold</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.risk_analysis.concentration_risk.map((risk, index) => (
                            <tr key={index}>
                              <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                                {risk.security_name || 'Unknown'}
                              </td>
                              <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                                {risk.percentage?.toFixed(2)}%
                              </td>
                              <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                                {risk.threshold?.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Box>
                  </Box>
                ) : (
                  <Text>No concentration risk detected</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Recommendations Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Investment Recommendations</Heading>

                {result.recommendations?.length > 0 ? (
                  <VStack align="start" spacing={4} width="100%">
                    {result.recommendations.map((recommendation, index) => (
                      <Alert
                        key={index}
                        status={recommendation.priority === 'high' ? 'error' :
                                recommendation.priority === 'medium' ? 'warning' : 'info'}
                        variant="left-accent"
                        borderRadius="md"
                        width="100%"
                      >
                        <Box>
                          <Flex align="center">
                            <AlertTitle>{recommendation.title}</AlertTitle>
                            <Spacer />
                            <Badge
                              colorScheme={recommendation.priority === 'high' ? 'red' :
                                        recommendation.priority === 'medium' ? 'yellow' : 'blue'}
                            >
                              {recommendation.priority.toUpperCase()}
                            </Badge>
                          </Flex>
                          <AlertDescription display="block">
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
            </TabPanel>
          </TabPanels>
        </Tabs>
      </CardBody>
    </Card>
  );
};

// Financial Statements Results Component
const FinancialStatementsResults = ({ result }) => {
  // Format percentage with arrow
  const formatPercentage = (value, includeSign = true) => {
    if (value === null || value === undefined) return 'N/A';

    const isPositive = value > 0;
    const formattedValue = Math.abs(value).toFixed(2);

    return (
      <HStack>
        {value !== 0 && <StatArrow type={isPositive ? 'increase' : 'decrease'} />}
        <Text color={isPositive ? 'green.500' : value < 0 ? 'red.500' : 'gray.500'}>
          {includeSign && isPositive ? '+' : ''}{formattedValue}%
        </Text>
      </HStack>
    );
  };

  return (
    <Card width="100%" mt={4}>
      <CardHeader bg="green.50">
        <Flex align="center">
          <Icon as={FiFileText} color="green.500" boxSize={5} mr={2} />
          <Heading size="md">Financial Statements Analysis</Heading>
        </Flex>
      </CardHeader>
      <CardBody>
        <Tabs variant="enclosed" colorScheme="green">
          <TabList>
            <Tab>Balance Sheet</Tab>
            <Tab>Income Statement</Tab>
            <Tab>Financial Ratios</Tab>
          </TabList>

          <TabPanels>
            {/* Balance Sheet Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Balance Sheet Summary</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Total Assets</StatLabel>
                    <StatNumber>${result.balance_sheet_analysis?.total_assets?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Total Liabilities</StatLabel>
                    <StatNumber>${result.balance_sheet_analysis?.total_liabilities?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Total Equity</StatLabel>
                    <StatNumber>${result.balance_sheet_analysis?.total_equity?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Key Ratios</Heading>
                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Current Ratio</StatLabel>
                    <StatNumber>{result.balance_sheet_analysis?.current_ratio?.toFixed(2) || 'N/A'}</StatNumber>
                    <StatHelpText>
                      {result.balance_sheet_analysis?.current_ratio > 1.5 ? 'Good' :
                       result.balance_sheet_analysis?.current_ratio > 1 ? 'Adequate' : 'Low'}
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Debt to Equity</StatLabel>
                    <StatNumber>{result.balance_sheet_analysis?.debt_to_equity?.toFixed(2) || 'N/A'}</StatNumber>
                    <StatHelpText>
                      {result.balance_sheet_analysis?.debt_to_equity < 1 ? 'Low leverage' :
                       result.balance_sheet_analysis?.debt_to_equity < 2 ? 'Moderate leverage' : 'High leverage'}
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Debt to Assets</StatLabel>
                    <StatNumber>{result.balance_sheet_analysis?.debt_to_assets?.toFixed(2) || 'N/A'}</StatNumber>
                    <StatHelpText>
                      {result.balance_sheet_analysis?.debt_to_assets < 0.4 ? 'Low debt' :
                       result.balance_sheet_analysis?.debt_to_assets < 0.6 ? 'Moderate debt' : 'High debt'}
                    </StatHelpText>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Major Assets</Heading>
                {result.balance_sheet_analysis?.major_assets?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Asset</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.balance_sheet_analysis.major_assets.map((asset, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {asset.name}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${asset.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No major assets information available</Text>
                )}

                <Heading size="sm">Major Liabilities</Heading>
                {result.balance_sheet_analysis?.major_liabilities?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Liability</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.balance_sheet_analysis.major_liabilities.map((liability, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {liability.name}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${liability.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No major liabilities information available</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Income Statement Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Income Statement Summary</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Total Revenue</StatLabel>
                    <StatNumber>${result.income_statement_analysis?.total_revenue?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Total Expenses</StatLabel>
                    <StatNumber>${result.income_statement_analysis?.total_expenses?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Net Profit</StatLabel>
                    <StatNumber>${result.income_statement_analysis?.net_profit?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Profitability Metrics</Heading>
                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Profit Margin</StatLabel>
                    <StatNumber>
                      {result.income_statement_analysis?.profit_margin !== null ?
                        formatPercentage(result.income_statement_analysis.profit_margin, false) : 'N/A'}
                    </StatNumber>
                    <StatHelpText>
                      {result.income_statement_analysis?.profit_margin > 15 ? 'Excellent' :
                       result.income_statement_analysis?.profit_margin > 10 ? 'Good' :
                       result.income_statement_analysis?.profit_margin > 5 ? 'Average' : 'Low'}
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Gross Margin</StatLabel>
                    <StatNumber>
                      {result.income_statement_analysis?.gross_margin !== null ?
                        formatPercentage(result.income_statement_analysis.gross_margin, false) : 'N/A'}
                    </StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Operating Margin</StatLabel>
                    <StatNumber>
                      {result.income_statement_analysis?.operating_margin !== null ?
                        formatPercentage(result.income_statement_analysis.operating_margin, false) : 'N/A'}
                    </StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Major Revenue Sources</Heading>
                {result.income_statement_analysis?.major_revenue_sources?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Source</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.income_statement_analysis.major_revenue_sources.map((source, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {source.name}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${source.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No major revenue sources information available</Text>
                )}

                <Heading size="sm">Major Expenses</Heading>
                {result.income_statement_analysis?.major_expenses?.length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Expense</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.income_statement_analysis.major_expenses.map((expense, index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {expense.name}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              ${expense.value?.toLocaleString() || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No major expenses information available</Text>
                )}
              </VStack>
            </TabPanel>

            {/* Financial Ratios Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Liquidity Ratios</Heading>
                {Object.keys(result.financial_ratios?.liquidity_ratios || {}).length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Ratio</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Interpretation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(result.financial_ratios.liquidity_ratios).map(([name, value], index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {value?.toFixed(2) || 'N/A'}
                            </td>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name === 'current_ratio' ?
                                (value > 1.5 ? 'Good liquidity' : value > 1 ? 'Adequate liquidity' : 'Poor liquidity') :
                                ''}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No liquidity ratios information available</Text>
                )}

                <Divider />

                <Heading size="sm">Profitability Ratios</Heading>
                {Object.keys(result.financial_ratios?.profitability_ratios || {}).length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Ratio</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Interpretation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(result.financial_ratios.profitability_ratios).map(([name, value], index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {formatPercentage(value, false)}
                            </td>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name === 'return_on_equity' ?
                                (value > 15 ? 'Excellent' : value > 10 ? 'Good' : value > 5 ? 'Average' : 'Poor') :
                                name === 'net_profit_margin' ?
                                (value > 15 ? 'Excellent' : value > 10 ? 'Good' : value > 5 ? 'Average' : 'Poor') :
                                ''}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No profitability ratios information available</Text>
                )}

                <Divider />

                <Heading size="sm">Solvency Ratios</Heading>
                {Object.keys(result.financial_ratios?.solvency_ratios || {}).length > 0 ? (
                  <Box width="100%" overflowX="auto">
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Ratio</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Value</th>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>Interpretation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(result.financial_ratios.solvency_ratios).map(([name, value], index) => (
                          <tr key={index}>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                            </td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {formatPercentage(value, false)}
                            </td>
                            <td style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #E2E8F0' }}>
                              {name === 'debt_to_equity' ?
                                (value < 50 ? 'Low leverage' : value < 100 ? 'Moderate leverage' : 'High leverage') :
                                name === 'debt_to_assets' ?
                                (value < 40 ? 'Low debt' : value < 60 ? 'Moderate debt' : 'High debt') :
                                ''}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Text>No solvency ratios information available</Text>
                )}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </CardBody>
    </Card>
  );
};

// Salary Analysis Results Component
const SalaryAnalysisResults = ({ result }) => {
  // Format percentage with arrow
  const formatPercentage = (value, includeSign = true) => {
    if (value === null || value === undefined) return 'N/A';

    const isPositive = value > 0;
    const formattedValue = Math.abs(value).toFixed(2);

    return (
      <HStack>
        {value !== 0 && <StatArrow type={isPositive ? 'increase' : 'decrease'} />}
        <Text color={isPositive ? 'green.500' : value < 0 ? 'red.500' : 'gray.500'}>
          {includeSign && isPositive ? '+' : ''}{formattedValue}%
        </Text>
      </HStack>
    );
  };

  return (
    <Card width="100%" mt={4}>
      <CardHeader bg="purple.50">
        <Flex align="center">
          <Icon as={FiDollarSign} color="purple.500" boxSize={5} mr={2} />
          <Heading size="md">Salary Analysis</Heading>
        </Flex>
      </CardHeader>
      <CardBody>
        <Tabs variant="enclosed" colorScheme="purple">
          <TabList>
            <Tab>Basic Analysis</Tab>
            <Tab>Pension & Savings</Tab>
            <Tab>Tax Analysis</Tab>
            <Tab>Recommendations</Tab>
          </TabList>

          <TabPanels>
            {/* Basic Analysis Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Salary Summary</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Gross Salary</StatLabel>
                    <StatNumber>${result.basic_analysis?.gross_salary?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Net Salary</StatLabel>
                    <StatNumber>${result.basic_analysis?.net_salary?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Deduction Rate</StatLabel>
                    <StatNumber>{formatPercentage(result.basic_analysis?.deduction_percentage, false)}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Salary Breakdown</Heading>
                <Box width="100%">
                  <Flex justify="space-between" mb={2}>
                    <Text fontWeight="bold">Gross Salary</Text>
                    <Text fontWeight="bold">${result.basic_analysis?.gross_salary?.toLocaleString() || 'N/A'}</Text>
                  </Flex>

                  <Divider mb={2} />

                  <Text fontWeight="bold" mb={2}>Deductions:</Text>

                  {Object.entries(result.tax_analysis || {}).map(([key, value]) => {
                    if (key !== 'tax_percentage' && key !== 'tax_bracket' && key !== 'total_tax' && value > 0) {
                      return (
                        <Flex key={key} justify="space-between" mb={1} pl={4}>
                          <Text>{key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</Text>
                          <Text color="red.500">-${value?.toLocaleString() || 'N/A'}</Text>
                        </Flex>
                      );
                    }
                    return null;
                  })}

                  {Object.entries(result.pension_analysis || {}).map(([key, value]) => {
                    if ((key === 'pension_contribution' || key === 'further_education_contribution') && value > 0) {
                      return (
                        <Flex key={key} justify="space-between" mb={1} pl={4}>
                          <Text>{key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</Text>
                          <Text color="red.500">-${value?.toLocaleString() || 'N/A'}</Text>
                        </Flex>
                      );
                    }
                    return null;
                  })}

                  <Flex justify="space-between" mt={2} fontWeight="bold">
                    <Text>Total Deductions</Text>
                    <Text color="red.500">-${result.basic_analysis?.deduction_total?.toLocaleString() || 'N/A'}</Text>
                  </Flex>

                  <Divider my={2} />

                  {result.basic_analysis?.addition_total > 0 && (
                    <>
                      <Text fontWeight="bold" mb={2}>Additions:</Text>

                      {Object.entries(result.basic_analysis?.additions || {}).map(([key, value]) => (
                        <Flex key={key} justify="space-between" mb={1} pl={4}>
                          <Text>{key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</Text>
                          <Text color="green.500">+${value?.toLocaleString() || 'N/A'}</Text>
                        </Flex>
                      ))}

                      <Flex justify="space-between" mt={2} fontWeight="bold">
                        <Text>Total Additions</Text>
                        <Text color="green.500">+${result.basic_analysis?.addition_total?.toLocaleString() || 'N/A'}</Text>
                      </Flex>

                      <Divider my={2} />
                    </>
                  )}

                  <Flex justify="space-between" fontWeight="bold">
                    <Text>Net Salary</Text>
                    <Text>${result.basic_analysis?.net_salary?.toLocaleString() || 'N/A'}</Text>
                  </Flex>
                </Box>
              </VStack>
            </TabPanel>

            {/* Pension & Savings Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Pension Contributions</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Pension Contribution</StatLabel>
                    <StatNumber>${result.pension_analysis?.pension_contribution?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Further Education</StatLabel>
                    <StatNumber>${result.pension_analysis?.further_education_contribution?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Total Saving</StatLabel>
                    <StatNumber>${result.pension_analysis?.total_saving?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Savings Analysis</Heading>

                <Box width="100%" p={4} borderWidth={1} borderRadius="md">
                  <VStack align="start" spacing={3} width="100%">
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Current Contribution Rate:</Text>
                      <Text>{formatPercentage(result.pension_analysis?.contribution_percentage, false)}</Text>
                    </Flex>

                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Recommended Contribution:</Text>
                      <Text>${result.pension_analysis?.recommended_contribution?.toLocaleString() || 'N/A'}</Text>
                    </Flex>

                    <Divider />

                    <Text fontWeight="bold">Contribution Status:</Text>
                    <Alert
                      status={result.pension_analysis?.contribution_percentage >= 15 ? 'success' : 'warning'}
                      borderRadius="md"
                    >
                      <AlertIcon />
                      {result.pension_analysis?.contribution_percentage >= 20 ?
                        'Excellent! Your pension contributions are at the recommended level.' :
                        result.pension_analysis?.contribution_percentage >= 15 ?
                        'Good. Your pension contributions are adequate, but could be increased for better retirement security.' :
                        'Your pension contributions are below recommended levels. Consider increasing your contributions.'}
                    </Alert>
                  </VStack>
                </Box>
              </VStack>
            </TabPanel>

            {/* Tax Analysis Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Tax Summary</Heading>

                <StatGroup width="100%">
                  <Stat>
                    <StatLabel>Income Tax</StatLabel>
                    <StatNumber>${result.tax_analysis?.income_tax?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Social Security</StatLabel>
                    <StatNumber>${result.tax_analysis?.social_security?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>

                  <Stat>
                    <StatLabel>Health Insurance</StatLabel>
                    <StatNumber>${result.tax_analysis?.health_insurance?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                </StatGroup>

                <Divider />

                <Heading size="sm">Tax Analysis</Heading>

                <Box width="100%" p={4} borderWidth={1} borderRadius="md">
                  <VStack align="start" spacing={3} width="100%">
                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Total Tax:</Text>
                      <Text>${result.tax_analysis?.total_tax?.toLocaleString() || 'N/A'}</Text>
                    </Flex>

                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Effective Tax Rate:</Text>
                      <Text>{formatPercentage(result.tax_analysis?.tax_percentage, false)}</Text>
                    </Flex>

                    <Flex justify="space-between" width="100%">
                      <Text fontWeight="bold">Tax Bracket:</Text>
                      <Badge
                        colorScheme={result.tax_analysis?.tax_bracket === 'low' ? 'green' :
                                    result.tax_analysis?.tax_bracket === 'medium' ? 'blue' : 'red'}
                      >
                        {result.tax_analysis?.tax_bracket?.toUpperCase() || 'UNKNOWN'}
                      </Badge>
                    </Flex>

                    <Divider />

                    <Text fontWeight="bold">Tax Breakdown:</Text>
                    <Box width="100%">
                      {Object.entries(result.tax_analysis || {}).map(([key, value]) => {
                        if (key !== 'tax_percentage' && key !== 'tax_bracket' && key !== 'total_tax' && value > 0) {
                          const percentage = result.basic_analysis?.gross_salary ?
                            (value / result.basic_analysis.gross_salary) * 100 : 0;

                          return (
                            <Box key={key} mb={2}>
                              <Flex justify="space-between">
                                <Text>{key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</Text>
                                <Text>${value?.toLocaleString() || 'N/A'} ({percentage.toFixed(1)}%)</Text>
                              </Flex>
                              <Progress
                                value={percentage}
                                max={result.tax_analysis?.tax_percentage || 100}
                                colorScheme="red"
                                size="sm"
                                borderRadius="md"
                              />
                            </Box>
                          );
                        }
                        return null;
                      })}
                    </Box>
                  </VStack>
                </Box>
              </VStack>
            </TabPanel>

            {/* Recommendations Tab */}
            <TabPanel>
              <VStack align="start" spacing={4} width="100%">
                <Heading size="sm">Financial Recommendations</Heading>

                {result.recommendations?.length > 0 ? (
                  <VStack align="start" spacing={4} width="100%">
                    {result.recommendations.map((recommendation, index) => (
                      <Alert
                        key={index}
                        status={recommendation.priority === 'high' ? 'error' :
                                recommendation.priority === 'medium' ? 'warning' : 'info'}
                        variant="left-accent"
                        borderRadius="md"
                        width="100%"
                      >
                        <Box>
                          <Flex align="center">
                            <AlertTitle>{recommendation.title}</AlertTitle>
                            <Spacer />
                            <Badge
                              colorScheme={recommendation.priority === 'high' ? 'red' :
                                        recommendation.priority === 'medium' ? 'yellow' : 'blue'}
                            >
                              {recommendation.priority.toUpperCase()}
                            </Badge>
                          </Flex>
                          <AlertDescription display="block">
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

                <Divider />

                <Heading size="sm">General Advice</Heading>
                <List spacing={3}>
                  <ListItem>
                    <ListIcon as={FiChevronRight} color="purple.500" />
                    <Text as="span" fontWeight="bold">Emergency Fund:</Text> Maintain 3-6 months of expenses in a liquid emergency fund.
                  </ListItem>
                  <ListItem>
                    <ListIcon as={FiChevronRight} color="purple.500" />
                    <Text as="span" fontWeight="bold">Debt Management:</Text> Pay off high-interest debt before focusing on additional savings.
                  </ListItem>
                  <ListItem>
                    <ListIcon as={FiChevronRight} color="purple.500" />
                    <Text as="span" fontWeight="bold">Tax Planning:</Text> Consider consulting with a tax professional to optimize your tax situation.
                  </ListItem>
                  <ListItem>
                    <ListIcon as={FiChevronRight} color="purple.500" />
                    <Text as="span" fontWeight="bold">Retirement Planning:</Text> Aim to save at least 15-20% of your income for retirement.
                  </ListItem>
                </List>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </CardBody>
    </Card>
  );
};

// Investment Suggestion Results Component
const InvestmentSuggestionResults = ({ result }) => {
  // Format percentage with arrow
  const formatPercentage = (value, includeSign = true) => {
    if (value === null || value === undefined) return 'N/A';

    const isPositive = value > 0;
    const formattedValue = Math.abs(value).toFixed(2);

    return (
      <HStack>
        {value !== 0 && <StatArrow type={isPositive ? 'increase' : 'decrease'} />}
        <Text color={isPositive ? 'green.500' : value < 0 ? 'red.500' : 'gray.500'}>
          {includeSign && isPositive ? '+' : ''}{formattedValue}%
        </Text>
      </HStack>
    );
  };

  return (
    <Card width="100%" mt={4}>
      <CardHeader bg="teal.50">
        <Flex align="center">
          <Icon as={FiTarget} color="teal.500" boxSize={5} mr={2} />
          <Heading size="md">Investment Suggestions</Heading>
          <Spacer />
          <Badge colorScheme="teal">{result.risk_profile || 'medium'} risk</Badge>
        </Flex>
      </CardHeader>
      <CardBody>
        <VStack align="start" spacing={4} width="100%">
          <Heading size="sm">Investment Summary</Heading>

          <StatGroup width="100%">
            <Stat>
              <StatLabel>Investment Amount</StatLabel>
              <StatNumber>${result.investment_amount?.toLocaleString() || 'N/A'}</StatNumber>
            </Stat>

            <Stat>
              <StatLabel>Risk Profile</StatLabel>
              <StatNumber>
                <Badge
                  colorScheme={result.risk_profile === 'low' ? 'green' :
                              result.risk_profile === 'medium' ? 'blue' : 'purple'}
                  fontSize="lg"
                  p={2}
                >
                  {result.risk_profile?.toUpperCase() || 'MEDIUM'}
                </Badge>
              </StatNumber>
            </Stat>
          </StatGroup>

          <Divider />

          <Heading size="sm">Target Asset Allocation</Heading>
          <Box width="100%">
            {Object.entries(result.target_allocation || {}).map(([assetType, percentage], index) => (
              <Box key={index} mb={3}>
                <Flex justify="space-between" mb={1}>
                  <HStack>
                    <Icon
                      as={assetType === 'stocks' ? FiTrendingUp :
                          assetType === 'bonds' ? FiShield :
                          assetType === 'cash' ? FiDollarSign :
                          assetType === 'alternatives' ? FiBarChart2 : FiInfo}
                      color={assetType === 'stocks' ? 'blue.500' :
                            assetType === 'bonds' ? 'green.500' :
                            assetType === 'cash' ? 'gray.500' :
                            assetType === 'alternatives' ? 'purple.500' : 'teal.500'}
                    />
                    <Text fontWeight="bold">{assetType.charAt(0).toUpperCase() + assetType.slice(1)}</Text>
                  </HStack>
                  <Text>
                    {percentage.toFixed(1)}% (${((percentage / 100) * result.investment_amount).toLocaleString()})
                  </Text>
                </Flex>
                <Progress
                  value={percentage}
                  max={100}
                  colorScheme={assetType === 'stocks' ? 'blue' :
                              assetType === 'bonds' ? 'green' :
                              assetType === 'cash' ? 'gray' :
                              assetType === 'alternatives' ? 'purple' : 'teal'}
                  size="md"
                  borderRadius="md"
                />
              </Box>
            ))}
          </Box>

          <Divider />

          <Heading size="sm">Investment Suggestions</Heading>

          {result.suggestions?.length > 0 ? (
            <Accordion allowMultiple width="100%">
              {result.suggestions.map((suggestion, index) => {
                if (suggestion.type === 'asset_type') {
                  return (
                    <AccordionItem key={index} borderWidth={1} borderRadius="md" mb={3}>
                      <AccordionButton
                        _expanded={{ bg: suggestion.asset_type === 'stocks' ? 'blue.50' :
                                      suggestion.asset_type === 'bonds' ? 'green.50' :
                                      suggestion.asset_type === 'cash' ? 'gray.50' :
                                      suggestion.asset_type === 'alternatives' ? 'purple.50' : 'teal.50' }}
                        borderRadius="md"
                      >
                        <Box flex="1" textAlign="left">
                          <HStack>
                            <Icon
                              as={suggestion.asset_type === 'stocks' ? FiTrendingUp :
                                  suggestion.asset_type === 'bonds' ? FiShield :
                                  suggestion.asset_type === 'cash' ? FiDollarSign :
                                  suggestion.asset_type === 'alternatives' ? FiBarChart2 : FiInfo}
                              color={suggestion.asset_type === 'stocks' ? 'blue.500' :
                                    suggestion.asset_type === 'bonds' ? 'green.500' :
                                    suggestion.asset_type === 'cash' ? 'gray.500' :
                                    suggestion.asset_type === 'alternatives' ? 'purple.500' : 'teal.500'}
                              mr={2}
                            />
                            <Text fontWeight="bold">{suggestion.title}</Text>
                          </HStack>
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                      <AccordionPanel pb={4}>
                        <VStack align="start" spacing={3} width="100%">
                          <Text>{suggestion.description}</Text>

                          <Flex justify="space-between" width="100%">
                            <Text fontWeight="bold">Allocation:</Text>
                            <Text>
                              {suggestion.allocation_percentage}% (${suggestion.allocation_amount?.toLocaleString()})
                            </Text>
                          </Flex>

                          <Divider />

                          <Text fontWeight="bold">Specific Suggestions:</Text>
                          <List spacing={2}>
                            {suggestion.specific_suggestions?.map((specific, i) => (
                              <ListItem key={i}>
                                <ListIcon as={FiChevronRight} color="teal.500" />
                                {specific}
                              </ListItem>
                            ))}
                          </List>
                        </VStack>
                      </AccordionPanel>
                    </AccordionItem>
                  );
                } else if (suggestion.type === 'general') {
                  return (
                    <AccordionItem key={index} borderWidth={1} borderRadius="md" mb={3}>
                      <AccordionButton _expanded={{ bg: 'blue.50' }} borderRadius="md">
                        <Box flex="1" textAlign="left">
                          <HStack>
                            <Icon as={FiInfo} color="blue.500" mr={2} />
                            <Text fontWeight="bold">{suggestion.title}</Text>
                          </HStack>
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                      <AccordionPanel pb={4}>
                        <VStack align="start" spacing={3} width="100%">
                          <Text>{suggestion.description}</Text>

                          <Divider />

                          <Text fontWeight="bold">General Advice:</Text>
                          <List spacing={2}>
                            {suggestion.specific_suggestions?.map((specific, i) => (
                              <ListItem key={i}>
                                <ListIcon as={FiChevronRight} color="blue.500" />
                                {specific}
                              </ListItem>
                            ))}
                          </List>
                        </VStack>
                      </AccordionPanel>
                    </AccordionItem>
                  );
                }
                return null;
              })}
            </Accordion>
          ) : (
            <Text>No investment suggestions available</Text>
          )}

          <Divider />

          <Alert status="info" borderRadius="md">
            <AlertIcon />
            <Box>
              <AlertTitle>Important Note</AlertTitle>
              <AlertDescription>
                These investment suggestions are based on your risk profile and current portfolio.
                Consider consulting with a financial advisor before making investment decisions.
              </AlertDescription>
            </Box>
          </Alert>
        </VStack>
      </CardBody>
    </Card>
  );
};

const FinancialAdvisorTool = ({ documentData }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisType, setAnalysisType] = useState('portfolio');
  const [riskProfile, setRiskProfile] = useState('medium');
  const [investmentAmount, setInvestmentAmount] = useState(100000);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const toast = useToast();

  const handleAnalyze = async () => {
    if (!documentData) {
      setError('No document data available. Please upload and process a document first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      // Send the analysis request to the API
      const response = await axios.post('/api/financial/financial-advice', {
        analysis_type: analysisType,
        document_data: documentData,
        risk_profile: riskProfile,
        investment_amount: investmentAmount
      });

      setAnalysisResult(response.data);
      toast({
        title: 'Analysis successful',
        description: `Financial analysis completed successfully`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error analyzing data:', err);
      setError(err.response?.data?.detail || 'Error analyzing data');
      toast({
        title: 'Analysis failed',
        description: err.response?.data?.detail || 'An error occurred while analyzing data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Financial Advisor Tool</Heading>
        <Text>Get financial analysis, accounting, and investment advice based on your documents.</Text>

        <Card width="100%">
          <CardHeader>
            <Heading size="md">Analysis Options</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="start" width="100%">
              <FormControl>
                <FormLabel>Analysis Type</FormLabel>
                <Select
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                >
                  <option value="portfolio">Portfolio Analysis</option>
                  <option value="financial_statements">Financial Statements Analysis</option>
                  <option value="salary">Salary Analysis</option>
                  <option value="investment_suggestion">Investment Suggestions</option>
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Select the type of financial analysis to perform
                </Text>
              </FormControl>

              {analysisType === 'portfolio' || analysisType === 'investment_suggestion' ? (
                <FormControl>
                  <FormLabel>Risk Profile</FormLabel>
                  <RadioGroup value={riskProfile} onChange={setRiskProfile}>
                    <Stack direction="row" spacing={5}>
                      <Radio value="low">
                        <HStack>
                          <Text>Low Risk</Text>
                          <Badge colorScheme="green">Conservative</Badge>
                        </HStack>
                      </Radio>
                      <Radio value="medium">
                        <HStack>
                          <Text>Medium Risk</Text>
                          <Badge colorScheme="blue">Balanced</Badge>
                        </HStack>
                      </Radio>
                      <Radio value="high">
                        <HStack>
                          <Text>High Risk</Text>
                          <Badge colorScheme="purple">Aggressive</Badge>
                        </HStack>
                      </Radio>
                    </Stack>
                  </RadioGroup>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Select your risk tolerance level
                  </Text>
                </FormControl>
              ) : null}

              {analysisType === 'investment_suggestion' && (
                <FormControl>
                  <FormLabel>Investment Amount</FormLabel>
                  <NumberInput
                    value={investmentAmount}
                    onChange={(valueString) => setInvestmentAmount(parseFloat(valueString))}
                    min={1000}
                    max={10000000}
                    step={1000}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Enter the amount you want to invest
                  </Text>
                </FormControl>
              )}

              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>Analysis Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                leftIcon={<FiActivity />}
                colorScheme="blue"
                onClick={handleAnalyze}
                isLoading={isAnalyzing}
                loadingText="Analyzing..."
                width="full"
                mt={2}
                isDisabled={!documentData}
              >
                Analyze
              </Button>

              {!documentData && (
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>No Data Available</AlertTitle>
                  <AlertDescription>
                    Please upload and process a document first to perform financial analysis.
                  </AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {analysisResult && analysisType === 'portfolio' && (
          <PortfolioAnalysisResults result={analysisResult} />
        )}

        {analysisResult && analysisType === 'financial_statements' && (
          <FinancialStatementsResults result={analysisResult} />
        )}

        {analysisResult && analysisType === 'salary' && (
          <SalaryAnalysisResults result={analysisResult} />
        )}

        {analysisResult && analysisType === 'investment_suggestion' && (
          <InvestmentSuggestionResults result={analysisResult} />
        )}
      </VStack>
    </Box>
  );
};

export default FinancialAdvisorTool;
