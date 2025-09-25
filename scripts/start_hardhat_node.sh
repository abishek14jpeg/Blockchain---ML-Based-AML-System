#!/usr/bin/bash
set -euo pipefail

# Start Hardhat node with WebSocket support
echo "Starting Hardhat node with WebSocket support..."

cd "$(dirname "$0")/.."

# Export Foundry path
export PATH="$HOME/.foundry/bin:$PATH"

# Start Hardhat node
npx hardhat node --hostname 127.0.0.1 --port 8545