# Admin API Endpoints

> Simplified administrative endpoints for tournament management

## Championship Management

### Create Championship
```http
POST /admin/championships
```

**Request Body:**
```json
{
  "name": "Spring Tournament 2024"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Spring Tournament 2024",
  "status": "active"
}
```

### List All Championships
```http
GET /admin/championships
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Spring Tournament 2024",
    "status": "active",
    "current_round": 4,
    "user_count": 8,
    "pairing_count": 4,
    "total_games": 15,
    "finished_games": 12
  }
]
```

## User Management

### Create User
```http
POST /admin/users
```

**Request Body:**
```json
{
  "external_id": "player_abc123",
  "fullname": "John Doe",
  "photo_url": "https://example.com/photo.jpg"
}
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

### List All Users
```http
GET /admin/users
```

**Response:**
```json
[
  {
    "id": 123,
    "external_id": "player_abc123",
    "fullname": "John Doe",
    "photo_url": "https://example.com/photo.jpg"
  }
]
```

## Pairing Management

### Generate Pairings
```http
POST /admin/championships/{championship_id}/generate-pairings
```

**Request Body:**
```json
{
  "user_ids": [123, 124, 125, 126]
}
```

**Response:**
```json
{
  "generated_pairings": [
    {
      "id": 1,
      "championship_id": 1,
      "player1": {
        "id": 123,
        "fullname": "John Doe"
      },
      "player2": {
        "id": 124,
        "fullname": "Jane Smith"
      },
      "status": "active"
    }
  ],
  "unpaired_users": [
    {
      "id": 125,
      "fullname": "Bob Wilson",
      "reason": "Odd number of users"
    }
  ]
}
```

## Game Viewing

### Get Championship Games
```http
GET /admin/championships/{championship_id}/games
```

**Query Parameters:**
- `round` (optional): Filter by round number

**Response:**
```json
[
  {
    "id": 1,
    "external_id": "game_xyz789",
    "round_number": 1,
    "pairing": {
      "id": 1,
      "player1": {
        "id": 123,
        "fullname": "John Doe"
      },
      "player2": {
        "id": 124,
        "fullname": "Jane Smith"
      }
    },
    "winner_id": 123,
    "is_finished": true
  }
]
```

## Round Management

### Advance to Next Round
```http
POST /admin/championships/{championship_id}/advance-round
```

**Response:**
```json
{
  "championship_id": 1,
  "previous_round": 3,
  "current_round": 4,
  "forfeited_games": 2,
  "new_games_created": 4,
  "message": "Advanced to round 4. 2 pending games marked as forfeited (both players lose)."
}
```

## Statistics

### Championship Statistics
```http
GET /admin/championships/{championship_id}/stats
```

**Response:**
```json
{
  "championship": {
    "id": 1,
    "name": "Spring Tournament 2024",
    "status": "active"
  },
  "users": {
    "total": 8,
    "active": 6,
    "eliminated": 2
  },
  "pairings": {
    "total": 4,
    "active": 3,
    "eliminated": 1
  },
  "games": {
    "total": 15,
    "finished": 12,
    "pending": 3,
    "by_round": {
      "1": 4,
      "2": 4,
      "3": 4,
      "4": 3
    }
  },
  "leaderboard": [
    {
      "user": {
        "id": 123,
        "fullname": "John Doe"
      },
      "wins": 5,
      "losses": 2,
      "status": "active"
    }
  ]
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Admin authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient admin privileges"
}
```

### 404 Not Found
```json
{
  "detail": "Championship not found"
}
```