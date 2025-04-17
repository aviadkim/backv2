/**
 * Script to fix Chakra UI imports in the project
 * 
 * This script creates a custom implementation of Chakra UI components
 * that are not exported directly from the main package in v3.16.0
 */

const fs = require('fs');
const path = require('path');

// Create the chakra-components directory if it doesn't exist
const componentsDir = path.join(__dirname, 'DevDocs', 'frontend', 'components', 'chakra-components');
if (!fs.existsSync(componentsDir)) {
  fs.mkdirSync(componentsDir, { recursive: true });
}

// Create custom table components
const tableComponents = `
import { Box } from '@chakra-ui/react';

export const TableContainer = ({ children, ...props }) => (
  <Box overflowX="auto" {...props}>
    {children}
  </Box>
);

export const Thead = ({ children, ...props }) => (
  <Box as="thead" {...props}>
    {children}
  </Box>
);

export const Tbody = ({ children, ...props }) => (
  <Box as="tbody" {...props}>
    {children}
  </Box>
);

export const Tr = ({ children, ...props }) => (
  <Box as="tr" display="table-row" {...props}>
    {children}
  </Box>
);

export const Th = ({ children, ...props }) => (
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

export const Td = ({ children, ...props }) => (
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
`;

// Create custom tab components
const tabComponents = `
import { Box } from '@chakra-ui/react';

export const TabList = ({ children, ...props }) => (
  <Box
    as="div"
    display="flex"
    borderBottom="1px"
    borderColor="gray.200"
    {...props}
  >
    {children}
  </Box>
);

export const Tab = ({ children, isSelected, onClick, ...props }) => (
  <Box
    as="button"
    px="4"
    py="2"
    fontWeight={isSelected ? "bold" : "normal"}
    borderBottom={isSelected ? "2px solid" : "none"}
    borderColor={isSelected ? "blue.500" : "transparent"}
    color={isSelected ? "blue.500" : "gray.600"}
    _hover={{ color: "blue.400" }}
    onClick={onClick}
    {...props}
  >
    {children}
  </Box>
);

export const TabPanels = ({ children, ...props }) => (
  <Box pt="4" {...props}>
    {children}
  </Box>
);

export const TabPanel = ({ children, ...props }) => (
  <Box {...props}>
    {children}
  </Box>
);
`;

// Create custom form components
const formComponents = `
import { Box, Input, FormHelperText } from '@chakra-ui/react';

export const FormControl = ({ children, isInvalid, isRequired, ...props }) => (
  <Box mb="4" {...props}>
    {children}
  </Box>
);

export const FormLabel = ({ children, htmlFor, ...props }) => (
  <Box
    as="label"
    fontSize="md"
    fontWeight="medium"
    htmlFor={htmlFor}
    mb="2"
    {...props}
  >
    {children}
  </Box>
);
`;

// Create custom number input components
const numberInputComponents = `
import { Box, Input } from '@chakra-ui/react';
import { useState } from 'react';

export const NumberInput = ({ children, defaultValue, min, max, onChange, ...props }) => {
  const [value, setValue] = useState(defaultValue || '');
  
  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };
  
  return (
    <Box position="relative" {...props}>
      <Input
        type="number"
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
      />
      {children}
    </Box>
  );
};

export const NumberInputField = ({ ...props }) => (
  <Input type="number" {...props} />
);

export const NumberInputStepper = ({ children, ...props }) => (
  <Box
    display="flex"
    flexDirection="column"
    position="absolute"
    right="0"
    top="0"
    bottom="0"
    width="24px"
    {...props}
  >
    {children}
  </Box>
);

export const NumberIncrementStepper = ({ onClick, ...props }) => (
  <Box
    display="flex"
    alignItems="center"
    justifyContent="center"
    borderTop="1px solid"
    borderColor="inherit"
    cursor="pointer"
    fontSize="xs"
    height="50%"
    position="relative"
    userSelect="none"
    _hover={{ bg: "gray.200" }}
    onClick={onClick}
    {...props}
  >
    +
  </Box>
);

export const NumberDecrementStepper = ({ onClick, ...props }) => (
  <Box
    display="flex"
    alignItems="center"
    justifyContent="center"
    borderBottom="1px solid"
    borderColor="inherit"
    cursor="pointer"
    fontSize="xs"
    height="50%"
    position="relative"
    userSelect="none"
    _hover={{ bg: "gray.200" }}
    onClick={onClick}
    {...props}
  >
    -
  </Box>
);
`;

// Create custom utility components
const utilityComponents = `
import { Box } from '@chakra-ui/react';

export const Divider = ({ orientation = 'horizontal', ...props }) => (
  <Box
    as="hr"
    borderWidth={orientation === 'horizontal' ? '0 0 1px 0' : '0 1px 0 0'}
    borderStyle="solid"
    borderColor="gray.200"
    my={orientation === 'horizontal' ? 2 : 0}
    mx={orientation === 'horizontal' ? 0 : 2}
    height={orientation === 'horizontal' ? 'auto' : '100%'}
    {...props}
  />
);

export const useToast = () => {
  return ({ title, description, status, duration, isClosable }) => {
    console.log(\`Toast: \${title} - \${description} (\${status})\`);
    // In a real implementation, this would show a toast notification
    // For now, we just log to the console
  };
};
`;

// Create the component files
fs.writeFileSync(path.join(componentsDir, 'TableComponents.js'), tableComponents);
fs.writeFileSync(path.join(componentsDir, 'TabComponents.js'), tabComponents);
fs.writeFileSync(path.join(componentsDir, 'FormComponents.js'), formComponents);
fs.writeFileSync(path.join(componentsDir, 'NumberInputComponents.js'), numberInputComponents);
fs.writeFileSync(path.join(componentsDir, 'UtilityComponents.js'), utilityComponents);

// Create an index file to export all components
const indexFile = `
// Table components
export { TableContainer, Thead, Tbody, Tr, Th, Td } from './TableComponents';

// Tab components
export { TabList, Tab, TabPanels, TabPanel } from './TabComponents';

// Form components
export { FormControl, FormLabel } from './FormComponents';

// Number input components
export { 
  NumberInput, 
  NumberInputField, 
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper
} from './NumberInputComponents';

// Utility components
export { Divider, useToast } from './UtilityComponents';
`;

fs.writeFileSync(path.join(componentsDir, 'index.js'), indexFile);

console.log('Chakra UI component fixes created successfully!');
