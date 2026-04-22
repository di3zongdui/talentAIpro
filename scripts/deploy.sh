#!/bin/bash
# TalentAI Pro - Deployment Script
# Usage: ./scripts/deploy.sh [production|staging|dev]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_NAME="TalentAI-Pro"
COMPOSE_FILE="docker-compose.yml"
TAG=${1:-latest}

echo -e "${GREEN}=== TalentAI Pro Deployment ===${NC}"
echo "Environment: $TAG"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed.${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is required but not installed.${NC}"; exit 1; }

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data logs ssl

# Load environment variables
if [ -f .env ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Using defaults.${NC}"
fi

# Build and deploy
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f $COMPOSE_FILE build --pull

echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down || true

echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Health check
echo -e "${YELLOW}Performing health check...${NC}"
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}API is healthy!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Health check failed. Checking logs...${NC}"
        docker-compose -f $COMPOSE_FILE logs api
        exit 1
    fi
    echo "Waiting for API... ($i/30)"
    sleep 2
done

# Show status
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
docker-compose -f $COMPOSE_FILE ps
echo ""
echo -e "${GREEN}API: http://localhost:8000${NC}"
echo -e "${GREEN}Docs: http://localhost:8000/docs${NC}"
echo ""
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "To stop: docker-compose -f $COMPOSE_FILE down"
