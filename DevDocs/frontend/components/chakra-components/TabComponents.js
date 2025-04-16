
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
