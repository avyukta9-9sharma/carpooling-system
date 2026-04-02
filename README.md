# Node-Based Carpooling System

A Django-based carpooling system where drivers publish trips along a road network (graph) and passengers can request to join nearby drivers in real time.

## Tech Stack

- Python / Django 6.0
- Django REST Framework
- PostgreSQL (production database)
- HTML/CSS (Server-Side Rendered pages)
- Django AllAuth (Google OAuth)

---

## Live Demo
https://dvmcarpooling.me/dashboard/login/

## Features Implemented

### Phase 1 — Core System ✅

#### Authentication
- Custom User model with Driver and Passenger roles
- Register, Login, Logout via both API and browser UI
- Admin panel for managing the road network

#### Graph / Road Network
- Directed graph using Django ORM (Node and Edge models)
- Admins can add/remove nodes and edges via admin panel
- BFS algorithm for shortest path finding between nodes

#### Trip Management
- Drivers can create trips by selecting start and end nodes
- BFS automatically calculates the shortest route
- Drivers can view all their trips, cancel scheduled trips
- Drivers can update their current node as they progress

#### Carpool Request System
- Passengers can submit carpool requests with pickup and dropoff nodes
- Drivers see only requests within 2 nodes of their remaining route
- Detour and fare calculated automatically for each matching request
- Drivers can make offers, passengers can confirm offers

#### Fare Calculation
- Fare formula: `base_fee + unit_price * sum(1/n_i)` per hop
- Detour calculated as extra nodes added to driver's remaining route

#### SSR Pages
- Driver dashboard: create trips, view trips, view incoming requests, make offers
- Passenger dashboard: submit requests, view offers, confirm offers
- Login and Register pages

---

### Phase 2 — Extended Features ✅

#### Google OAuth
- Sign in with Google via Django AllAuth
- Integrated into the login page alongside standard username/password login

#### Wallet System
- Each user has a wallet with a balance
- Passengers can top up their wallet
- Full transaction history (top-ups, fare deductions, driver earnings)

#### Mid-Ride Carpool Support
- Passengers can discover and join trips that are already in progress (active status)
- `/api/trips/available/` endpoint returns both scheduled and active trips matching a passenger's pickup/dropoff nodes

#### PostgreSQL Database
- Migrated from SQLite to PostgreSQL for production-grade data persistence

---

### Optional Features ✅

#### Trip Rating System
- Passengers and drivers can rate each other after a trip (1–5 stars)
- Ratings include an optional comment
- Per-user average rating and full rating history available via API
- Prevents duplicate ratings for the same trip

#### Interactive Network Map
- Visual browser page showing the full road network
- Nodes rendered as circles, edges as directional arrows
- Auto-fetches live node/edge data from the API and draws on HTML canvas
- Accessible from both driver and passenger dashboards via the nav bar

---

## How to Run

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies:
   ```
   pip install django djangorestframework psycopg2-binary django-allauth requests PyJWT cryptography
   ```
5. Set up PostgreSQL and update `DATABASES` in `settings.py` with your credentials
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`
9. Visit: `http://127.0.0.1:8000/dashboard/login/`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register user |
| POST | `/api/auth/login/` | Login |
| POST | `/api/auth/logout/` | Logout |
| GET/POST | `/api/nodes/` | List/create nodes (admin) |
| DELETE | `/api/nodes/{id}/` | Delete node (admin) |
| GET/POST | `/api/edges/` | List/create edges (admin) |
| DELETE | `/api/edges/{id}/` | Delete edge (admin) |
| GET/POST | `/api/trips/` | List/create trips (driver) |
| GET | `/api/trips/available/` | List available trips for a passenger |
| POST | `/api/trips/{id}/cancel/` | Cancel trip |
| POST | `/api/trips/{id}/update-node/` | Update driver's current position |
| GET | `/api/trips/{id}/requests/` | View incoming carpool requests |
| POST | `/api/trips/{id}/offer/{req_id}/` | Make offer to passenger |
| POST | `/api/trips/{id}/rate/` | Submit a rating for a user on this trip |
| GET/POST | `/api/requests/` | List/create carpool requests (passenger) |
| POST | `/api/requests/{id}/cancel/` | Cancel carpool request |
| POST | `/api/offers/{id}/confirm/` | Passenger confirms offer |
| GET | `/api/wallet/` | Get wallet balance |
| POST | `/api/wallet/topup/` | Top up wallet |
| GET | `/api/wallet/transactions/` | Transaction history |
| GET | `/api/users/{id}/ratings/` | Get ratings for a user |

---

## SSR Dashboard Pages

| URL | Description |
|-----|-------------|
| `/dashboard/login/` | Login page (also has Google OAuth button) |
| `/dashboard/register/` | Register page |
| `/dashboard/driver/` | Driver dashboard |
| `/dashboard/passenger/` | Passenger dashboard |
| `/dashboard/map/` | Interactive road network map |

---

## Admin Panel

Visit `/admin` and login with superuser credentials to manage nodes, edges, trips, users, wallets, transactions, ratings, and more.

---

### Phase 3 ✅ 
- Docker + Nginx + Gunicorn + DigitalOcean VPS + domain + SSL
