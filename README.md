# Sticky Note Scheduler

A web application for creating events using a sticky note interface. Built with React and FastAPI.

My first mini-project built with the Cursor IDE - and woah is it something. I'm really not sure what I think of it yet, but lets talk about it!

## Assumptions

- Events are all created in the same timezone.
- Events do not extend past midnight. Sleep is important! ;)
- Recurring events continue indefinitely.
- The first event (anchor event) for a recurring event might not fall on the same day as future events derived from it's recurrence rule (e.g. An event on Tuesday, might then only reoccur on Saturdays)

## Bugs

- tl;dr timezones
- Conflict detection is done in UTC, and if, for example, the comparison is to see if a recurring event series that starts in January conflicts with a one-time event in June, then the UTC time comparison will be off due to daylights savings. I store timezone, so the fix is here to be made when/if I have the time.
- There's another similar bug, where if the UTC time crosses into the next day, then it also disrupts the time conflict comparison (because the conflict detection involves casting into minutes and doing relevant < and > checks, which reset to 0 once UTC reaches the next day).

## Tech Stack

### Frontend

- React with Next.js
- TailwindCSS for styling
- Shadcn/UI component library
- TypeScript

### Backend

- Python with FastAPI
- SQLAlchemy for ORM
- Pydantic for data validation
- SQLite database
- Docker containerization

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository:

```bash
git clone <repository-url>
cd sticky-note-scheduler
```

2. Start the application using Docker Compose:

```bash
docker compose up --build
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

#### Frontend (without Docker)

```bash
cd frontend
npm install
npm run dev
```

#### Backend (without Docker)

1. Install Poetry (Python package manager):

```bash
pip install poetry
```

2. Install dependencies and set up the environment:

```bash
cd backend
poetry install
```

3. Run database migrations:

```bash
poetry run alembic upgrade head
```

4. Start the development server:

```bash
poetry run start
```

The backend API will be available at http://localhost:8000
