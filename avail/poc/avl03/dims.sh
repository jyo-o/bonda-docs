#!/bin/bash
# dims.sh <blockhash> -> prints rows cols and computed bytes
h="$1"
curl -s -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"chain_getHeader\",\"params\":[\"$h\"]}" \
  -H "Content-Type: application/json" http://localhost:9944 \
  | jq "{block: .result.number, rows: .result.extension.V3.commitment.rows, cols: .result.extension.V3.commitment.cols, appBytes: .result.extension.V3.appLookup.size, gridBytes: (.result.extension.V3.commitment.rows * .result.extension.V3.commitment.cols * 32)}"
