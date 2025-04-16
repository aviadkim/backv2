
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
