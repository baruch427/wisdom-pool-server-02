# Step 1: Create a new pool
Write-Host "Creating a new pool..."
$poolResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pools" -Method Post -ContentType "application/json" -Body '{"pool_content": {"title": "Final Test Pool", "description": "A pool for testing multiple drops"}, "creator_id": "final_test_user"}'
$poolId = $poolResponse.pool_id
Write-Host "Pool created with ID: $poolId"

# Step 2: Create a new stream in that pool
Write-Host "Creating a new stream..."
$streamBodyObject = @{
    stream_content = @{
        title = "Final Test Stream"
        description = "A stream for finally testing drops."
    }
    pool_id = $poolId
    creator_id = "final_test_user"
}
$streamBodyJson = $streamBodyObject | ConvertTo-Json

$streamResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/streams" -Method Post -ContentType "application/json" -Body $streamBodyJson
$streamId = $streamResponse.stream_id
Write-Host "Stream created with ID: $streamId"

# Step 3: Post multiple drops to the stream
Write-Host "Posting multiple drops to the stream..."
$dropsBody = @'
{
    "drops": [
        {
            "title": "First Drop (Final)",
            "text": "This is the first drop."
        },
        {
            "title": "Second Drop (Final)",
            "text": "This is the second drop."
        }
    ],
    "creator_id": "final_test_user"
}
'@
$addDropsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/streams/$streamId/drops" -Method Post -ContentType "application/json" -Body $dropsBody

Write-Host "--- Success! ---" -ForegroundColor Green
Write-Host "Response from adding drops:"
$addDropsResponse | ConvertTo-Json -Depth 5
