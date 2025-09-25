#!/usr/bin/bash
set -euo pipefail

# Add Foundry to PATH if not already present
export PATH="$HOME/.foundry/bin:$PATH"

# start_anvil.sh
# Simple HTTP-only Anvil startup script

HTTP_PORT=${1:-8545}

echo "Starting Anvil HTTP RPC on http://127.0.0.1:${HTTP_PORT}"
echo "Press Ctrl+C to stop."

# Start anvil with simple HTTP support
exec anvil --host 127.0.0.1 --port "${HTTP_PORT}"
