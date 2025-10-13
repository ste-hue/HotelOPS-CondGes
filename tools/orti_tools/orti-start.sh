#!/bin/bash

# 🎯 ORTI Finance - Unified Launcher (MCP Supabase Direct)
# Single script to rule them all - no backend, no complexity

set -e

echo "🚀 ORTI Finance - Starting MCP Direct Architecture..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Kill any existing processes
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
pkill -f "vite\|node.*5173" 2>/dev/null || true
sleep 1

# Check MCP configuration
if [ ! -f ~/.cursor/mcp.json ]; then
    echo -e "${RED}❌ MCP not configured. Expected ~/.cursor/mcp.json${NC}"
    echo -e "${YELLOW}💡 Configure MCP Supabase first!${NC}"
    exit 1
fi

# Verify Supabase MCP is configured
if ! grep -q "supabase" ~/.cursor/mcp.json; then
    echo -e "${RED}❌ Supabase MCP not found in config${NC}"
    exit 1
fi

echo -e "${GREEN}✅ MCP Supabase configured${NC}"

# Start Frontend (Vite on 5173)
echo -e "${BLUE}🎨 Starting Frontend (Port 5173)...${NC}"
cd orti-finance-compass

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

# Start Vite dev server
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

# Check frontend health
if curl -s "http://localhost:5173" | grep -q "DOCTYPE"; then
    echo -e "${GREEN}✅ Frontend active on http://localhost:5173${NC}"
else
    echo -e "${YELLOW}⏳ Frontend starting...${NC}"
    sleep 2
fi

echo ""
echo -e "${GREEN}🎉 ORTI FINANCE READY!${NC}"
echo ""
echo -e "${BLUE}📍 ACCESS:${NC}"
echo -e "   🎨 Dashboard: ${GREEN}http://localhost:5173${NC}"
echo ""
echo -e "${BLUE}🔧 ARCHITECTURE:${NC}"
echo -e "   Frontend → MCP Supabase → Database"
echo -e "   No backend, no complexity, just works!"
echo ""
echo -e "${YELLOW}⚙️ PROCESS:${NC}"
echo -e "   Frontend PID: ${FRONTEND_PID}"
echo ""
echo -e "${RED}🛑 To stop: pkill -f vite${NC}"
echo -e "${BLUE}📋 Logs follow (Ctrl+C to exit):${NC}"
echo ""

# Keep script running and show logs
wait $FRONTEND_PID