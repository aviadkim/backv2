import React from 'react';
import { 
  Box, 
  Flex, 
  HStack, 
  IconButton, 
  Button, 
  Menu, 
  MenuButton, 
  MenuList, 
  MenuItem, 
  MenuDivider, 
  useDisclosure, 
  useColorModeValue, 
  Stack, 
  useColorMode, 
  Text,
  Icon
} from '@chakra-ui/react';
import { 
  HamburgerIcon, 
  CloseIcon, 
  ChevronDownIcon, 
  MoonIcon, 
  SunIcon 
} from '@chakra-ui/icons';
import { 
  FiHome, 
  FiUpload, 
  FiFileText, 
  FiPieChart, 
  FiSettings, 
  FiUser, 
  FiLogOut 
} from 'react-icons/fi';
import { Link } from 'react-router-dom';

const NavLink = ({ children, icon, to, ...rest }) => {
  return (
    <Box
      as={Link}
      px={2}
      py={1}
      rounded={'md'}
      _hover={{
        textDecoration: 'none',
        bg: useColorModeValue('gray.200', 'gray.700'),
      }}
      to={to}
      display="flex"
      alignItems="center"
      {...rest}
    >
      {icon && <Icon as={icon} mr={2} />}
      {children}
    </Box>
  );
};

const Navigation = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  
  const Links = [
    { name: 'Dashboard', icon: FiHome, to: '/' },
    { name: 'Upload Documents', icon: FiUpload, to: '/upload' },
    { name: 'Financial Analysis', icon: FiPieChart, to: '/financial' },
    { name: 'Reports', icon: FiFileText, to: '/reports' },
    { name: 'Settings', icon: FiSettings, to: '/settings' },
  ];
  
  return (
    <Box bg={useColorModeValue('white', 'gray.900')} px={4} boxShadow="sm">
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
        <IconButton
          size={'md'}
          icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
          aria-label={'Open Menu'}
          display={{ md: 'none' }}
          onClick={isOpen ? onClose : onOpen}
        />
        <HStack spacing={8} alignItems={'center'}>
          <Box fontWeight="bold" fontSize="xl">DevDocs</Box>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            {Links.map((link) => (
              <NavLink key={link.name} icon={link.icon} to={link.to}>
                {link.name}
              </NavLink>
            ))}
          </HStack>
        </HStack>
        <Flex alignItems={'center'}>
          <Button onClick={toggleColorMode} mr={4}>
            {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          </Button>
          
          <Menu>
            <MenuButton
              as={Button}
              rounded={'full'}
              variant={'link'}
              cursor={'pointer'}
              minW={0}
            >
              <Flex align="center">
                <Icon as={FiUser} mr={2} />
                <Text display={{ base: 'none', md: 'block' }}>User</Text>
                <ChevronDownIcon ml={2} />
              </Flex>
            </MenuButton>
            <MenuList>
              <MenuItem icon={<Icon as={FiUser} />}>Profile</MenuItem>
              <MenuItem icon={<Icon as={FiSettings} />}>Settings</MenuItem>
              <MenuDivider />
              <MenuItem icon={<Icon as={FiLogOut} />}>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <Stack as={'nav'} spacing={4}>
            {Links.map((link) => (
              <NavLink key={link.name} icon={link.icon} to={link.to}>
                {link.name}
              </NavLink>
            ))}
          </Stack>
        </Box>
      ) : null}
    </Box>
  );
};

export default Navigation;
