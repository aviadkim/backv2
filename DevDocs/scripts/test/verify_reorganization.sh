#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Verifying codebase reorganization...${NC}"

# Check if symbolic links are working
echo -e "${BLUE}Checking symbolic links...${NC}"
if [ ! -L "docker-compose.yml" ] || [ ! -e "docker-compose.yml" ]; then
  echo -e "${RED}docker-compose.yml symbolic link is broken${NC}"
  exit 1
fi

if [ ! -L "Dockerfile.backend" ] || [ ! -e "Dockerfile.backend" ]; then
  echo -e "${RED}Dockerfile.backend symbolic link is broken${NC}"
  exit 1
fi

if [ ! -L "Dockerfile.frontend" ] || [ ! -e "Dockerfile.frontend" ]; then
  echo -e "${RED}Dockerfile.frontend symbolic link is broken${NC}"
  exit 1
fi

if [ ! -L "Dockerfile.mcp" ] || [ ! -e "Dockerfile.mcp" ]; then
  echo -e "${RED}Dockerfile.mcp symbolic link is broken${NC}"
  exit 1
fi

echo -e "${GREEN}All symbolic links are working correctly${NC}"

# Check if docker-compose.yml has been updated with new Dockerfile paths
echo -e "${BLUE}Checking docker-compose.yml for updated Dockerfile paths...${NC}"
if ! grep -q "dockerfile: docker/dockerfiles/Dockerfile.frontend" docker/compose/docker-compose.yml; then
  echo -e "${RED}docker-compose.yml does not reference the new Dockerfile.frontend path${NC}"
  exit 1
fi

if ! grep -q "dockerfile: docker/dockerfiles/Dockerfile.backend" docker/compose/docker-compose.yml; then
  echo -e "${RED}docker-compose.yml does not reference the new Dockerfile.backend path${NC}"
  exit 1
fi

if ! grep -q "dockerfile: docker/dockerfiles/Dockerfile.mcp" docker/compose/docker-compose.yml; then
  echo -e "${RED}docker-compose.yml does not reference the new Dockerfile.mcp path${NC}"
  exit 1
fi

echo -e "${GREEN}docker-compose.yml has been updated with new Dockerfile paths${NC}"

# Test if docker-compose can parse the updated docker-compose.yml
echo -e "${BLUE}Testing if docker-compose can parse the updated docker-compose.yml...${NC}"
if ! docker-compose config > /dev/null 2>&1; then
  echo -e "${RED}docker-compose cannot parse the updated docker-compose.yml${NC}"
  exit 1
fi

echo -e "${GREEN}docker-compose can parse the updated docker-compose.yml${NC}"

# Final verification message
echo -e "${GREEN}Codebase reorganization verification completed successfully!${NC}"
echo -e "${YELLOW}The codebase has been successfully reorganized with the following structure:${NC}"
echo -e "${BLUE}scripts/${NC} - Shell scripts and other executable files"
echo -e "${BLUE}docs/${NC} - Documentation files"
echo -e "${BLUE}docker/${NC} - Docker-related files"
echo -e "${BLUE}config/${NC} - Configuration files"
echo -e "${BLUE}Symbolic links${NC} have been created in the root directory for backward compatibility"

echo -e "\n${YELLOW}To test the reorganized codebase, run:${NC}"
echo -e "${BLUE}./docker-start.sh${NC} - To start the Docker containers"
echo -e "${BLUE}./start.sh${NC} - To start the application without Docker"