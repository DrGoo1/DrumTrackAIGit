#!/bin/bash
# ChatGPT-5 v4/v5 WebDAW QA Test Script
# Tests all plug-and-test endpoints for full DAW functionality

echo "=== DrumTracKAI v4/v5 WebDAW QA Test ==="
echo

# 1) Health check
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/api/health | jq
echo

# 2) v4/v5 status
echo "2. Testing v4/v5 integration status..."
curl -s http://localhost:8000/api/v4v5/status | jq
echo

# 3) Seed default kit
echo "3. Seeding default kit..."
curl -s -X POST http://localhost:8000/api/devseed | jq
echo

# 4) List default kit samples
echo "4. Testing samples browser..."
curl -s http://localhost:8000/api/samples/kits/default | jq
echo

# 5) List sample directories
echo "5. Testing sample directories..."
curl -s http://localhost:8000/api/samples/dirs | jq
echo

# 6) Save arrangement + tempo
echo "6. Testing sections (arrangement + tempo)..."
curl -s -X POST http://localhost:8000/api/sections \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test1","sections":[{"id":"s1","type":"verse","start_sec":0,"end_sec":8}],"tempo_points":[{"sec":0,"bpm":120}]}' | jq
echo

# 7) Get arrangement
echo "7. Retrieving sections..."
curl -s "http://localhost:8000/api/sections?job_id=test1" | jq
echo

# 8) Groove analysis
echo "8. Testing groove analysis..."
curl -s -X POST http://localhost:8000/api/groove/analyze \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test1","section_id":"all"}' | jq
echo

# 9) Reference loops search
echo "9. Testing reference loops (Pocket Transfer)..."
curl -s "http://localhost:8000/api/reference_loops?style=funk&bpm=100" | jq
echo

# 10) Review comments
echo "10. Testing review system..."
curl -s -X POST http://localhost:8000/api/review/comments \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test1","section_id":"all","time_sec":15.5,"text":"Test comment at cursor"}' | jq
echo

curl -s "http://localhost:8000/api/review/comments?job_id=test1" | jq
echo

# 11) Quick preview render
echo "11. Testing quick preview render..."
curl -s -X POST http://localhost:8000/api/preview/render \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test1","bpm":120,"bars":4,"kit_map":{"kick":"/samples/kits/default/kick.wav"}}' | jq
echo

# 12) Kit management
echo "12. Testing kit management..."
curl -s http://localhost:8000/api/kits | jq
echo

# 13) Export jobs
echo "13. Testing export system..."
curl -s http://localhost:8000/api/exports | jq
echo

echo "=== QA Test Complete ==="
echo "All endpoints should return valid JSON responses."
echo "Check the browser at http://localhost:3000 for frontend integration."
