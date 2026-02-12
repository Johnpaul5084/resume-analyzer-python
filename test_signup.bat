@echo off
curl -X POST "http://127.0.0.1:8000/api/v1/signup" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"newuser@test.com\",\"password\":\"pass123\",\"full_name\":\"New User\"}" ^
  -v
