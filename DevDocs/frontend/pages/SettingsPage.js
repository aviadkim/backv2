import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Input,
  Button,
  Switch,
  VStack,
  HStack,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Select
} from '@chakra-ui/react';

// Import components that need to be imported separately
import { FormControl, FormLabel, Divider, useToast } from '../components/chakra-components';

const SettingsPage = () => {
  const [apiKey, setApiKey] = useState('');
  const [language, setLanguage] = useState('heb+eng');
  const [enableNotifications, setEnableNotifications] = useState(true);
  const [enableAutoAnalysis, setEnableAutoAnalysis] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const toast = useToast();

  const handleSaveAPIKey = () => {
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: 'API key saved',
        description: 'Your OpenRouter API key has been saved successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    }, 1000);
  };

  const handleSavePreferences = () => {
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: 'Preferences saved',
        description: 'Your preferences have been saved successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    }, 1000);
  };

  return (
    <Box>
      <Heading mb={6}>Settings</Heading>
      <Text mb={6}>Configure application settings and preferences.</Text>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">API Configuration</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="start">
              <FormControl>
                <FormLabel>OpenRouter API Key</FormLabel>
                <Input
                  type="password"
                  placeholder="sk-or-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Your OpenRouter API key for accessing AI capabilities
                </Text>
              </FormControl>

              <Button
                colorScheme="blue"
                onClick={handleSaveAPIKey}
                isLoading={isLoading}
                isDisabled={!apiKey}
              >
                Save API Key
              </Button>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Application Preferences</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="start">
              <FormControl>
                <FormLabel>Default Language</FormLabel>
                <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  <option value="heb+eng">Hebrew + English</option>
                  <option value="eng">English</option>
                  <option value="heb">Hebrew</option>
                </Select>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Default language for OCR and document processing
                </Text>
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="notifications" mb="0">
                  Enable Notifications
                </FormLabel>
                <Switch
                  id="notifications"
                  isChecked={enableNotifications}
                  onChange={() => setEnableNotifications(!enableNotifications)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-analysis" mb="0">
                  Auto-Analyze Documents
                </FormLabel>
                <Switch
                  id="auto-analysis"
                  isChecked={enableAutoAnalysis}
                  onChange={() => setEnableAutoAnalysis(!enableAutoAnalysis)}
                />
              </FormControl>

              <Button
                colorScheme="blue"
                onClick={handleSavePreferences}
                isLoading={isLoading}
              >
                Save Preferences
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Card mt={6}>
        <CardHeader>
          <Heading size="md">Account Information</Heading>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <Box>
              <Text fontWeight="bold">User</Text>
              <Text>demo@example.com</Text>
            </Box>

            <Box>
              <Text fontWeight="bold">Plan</Text>
              <Text>Free Tier</Text>
            </Box>

            <Box>
              <Text fontWeight="bold">Documents Processed</Text>
              <Text>12 / 50</Text>
            </Box>

            <Box>
              <Text fontWeight="bold">API Calls</Text>
              <Text>87 / 500</Text>
            </Box>
          </SimpleGrid>

          <Divider my={4} />

          <HStack spacing={4}>
            <Button colorScheme="blue" variant="outline">
              Upgrade Plan
            </Button>
            <Button colorScheme="red" variant="outline">
              Delete Account
            </Button>
          </HStack>
        </CardBody>
      </Card>
    </Box>
  );
};

export default SettingsPage;
