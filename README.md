# OnboardIQ

<<<<<<< HEAD

AI-powered adaptive onboarding engine that generates personalized learning paths based on skill gaps.

## Problem Statement

Traditional onboarding processes are often static, generic, and inefficient. Every learner receives nearly the same path, regardless of existing skills, role requirements, or learning priorities.

OnboardIQ solves this by building adaptive, data-driven pathways. It compares resume skills with job description requirements, identifies gaps, and creates a structured roadmap that is tailored to each learner.

## Features

- Resume and Job Description upload
- Skill extraction from uploaded documents
- Skill gap analysis between candidate and role
- Adaptive learning roadmap generation
- Reasoning trace for each recommended skill
- Dockerized setup for quick deployment

## Architecture Overview

End-to-end flow:

Upload -> Parsing -> Skill Extraction -> Gap Analysis -> Path Generation -> UI

The core recommendation layer uses a graph-based adaptive engine to resolve dependencies and produce an ordered learning path.

## Tech Stack

- Frontend: React + Tailwind CSS
- Backend: FastAPI (Python)
- Data: JSON datasets (skills, skill graph, resources, synonyms)
- Deployment: Docker

## Setup Instructions (Local)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload (Alternate for Error: python -m uvicorn app.main:app --reload)
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Docker Setup

```bash
docker-compose build
docker-compose up
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## How It Works (Core Logic)

1. Skill extraction uses a predefined skills dataset and synonym normalization.
2. Skill gap is computed as:

   Gap = JD Skills - Resume Skills

3. Adaptive path generation:

- Uses a skill dependency graph
- Adds prerequisite skills recursively
- Removes skills already known by the user
- Returns a clean, ordered learning path

## Reasoning Trace

Each roadmap recommendation includes a clear reason, such as:

- Missing in resume
- Required in job description
- Needed as a prerequisite for another target skill

This keeps recommendations transparent and easy to understand.

## Datasets Used

- Skills dataset (custom JSON)
- Skill graph dataset (custom JSON)
- Synonyms mapping (custom JSON)
- Learning resources dataset (custom JSON)
- External datasets like Kaggle or O\*NET can be integrated in future versions

## Screenshots

![Upload](./screenshots/upload.png)
![Skills Output](./screenshots/skills-output.png)
![Roadmap Visualization](./screenshots/roadmap.png)

## Future Improvements

- LLM-based skill extraction for deeper semantic matching
- User authentication and profile-based onboarding
- Progress tracking and milestone completion
- Real course provider integration (Coursera, Udemy, etc.)

## Conclusion

# OnboardIQ demonstrates how adaptive learning can make onboarding faster, more relevant, and more effective. By identifying real skill gaps and generating targeted pathways, it improves onboarding efficiency for both learners and teams.

Roadmap Generator the role using Resume

> > > > > > > c29e2c63dd7705bff5cc209f9aa8f479f5dbdec6
