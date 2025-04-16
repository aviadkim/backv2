
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
