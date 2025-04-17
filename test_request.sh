#!/bin/bash
curl localhost:7788/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DUMMY_API_KEY" \
  -d '{
    "model": "gpt-4o,claude-3-7-sonnet-latest",
    "messages": [
      {
        "role": "assistant",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
