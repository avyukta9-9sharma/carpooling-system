# Carpooling System
# Node-Based Carpooling System

A Django-based carpooling system where drivers publish trips along a road network (graph) and passengers can request to join.

## Tech Stack
- Python / Django 6.0
- Django REST Framework
- SQLite (development)
- HTML/CSS (Server-Side Rendered pages)

## Features Implemented (Phase 1)

### Authentication
- Custom User model with Driver and Passenger roles
- Register, Login, Logout via both API and browser UI
- Admin panel for managing the road network

### Graph / Road Network
- Directed graph using Django ORM (Node and Edge models)
- Admins can add/remove nodes and edges via admin panel
- BFS algorithm for shortest path finding between nodes

### Trip Management
- Drivers can create trips by selecting start and end nodes
- BFS automatically calculates the shortest route
- Drivers can view all their trips, cancel scheduled trips
- Drivers can update their current node as they progress

### Carpool Request System
- Passengers can submit carpool requests with pickup and dropoff nodes
- Drivers see only requests within 2 nodes of their remaining route
- Detour and fare calculated automatically for each matching request
- Drivers can make offers, passengers can confirm offers

### Fare Calculation
- Fare formula: base_fee + unit_price * sum(1/n_i) per hop
- Detour calculated as extra nodes added to driver's remaining route

### SSR Pages
- Driver dashboard: create trips, view trips, view incoming requests, make offers
- Passenger dashboard: submit requests, view offers, confirm offers
- Login and Register pages

## How to Run

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install django djangorestframework`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run server: `python manage.py runserver`
8. Visit: `http://127.0.0.1:8000/dashboard/login/`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/ | Register user |
| POST | /api/auth/login/ | Login |
| GET/POST | /api/nodes/ | List/create nodes |
| GET/POST | /api/edges/ | List/create edges |
| GET/POST | /api/trips/ | List/create trips |
| POST | /api/trips/{id}/cancel/ | Cancel trip |
| POST | /api/trips/{id}/update-node/ | Update driver position |
| GET | /api/trips/{id}/requests/ | View incoming carpool requests |
| POST | /api/trips/{id}/offer/{req_id}/ | Make offer to passenger |
| GET/POST | /api/requests/ | List/create carpool requests |
| POST | /api/requests/{id}/cancel/ | Cancel request |
| POST | /api/offers/{id}/confirm/ | Passenger confirms offer |

## Admin Panel
Visit `/admin` and login with superuser credentials to manage nodes, edges, trips, users.
