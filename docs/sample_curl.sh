#!/usr/bin/env bash

API="http://localhost:8000/api/v1"

curl -X POST "$API/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","phone_number":"15550111111","password":"Password123!","role":"user"}'

TOKENS=$(curl -s -X POST "$API/auth/login/" -H "Content-Type: application/json" -d '{"username":"demo","password":"Password123!"}')
ACCESS=$(echo "$TOKENS" | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

curl -X POST "$API/queues/entries/join/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"service":1}'

curl -X POST "$API/queues/entries/join_qr/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"organization_slug":"city-hospital","service_code":"consult","phone_number":"15550111111"}'

curl -X GET "$API/analytics/export_csv/" -H "Authorization: Bearer $ACCESS"
