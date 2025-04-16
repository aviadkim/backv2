
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
    console.log(`Toast: ${title} - ${description} (${status})`);
    // In a real implementation, this would show a toast notification
    // For now, we just log to the console
  };
};
