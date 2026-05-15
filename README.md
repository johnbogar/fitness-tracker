# Fitness Tracker

A full-stack fitness tracking web application built as a graduate software engineering project. Users can log workouts, track personal records, set and manage goals, and monitor activity streaks.

## Tech Stack

**Backend:** Python, Flask, SQLAlchemy, PostgreSQL  
**Frontend:** React, React Router, Recharts, Axios  
**Testing:** pytest (backend), React Testing Library (frontend)

## Features

- User registration, login, and profile management
- Workout logging with history tracking
- Personal records tracking
- Goal setting, editing, and deletion
- Activity streak tracking
- Dashboard with data visualizations

## Project Structure

```
fitness-tracker/
├── backend/
│   ├── routes/        # API route handlers
│   ├── models/        # SQLAlchemy data models
│   ├── tests/         # pytest test suite
│   ├── app.py         # Flask application entry point
│   └── db.py          # Database configuration
└── frontend/
    ├── src/
    │   ├── components/ # Reusable UI components
    │   ├── pages/      # Page-level components
    │   ├── context/    # Auth context
    │   └── utils/      # API utility functions
    └── public/
```

## Getting Started

### Prerequisites
- Python 3.x
- Node.js
- PostgreSQL

### Backend
```bash
cd backend
pip install -r requirements.txt
python create_tables.py
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create a `.env` file in the `backend/` directory:
```
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
```
