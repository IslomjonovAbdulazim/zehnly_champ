# Tournament Admin Panel API Guide for AI Assistants

> Comprehensive guide for AI assistants to understand and build admin interfaces for the tournament management system

## 🌐 API Base URL
**Production API:** `https://zehnlychamp-production.up.railway.app/`

All API endpoints mentioned in this guide should be prefixed with this base URL.

## 🏆 System Overview

### Tournament Concept
This is a **bracket-style tournament system** where:
- Users are paired once and play the same opponent throughout the tournament
- Each round, paired players compete in games (win/lose only)
- Admin advances rounds manually when ready
- Tournament progresses until completion

### Data Flow
```
Championship (Tournament)
├── UserChampionship (Roster of participants)
├── Pairings (Who plays who - fixed for entire tournament)
│   └── Games (Individual matches per round)
└── Current Round (Admin-controlled progression)
```

### Admin Responsibilities
1. **Setup**: Create championship, add users, generate pairings
2. **Management**: View games, advance rounds, monitor progress
3. **Oversight**: Check statistics, leaderboards, eliminate players

---

## 🔐 Authentication System

### Login Process
**Endpoint:** `POST /admin/login`

The system uses hardcoded admin credentials from environment variables:
- Email: `admin@gmail.com`
- Password: `admin123`

**Implementation Example:**
```javascript
// Frontend login function
const BASE_URL = 'https://zehnlychamp-production.up.railway.app';

async function adminLogin(email, password) {
  const response = await fetch(`${BASE_URL}/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const { access_token } = await response.json();
    localStorage.setItem('admin_token', access_token);
    return true;
  }
  return false;
}
```

### Token Usage
ALL admin endpoints require the JWT token in the Authorization header:

```javascript
// Add to every admin API call
headers: {
  'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
  'Content-Type': 'application/json'
}
```

---

## 📋 Complete Admin Workflow

### Step 1: Create Tournament
**Purpose:** Start a new championship tournament

**Endpoint:** `POST /admin/championships`

**Frontend Implementation:**
```javascript
async function createChampionship(name) {
  const response = await fetch(`${BASE_URL}/admin/championships`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name })
  });
  return response.json();
}
```

**UI Suggestions:**
- Simple form with tournament name input
- "Create Tournament" button
- Show success message with new tournament ID

### Step 2: User Management
**Purpose:** Add participants to the system

**Endpoints:**
- `POST /admin/users` - Create individual user
- `GET /admin/users` - List all users for selection

**Frontend Implementation:**
```javascript
// Create user
async function createUser(external_id, fullname, photo_url) {
  const response = await fetch(`${BASE_URL}/admin/users`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ external_id, fullname, photo_url })
  });
  return response.json();
}

// Get users for pairing
async function getUsers() {
  const response = await fetch(`${BASE_URL}/admin/users`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

**UI Suggestions:**
- User creation form (external_id, name, photo)
- User list with checkboxes for pairing selection
- Search/filter functionality for large user lists

### Step 3: Generate Pairings
**Purpose:** Create fixed matchups for the entire tournament

**Endpoint:** `POST /admin/championships/{id}/generate-pairings`

**Key Concept:** Once pairings are generated, these same opponents will play each other in EVERY round of the tournament.

**Frontend Implementation:**
```javascript
async function generatePairings(championshipId, userIds) {
  const response = await fetch(`${BASE_URL}/admin/championships/${championshipId}/generate-pairings`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_ids: userIds })
  });
  return response.json();
}
```

**UI Suggestions:**
- Multi-select user list
- "Generate Random Pairings" button
- Display generated pairings in cards/table format
- Show unpaired users (if odd number) with explanation

### Step 4: Round Management
**Purpose:** Progress tournament through rounds

**Key Endpoints:**
- `GET /admin/championships/{id}/games?round=X` - View current round games
- `POST /admin/championships/{id}/advance-round` - Move to next round

**Important:** When advancing rounds:
- All unfinished games are automatically forfeited (both players lose)
- New games are created for the next round with same pairings
- This is irreversible!

**Frontend Implementation:**
```javascript
// View games for current round
async function getRoundGames(championshipId, round) {
  const response = await fetch(`${BASE_URL}/admin/championships/${championshipId}/games?round=${round}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Advance to next round (with confirmation!)
async function advanceRound(championshipId) {
  // Show confirmation dialog first!
  if (!confirm('This will forfeit all pending games. Continue?')) return;
  
  const response = await fetch(`${BASE_URL}/admin/championships/${championshipId}/advance-round`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

**UI Suggestions:**
- Round selector/tabs to view different rounds
- Game status indicators (finished/pending)
- Big "Advance Round" button with confirmation dialog
- Show forfeit warnings clearly

---

## 📊 Tournament Monitoring

### Championship Overview
**Endpoint:** `GET /admin/championships`

**Purpose:** Dashboard view of all tournaments

**Frontend Implementation:**
```javascript
async function getChampionships() {
  const response = await fetch(`${BASE_URL}/admin/championships`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

**UI Suggestions:**
- Tournament cards showing key metrics
- Current round prominently displayed
- Progress bars (finished_games / total_games)
- Click to drill down into specific tournament

### Detailed Statistics
**Endpoint:** `GET /admin/championships/{id}/stats`

**Purpose:** Complete tournament analysis

**Returns:**
- User statistics (active/eliminated counts)
- Game progress by round
- Leaderboard sorted by wins
- Detailed breakdowns

**UI Suggestions:**
- Charts/graphs for game progress
- Leaderboard table with win/loss records
- Round-by-round game counts
- Export capabilities for reporting

---

## 🎮 External Game Integration

### Important Notes for Frontend
The system integrates with external game backends:

1. **Games are created** when rounds advance
2. **External system** handles actual gameplay
3. **Results come back** via `/games/result` endpoint
4. **Admin only views** game status, doesn't control results

**Frontend Considerations:**
- Show game external_ids for tracking
- Display game status (pending/finished)
- Don't provide game result input (that's external)
- Focus on tournament flow, not individual game management

---

## 🚨 Error Handling & Edge Cases

### Common Scenarios

**Authentication Errors (401/403):**
```javascript
// Always check for auth errors
if (response.status === 401 || response.status === 403) {
  // Redirect to login
  localStorage.removeItem('admin_token');
  window.location.href = '/admin/login';
}
```

**No Users Selected for Pairing:**
- Validate user selection before API call
- Show helpful error messages

**Odd Number of Users:**
- API returns unpaired users
- Show clear explanation to admin
- Suggest adding/removing one user

**Empty Championships:**
- Handle championships with no pairings
- Show appropriate empty states
- Guide admin through setup process

---

## 💡 Frontend Component Suggestions

### Dashboard Layout
```
┌─────────────────────────────────────┐
│ Tournament Admin Panel              │
├─────────────────────────────────────┤
│ 📊 Championship Overview           │
│ ┌─────┐ ┌─────┐ ┌─────┐           │
│ │ T1  │ │ T2  │ │ T3  │           │
│ │ R3  │ │ R1  │ │ R5  │           │
│ └─────┘ └─────┘ └─────┘           │
├─────────────────────────────────────┤
│ 🎮 Active Tournament               │
│ Round 3 │ 8/12 games finished      │
│ [Advance Round] [View Games]        │
└─────────────────────────────────────┘
```

### Tournament Detail View
```
┌─────────────────────────────────────┐
│ Spring Tournament 2024              │
├─────────────────────────────────────┤
│ Rounds: [1] [2] [3] [4*]           │
├─────────────────────────────────────┤
│ Games in Round 4:                   │
│ ┌─────────────────────────────────┐ │
│ │ John vs Jane    [Finished] ✓    │ │
│ │ Bob vs Alice    [Pending]  ⏳   │ │
│ │ Mike vs Sarah   [Finished] ✓    │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ [🚀 Advance to Round 5]           │
└─────────────────────────────────────┘
```

### User Management
```
┌─────────────────────────────────────┐
│ User Management                     │
├─────────────────────────────────────┤
│ [➕ Add New User]                  │
├─────────────────────────────────────┤
│ Select users for pairing:           │
│ ☑ John Doe      ☑ Jane Smith       │
│ ☑ Bob Wilson    ☐ Alice Johnson    │
│ ☑ Mike Chen     ☑ Sarah Davis      │
├─────────────────────────────────────┤
│ [🎲 Generate Random Pairings]      │
└─────────────────────────────────────┘
```

---

## 🔧 API Integration Patterns

### Polling for Updates
Since games are updated externally, implement polling:

```javascript
// Poll for game updates every 30 seconds
setInterval(async () => {
  const games = await getRoundGames(championshipId, currentRound);
  updateGameDisplay(games);
}, 30000);
```

### Optimistic Updates
For admin actions, update UI immediately:

```javascript
// Update UI first, then sync with server
function advanceRoundOptimistic() {
  setCurrentRound(currentRound + 1);
  setGamesLoading(true);
  
  advanceRound(championshipId)
    .then(result => {
      // Confirm success
      setGamesLoading(false);
      showSuccessMessage(result.message);
    })
    .catch(error => {
      // Rollback on error
      setCurrentRound(currentRound);
      showErrorMessage('Failed to advance round');
    });
}
```

### Data Refresh Strategy
```javascript
// Refresh tournament data after key actions
async function refreshTournamentData() {
  const [championships, games, stats] = await Promise.all([
    getChampionships(),
    getRoundGames(championshipId, currentRound),
    getChampionshipStats(championshipId)
  ]);
  
  updateDashboard({ championships, games, stats });
}
```

---

## 🎯 Key Success Metrics

### For Admin Panel Effectiveness
1. **Tournament Setup Time** - How quickly admin can create and start tournaments
2. **Round Management** - Clear visibility into round status and easy advancement
3. **User Experience** - Intuitive navigation and clear status indicators
4. **Error Prevention** - Confirmations for destructive actions, clear validation

### Technical Performance
1. **API Response Times** - Keep under 500ms for good UX
2. **Real-time Updates** - Tournament state should feel live
3. **Error Recovery** - Graceful handling of network issues
4. **Data Consistency** - Always show accurate tournament state

This comprehensive guide should give AI assistants everything they need to build an effective admin panel for the tournament system! 🚀