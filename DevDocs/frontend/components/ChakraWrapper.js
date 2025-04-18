import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';

// Use the default theme instead of a custom theme
const ChakraWrapper = ({ children }) => {
  return (
    <ChakraProvider>
      {children}
    </ChakraProvider>
  );
};

export default ChakraWrapper;
