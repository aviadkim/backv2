
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
