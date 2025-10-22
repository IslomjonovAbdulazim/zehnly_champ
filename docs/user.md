# User API Endpoints

> Simple endpoints to view user tournament data (no accounts required)

## User Details

### Get User Info
```http
GET /users/{user_id}
```

**Response:**
```json
{
  "id": 123,
  "external_id": "player_abc123",
  "fullname": "John Doe",
  "photo_url": "https://example.com/photo.jpg"
}
```

## Tournament Status

### Get User Tournaments
```http
GET /users/{user_id}/tournaments
```

**Response:**
```json
[
  {
    "championship": {
      "id": 1,
      "name": "Spring Tournament 2024",
      "status": "active"
    },
    "user_status": "active",
    "opponent": {
      "id": 124,
      "fullname": "Jane Smith",
      "photo_url": "https://example.com/photo2.jpg"
    },
    "wins": 3,
    "losses": 2
  }
]
```

## Match Results

### Get User Games
```http
GET /users/{user_id}/games
```

**Query Parameters:**
- `championship_id` (optional): Filter by tournament

**Response:**
```json
[
  {
    "id": 1,
    "external_id": "game_xyz789",
    "championship_name": "Spring Tournament 2024",
    "round_number": 1,
    "opponent": {
      "id": 124,
      "fullname": "Jane Smith",
      "photo_url": "https://example.com/photo2.jpg"
    },
    "winner_id": 123,
    "is_finished": true,
    "did_user_win": true
  }
]
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid user ID"
}
```