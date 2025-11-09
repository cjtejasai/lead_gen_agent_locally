#!/bin/bash

# Ayka Lead Generation Platform - Quick Start Script
# This script helps you get started quickly with the platform

set -e

echo "=========================================="
echo "  Ayka Lead Generation Platform Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env from example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${RED}⚠ Please edit backend/.env and add your API keys${NC}"
    echo ""
fi

if [ ! -f "frontend/.env.local" ]; then
    echo -e "${YELLOW}Creating frontend/.env.local...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo -e "${GREEN}✓ Frontend environment configured${NC}"
    echo ""
fi

# Start Docker services
echo -e "${GREEN}Starting Docker services...${NC}"
docker-compose up -d postgres neo4j redis

echo ""
echo -e "${YELLOW}Waiting for services to be ready (30 seconds)...${NC}"
sleep 30

# Check if services are running
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
fi

if docker-compose ps | grep -q "neo4j.*Up"; then
    echo -e "${GREEN}✓ Neo4j is running${NC}"
else
    echo -e "${RED}✗ Neo4j failed to start${NC}"
fi

if docker-compose ps | grep -q "redis.*Up"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "  Services Started Successfully!"
echo "==========================================${NC}"
echo ""
echo "Access the services:"
echo "  - Neo4j Browser: http://localhost:7474"
echo "    Username: neo4j"
echo "    Password: your-neo4j-password (from backend/.env)"
echo ""
echo "Next steps:"
echo ""
echo "1. Install backend dependencies:"
echo "   ${YELLOW}cd backend${NC}"
echo "   ${YELLOW}python -m venv venv${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}  # On Windows: venv\\Scripts\\activate"
echo "   ${YELLOW}pip install -r requirements.txt${NC}"
echo ""
echo "2. Start the backend server:"
echo "   ${YELLOW}uvicorn app.main:app --reload${NC}"
echo "   API will be at: http://localhost:8000"
echo "   Docs will be at: http://localhost:8000/docs"
echo ""
echo "3. In a new terminal, install frontend dependencies:"
echo "   ${YELLOW}cd frontend${NC}"
echo "   ${YELLOW}npm install${NC}"
echo ""
echo "4. Start the frontend:"
echo "   ${YELLOW}npm run dev${NC}"
echo "   App will be at: http://localhost:3000"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT: Make sure you've added your API keys to backend/.env:${NC}"
echo "   - OPENAI_API_KEY"
echo "   - ASSEMBLYAI_API_KEY"
echo "   - ANTHROPIC_API_KEY (optional)"
echo ""
echo "For detailed setup instructions, see IMPLEMENTATION_GUIDE.md"
echo ""
