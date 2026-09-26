#!/bin/bash
# usage: send.sh <id> <token> <basename.mp3>
cd "${UPLOAD_DIR:-$HOME/pod/up32}"
for i in $(seq 1 15); do
  out=$(curl -sS -X POST "https://api.notion.com/v1/mcp/file_uploads/$1/send" -H "authorization: Bearer $2" -F "file=@$3;type=audio/mpeg" -w "\nHTTP %{http_code}")
  sleep 3
done; echo "FAIL $3: $(echo "$out" | head -c 200)"; exit 1
