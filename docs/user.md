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

**Parameters:**
- `user_id` (string): MongoDB ObjectId or external_id of the user

**Example:**
```http
GET /users/68e53d2db1e331166a013e92/tournaments
```

**Response when user is in active tournament:**
```json
{
  "championship": {
    "id": 1,
    "name": "Spring Tournament 2024",
    "status": "active"
  },
  "user_status": "active",
  "opponent": {
    "id": 124,
    "external_id": "player_xyz456",
    "fullname": "Jane Smith",
    "photo_url": "https://example.com/photo2.jpg"
  },
  "wins": 3,
  "losses": 2
}
```

**Response when user exists but not in any tournament:**
```json
{
  "championship": {
    "id": 1,
    "name": "Spring Tournament 2024",
    "status": "active"
  },
  "user_status": null,
  "wins": 0,
  "losses": 0
}
```

**Response when user does not exist:**
```json
null
```

**Notes:**
- Returns null if user doesn't exist in database
- If user exists, always returns the current active tournament
- `user_status` can be: "active", "eliminated", "waiting", or null if not participating
- `opponent` is only included when user is actively matched in a tournament
- `wins` and `losses` are 0 when user not in tournament

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