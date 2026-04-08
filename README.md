# Node-Based Carpooling System

A full-stack Django backend carpooling system built for the **DVM (Department of Visual Media) Backend Recruitment Task, BITS Pilani**.

Drivers publish trips along a directed road network (graph), and passengers request to join. The system handles graph-based route matching, proximity-aware carpool offers, fare calculation, wallet management, and live deployment.

**Live Demo:** [https://dvmcarpooling.me/dashboard/login/](https://dvmcarpooling.me/dashboard/login/)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Python 3.12 / Django 6.0 |
| REST API | Django REST Framework 3.16 |
| Authentication | Django sessions + Django AllAuth (Google OAuth2) |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |
| Web Server | Nginx (reverse proxy) |
| Application Server | Gunicorn |
| Hosting | DigitalOcean VPS (Bangalore) |
| Domain | dvmcarpooling.me (Namecheap) |
| SSL | Let's Encrypt (auto-renewing) |
| Frontend | Server-Side Rendered HTML/CSS (Django Templates) |

---

## Features Implemented

### Phase 1 — Core System

**Authentication & User Roles**
- Custom User model extending Django's AbstractUser with Driver and Passenger roles
- Register, Login, Logout via both REST API and browser UI
- Role-based access control across all views and API endpoints
- Admin panel for full management of users, graph, trips, and requests

**Graph / Road Network**
- Directed graph implemented using Django ORM (Node and Edge models)
- Admins can add and remove nodes and edges via the admin panel or API
- BFS (Breadth-First Search) algorithm for shortest path computation between any two nodes
- Interactive visual graph rendered in-browser using HTML Canvas + JavaScript

**Trip Management**
- Drivers create trips by selecting start and end nodes
- BFS automatically computes and stores the shortest route on trip creation
- Drivers can view all their trips, cancel scheduled trips
- Drivers update their current node as they progress along the route

**Carpool Request System**
- Passengers submit carpool requests with pickup and dropoff nodes
- Drivers see only requests within 2 nodes of their remaining route (proximity matching)
- Detour (extra hops) and fare calculated automatically for each matching request
- Drivers make offers to passengers with computed fare and detour
- Passengers view offers and confirm or ignore them

**Fare Calculation**
- Formula: `fare = base_fee + unit_price * sum(1/n_i per hop)`
- Detour = extra nodes added to the driver's remaining route to accommodate the passenger

**SSR Dashboard Pages**
- Driver dashboard: create trips, view all trips, view incoming carpool requests, make offers, cancel trips
- Passenger dashboard: submit carpool requests, view pending/confirmed offers, confirm offers, cancel requests
- Login and Register pages
- Interactive road network map (accessible to all logged-in users)

---

### Phase 2 — Extended Features

**Wallet System**
- Each user has a wallet with a balance
- Passengers can top up their wallet balance via API
- Full transaction history (top-ups, fare deductions, driver earnings)

**Mid-Ride Carpool Support**
- Passengers can search for available trips including trips already in progress (`active` status)
- `/api/trips/available/` endpoint returns all scheduled and active trips near a passenger's requested pickup/dropoff

**PostgreSQL Database**
- Migrated from SQLite to PostgreSQL for production
- Managed via Docker Compose as a separate service

**Google OAuth Login**
- Sign in with Google via Django AllAuth
- New Google users are prompted to choose their role (Driver or Passenger) before being redirected to their dashboard
- Existing username/password login continues to work alongside OAuth

---

### Optional Features

**Trip Rating System**
- After a trip, users can rate each other with a score (1–5) and an optional comment
- `GET /api/users/{id}/ratings/` returns average score and full rating history for any user

**Interactive Network Map**
- Visual graph rendered in the browser showing all nodes as circles and edges as directional arrows
- Fetches live data from the API — updates automatically when the admin adds new nodes/edges
- Accessible from both driver and passenger dashboards via nav bar

---

### Phase 3 — Deployment

- Dockerized Django app with Gunicorn as the WSGI server
- Nginx as a reverse proxy handling HTTP → HTTPS redirect and static file serving
- PostgreSQL running as a separate Docker container with a persistent volume
- Deployed on a DigitalOcean Ubuntu 24.04 VPS (Bangalore region)
- Custom domain `dvmcarpooling.me` registered via Namecheap (GitHub Student Pack)
- HTTPS secured with a Let's Encrypt SSL certificate (auto-renews via Certbot)

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/avyukta9-9sharma/carpooling-system.git
cd carpooling-system

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure database in carpooling_project/settings.py
# Change DATABASES to use SQLite for local dev:
# 'ENGINE': 'django.db.backends.sqlite3'
# 'NAME': BASE_DIR / 'db.sqlite3'

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (admin)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver

# 8. Visit
http://127.0.0.1:8000/dashboard/login/
```

---

## How to Run with Docker (Production Setup)

```bash
# 1. Clone and enter directory
git clone https://github.com/avyukta9-9sharma/carpooling-system.git
cd carpooling-system

# 2. Build and start all containers
docker-compose up -d --build

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Visit
http://localhost/dashboard/login/
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user (driver or passenger) |
| POST | `/api/auth/login/` | Login with username and password |
| POST | `/api/auth/logout/` | Logout current user |

### Graph — Nodes & Edges (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/nodes/` | List all nodes / Create a node |
| DELETE | `/api/nodes/{id}/` | Delete a node |
| GET / POST | `/api/edges/` | List all edges / Create an edge |
| DELETE | `/api/edges/{id}/` | Delete an edge |

### Trips (Driver)
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/trips/` | List driver's trips / Create a trip |
| POST | `/api/trips/{id}/cancel/` | Cancel a scheduled trip |
| POST | `/api/trips/{id}/update-node/` | Update driver's current position |
| GET | `/api/trips/{id}/requests/` | View incoming carpool requests near route |
| POST | `/api/trips/{trip_id}/offer/{req_id}/` | Make a carpool offer to a passenger |
| GET | `/api/trips/available/` | List all active/scheduled trips (passenger use) |

### Carpool Requests (Passenger)
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/requests/` | List passenger's requests / Submit a request |
| POST | `/api/requests/{id}/cancel/` | Cancel a pending request |
| POST | `/api/offers/{id}/confirm/` | Confirm a driver's offer |

### Wallet
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/wallet/` | Get current wallet balance |
| POST | `/api/wallet/topup/` | Top up wallet balance |
| GET | `/api/wallet/transactions/` | View full transaction history |

### Ratings
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/trips/{trip_id}/rate/` | Submit a rating for a user on a trip |
| GET | `/api/users/{user_id}/ratings/` | View ratings received by a user |

---

## SSR Dashboard Pages

| URL | Description |
|---|---|
| `/dashboard/login/` | Login page (username/password or Google OAuth) |
| `/dashboard/register/` | Register a new account |
| `/dashboard/set-role/` | Role selection page for new Google OAuth users |
| `/dashboard/driver/` | Driver dashboard (trips, create trip, incoming requests) |
| `/dashboard/passenger/` | Passenger dashboard (submit requests, view/confirm offers) |
| `/dashboard/map/` | Interactive visual road network map |
| `/dashboard/logout/` | Logout and redirect to login |

---

## Admin Panel

Visit `/admin/` and log in with superuser credentials to:
- Manage the road network (add/remove nodes and edges)
- View and manage all users, trips, carpool requests, offers
- View wallets and transaction history
- View ratings
- Configure Google OAuth (Social Applications)

---

## Project Structure

```
carpooling/
├── carpooling_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── models.py          # User, Node, Edge, Trip, CarpoolRequest, CarpoolOffer, Wallet, Transaction, Rating
│   ├── views.py           # All API + SSR views
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # API URL patterns
│   ├── dashboard_urls.py  # SSR dashboard URL patterns
│   ├── utils.py           # BFS, proximity matching, fare calculation
│   ├── admin.py           # Admin registrations
│   └── templates/core/
│       ├── login.html
│       ├── register.html
│       ├── set_role.html
│       ├── driver_dashboard.html
│       ├── passenger_dashboard.html
│       ├── trip_requests.html
│       └── network_map.html
├── nginx/
│   └── nginx.conf         # Nginx reverse proxy config with SSL
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Deployment Architecture

```
Internet
    │
    ▼
Nginx (port 80/443)
    │  ← HTTP redirects to HTTPS
    │  ← Serves /static/ files directly
    │
    ▼
Gunicorn (port 8000)
    │
    ▼
Django Application
    │
    ▼
PostgreSQL (Docker container)
```

---

## What's Not Implemented

- Phase 3 advanced options: load balancing, CI/CD pipeline
- Real payment gateway integration (wallet is simulated)
- Real-time notifications (WebSockets)
- Mobile application
