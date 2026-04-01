# NEXUS CENTRAL

Nexus Central is an enterprise-grade resource management and booking ecosystem. It provides a centralized platform for reserving high-value equipment and studio spaces, ensuring operational efficiency through automated conflict resolution, weather-dependent logic, and secure administrative control.

The system is architected as a decoupled three-tier application, consisting of a high-performance REST API, a cloud-synchronized database, and two dedicated client interfaces for users and administrators.

---

## Technical Architecture

### Backend Infrastructure
* Framework: FastAPI (Asynchronous Python)
* Database: PostgreSQL (Relational)
* ORM: SQLAlchemy (Object-Relational Mapping)
* Validation: Pydantic (Strict Data Modeling)
* Deployment: Railway Cloud Infrastructure

### Frontend Interfaces
* User Client: Telegram Bot API (Session-persistent messaging interface)
* Admin Client: CustomTkinter (Multi-threaded desktop management dashboard)

---

## Core System Features

### Layered Security Protocol
All communications between the clients and the backend are protected by a header-based authentication system. The API enforces X-API-KEY validation for every request, preventing unauthorized data access or resource manipulation.

### Intelligent Reservation Engine
* Conflict Detection: The system performs real-time checks to ensure no overlapping bookings exist for a specific resource, maintaining a clean schedule.
* Environmental Integration: A dedicated weather service router monitors conditions in Barcelona. It provides automated warnings for outdoor gear bookings if rain or hazardous conditions are detected.
* Database Integrity: Schema-level cascading deletes ensure that when a user or category is removed, all associated booking and resource records are purged to prevent orphaned data.

### Persistent Bot Sessions
The Telegram interface implements a file-based persistence layer using JSON. This allows the bot to retain user authentication states across process restarts, eliminating the need for repeated logins and enhancing the overall user experience.

### Optimized Administrative Workflow
The Admin Dashboard is built with a non-blocking multi-threaded architecture. Network operations are offloaded to background threads, ensuring the GUI remains responsive during API calls. The interface provides real-time feedback through a synchronized status and notification system.

---

## Repository Structure

| Component | Responsibility |
| :--- | :--- |
| main.py | FastAPI entry point and security configuration |
| app/api/routers/ | Modular endpoint logic (Users, Resources, Bookings) |
| app/api/schemas.py | Pydantic models for data serialization and validation |
| app/repositories/ | Database engine and SQLAlchemy model definitions |
| admin_dashboard.py | Desktop application for inventory and user management |
| bot_handler.py | Telegram bot interface with persistent session logic |
| Procfile | Production deployment instructions for Railway |

---

## Installation and Deployment

### Environment Configuration
The application requires a .env file in the root directory containing the following parameters:
* TELEGRAM_BOT_TOKEN: Unique identifier from BotFather.
* DATABASE_URL: PostgreSQL connection string (formatted for psycopg).
* ADMIN_API_KEY: Secret key for header-based authentication.

### Local Setup
1. Install dependencies:
   pip install -r requirements.txt

2. Initialize the server:
   uvicorn main:app --reload

3. Launch Administrative Dashboard:
   python admin_dashboard.py

4. Launch User Interface:
   python bot_handler.py

### Production Deployment
This project is optimized for deployment on the Railway platform. The environment uses the internal database network for API-to-DB communication, while local administration utilizes the external connection string for maintenance and seeding operations.
