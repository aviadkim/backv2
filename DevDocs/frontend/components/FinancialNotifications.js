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
  Flex,
  Spacer,
  Switch,
  Input,
  Collapse,
  useDisclosure
} from '@chakra-ui/react';
import {
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
} from '@chakra-ui/react';

// Create custom increment/decrement steppers since they're not exported directly
const NumberIncrementStepper = (props) => (
  <Box
    {...props}
    as="div"
    display="flex"
    alignItems="center"
    justifyContent="center"
    borderTop="1px solid"
    borderColor="inherit"
    cursor="pointer"
    fontSize="xs"
    height="50%"
    position="absolute"
    right="0"
    top="0"
    userSelect="none"
    width="100%"
    _hover={{ bg: "gray.200" }}
    onClick={props.onClick}
  >
    +
  </Box>
);

const NumberDecrementStepper = (props) => (
  <Box
    {...props}
    as="div"
    display="flex"
    alignItems="center"
    justifyContent="center"
    borderBottom="1px solid"
    borderColor="inherit"
    cursor="pointer"
    fontSize="xs"
    height="50%"
    position="absolute"
    right="0"
    bottom="0"
    userSelect="none"
    width="100%"
    _hover={{ bg: "gray.200" }}
    onClick={props.onClick}
  >
    -
  </Box>
);
import {
  FiBell,
  FiAlertCircle,
  FiCheckCircle,
  FiAlertTriangle,
  FiInfo,
  FiSettings,
  FiEye,
  FiEyeOff,
  FiChevronDown,
  FiChevronUp
} from 'react-icons/fi';
import axios from 'axios';

const FinancialNotifications = ({ documentData }) => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userSettings, setUserSettings] = useState({
    portfolio_value_threshold: 1000000,
    portfolio_change_threshold: 5.0,
    security_return_threshold: 10.0,
    abnormal_change_threshold: 20.0,
    watched_securities: []
  });
  const [watchedSecurity, setWatchedSecurity] = useState('');

  const { isOpen, onToggle } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    if (documentData) {
      generateNotifications();
    }
  }, [documentData]);

  const generateNotifications = async () => {
    if (!documentData) {
      setError('No document data available. Please upload and process a document first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Send the request to the API
      const response = await axios.post('/api/financial/notifications', {
        document_data: documentData,
        user_settings: userSettings
      });

      setNotifications(response.data.notifications || []);

      toast({
        title: 'Notifications generated',
        description: `Generated ${response.data.notifications?.length || 0} notifications`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error generating notifications:', err);
      setError(err.response?.data?.detail || 'Error generating notifications');
      toast({
        title: 'Error generating notifications',
        description: err.response?.data?.detail || 'An error occurred while generating notifications',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (setting, value) => {
    setUserSettings({
      ...userSettings,
      [setting]: value
    });
  };

  const addWatchedSecurity = () => {
    if (watchedSecurity && !userSettings.watched_securities.includes(watchedSecurity)) {
      setUserSettings({
        ...userSettings,
        watched_securities: [...userSettings.watched_securities, watchedSecurity]
      });
      setWatchedSecurity('');
    }
  };

  const removeWatchedSecurity = (security) => {
    setUserSettings({
      ...userSettings,
      watched_securities: userSettings.watched_securities.filter(s => s !== security)
    });
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'red';
      case 'medium':
        return 'orange';
      case 'low':
        return 'blue';
      default:
        return 'gray';
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'portfolio_threshold':
      case 'abnormal_change':
        return FiAlertTriangle;
      case 'security_performance':
      case 'expiring_security':
        return FiAlertCircle;
      case 'document_processing':
        return FiCheckCircle;
      case 'custom_alert':
        return FiBell;
      default:
        return FiInfo;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Box p={5} width="100%">
      <VStack spacing={6} align="start" width="100%">
        <Heading size="lg">Financial Notifications</Heading>
        <Text>Receive alerts and notifications about your financial documents.</Text>

        <Card width="100%">
          <CardHeader>
            <Flex align="center">
              <Heading size="md">Notification Settings</Heading>
              <Spacer />
              <Button
                rightIcon={isOpen ? <FiChevronUp /> : <FiChevronDown />}
                onClick={onToggle}
                variant="ghost"
              >
                {isOpen ? 'Hide' : 'Show'}
              </Button>
            </Flex>
          </CardHeader>
          <Collapse in={isOpen} animateOpacity>
            <CardBody>
              <VStack spacing={4} align="start" width="100%">
                <FormControl>
                  <FormLabel>Portfolio Value Threshold</FormLabel>
                  <NumberInput
                    value={userSettings.portfolio_value_threshold}
                    onChange={(valueString) => handleSettingChange('portfolio_value_threshold', parseFloat(valueString))}
                    min={0}
                    step={10000}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Alert when portfolio value falls below this threshold
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Portfolio Change Threshold (%)</FormLabel>
                  <NumberInput
                    value={userSettings.portfolio_change_threshold}
                    onChange={(valueString) => handleSettingChange('portfolio_change_threshold', parseFloat(valueString))}
                    min={0}
                    max={100}
                    step={0.5}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Alert when portfolio changes by this percentage
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Security Return Threshold (%)</FormLabel>
                  <NumberInput
                    value={userSettings.security_return_threshold}
                    onChange={(valueString) => handleSettingChange('security_return_threshold', parseFloat(valueString))}
                    min={0}
                    max={100}
                    step={0.5}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Alert when a security's return exceeds this percentage
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Abnormal Change Threshold (%)</FormLabel>
                  <NumberInput
                    value={userSettings.abnormal_change_threshold}
                    onChange={(valueString) => handleSettingChange('abnormal_change_threshold', parseFloat(valueString))}
                    min={0}
                    max={100}
                    step={0.5}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Alert when a security changes by this percentage
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Watched Securities</FormLabel>
                  <HStack>
                    <Input
                      value={watchedSecurity}
                      onChange={(e) => setWatchedSecurity(e.target.value)}
                      placeholder="Enter ISIN code (e.g., US0378331005)"
                    />
                    <Button onClick={addWatchedSecurity}>Add</Button>
                  </HStack>
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Add securities to watch (using ISIN codes)
                  </Text>
                </FormControl>

                {userSettings.watched_securities.length > 0 && (
                  <Box width="100%" mt={2}>
                    <Text fontWeight="bold">Watched Securities:</Text>
                    <HStack mt={2} flexWrap="wrap">
                      {userSettings.watched_securities.map((security, index) => (
                        <Badge
                          key={index}
                          colorScheme="blue"
                          p={2}
                          borderRadius="md"
                          display="flex"
                          alignItems="center"
                        >
                          {security}
                          <Icon
                            as={FiEyeOff}
                            ml={2}
                            cursor="pointer"
                            onClick={() => removeWatchedSecurity(security)}
                          />
                        </Badge>
                      ))}
                    </HStack>
                  </Box>
                )}

                <Button
                  leftIcon={<FiBell />}
                  colorScheme="blue"
                  onClick={generateNotifications}
                  isLoading={isLoading}
                  loadingText="Generating..."
                  width="full"
                  mt={2}
                  isDisabled={!documentData}
                >
                  Generate Notifications
                </Button>
              </VStack>
            </CardBody>
          </Collapse>
        </Card>

        {error && (
          <HStack width="100%" color="red.500">
            <Icon as={FiAlertCircle} />
            <Text>{error}</Text>
          </HStack>
        )}

        {!documentData && (
          <Card width="100%" bg="orange.50">
            <CardBody>
              <HStack>
                <Icon as={FiInfo} color="orange.500" />
                <Text>Please upload and process a document first to generate notifications.</Text>
              </HStack>
            </CardBody>
          </Card>
        )}

        {notifications.length > 0 ? (
          <VStack spacing={4} width="100%">
            <Heading size="md">Notifications ({notifications.length})</Heading>

            {notifications.map((notification, index) => (
              <Card key={index} width="100%" borderLeft="4px solid" borderLeftColor={`${getPriorityColor(notification.priority)}.500`}>
                <CardBody>
                  <HStack align="start" spacing={4}>
                    <Icon
                      as={getNotificationIcon(notification.type)}
                      color={`${getPriorityColor(notification.priority)}.500`}
                      boxSize={6}
                    />
                    <Box flex="1">
                      <Flex align="center" mb={1}>
                        <Heading size="sm">{notification.title}</Heading>
                        <Spacer />
                        <Badge colorScheme={getPriorityColor(notification.priority)}>
                          {notification.priority}
                        </Badge>
                      </Flex>
                      <Text>{notification.message}</Text>
                      <Text fontSize="sm" color="gray.500" mt={2}>
                        {formatDate(notification.created_at)}
                      </Text>
                    </Box>
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        ) : (
          <Card width="100%" bg="gray.50">
            <CardBody>
              <VStack>
                <Icon as={FiBell} boxSize={8} color="gray.400" />
                <Text>No notifications yet</Text>
                <Button
                  leftIcon={<FiBell />}
                  colorScheme="blue"
                  onClick={generateNotifications}
                  isLoading={isLoading}
                  loadingText="Generating..."
                  isDisabled={!documentData}
                >
                  Generate Notifications
                </Button>
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default FinancialNotifications;
