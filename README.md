# Edulance

Edulance is a Django-based collaborative platform that connects learners, mentors, and peers to work together on educational or skill-based projects.  
It allows users to collaborate with each other — all within an easy-to-use interface.

---

## Features

- **Skill-based Collaboration** – Users can select and discover collaborators based on shared skills.
- **User Authentication** – Secure JWT-based authentication.
- **Project & Team Management** – Create, join, and manage collaboration projects.
- **Interactive Frontend** – Django templates with Bootstrap and JavaScript for a dynamic user experience.
- **API Endpoints** – Django REST Framework (DRF)-powered backend.
- **Testing Support** – Fully integrated backend testing using pytest.

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Django, Django REST Framework |
| **Frontend** | Django Templates, Bootstrap, JavaScript |
| **Database** | PostgreSQL (can be swapped with SQLite for local dev) |
| **Authentication** | JWT via djangorestframework-simplejwt |
| **Testing** | pytest|

---


## Project Setup (Using `uv`)

This section explains how to set up and run the Edulance project from scratch using the **`uv`** package manager.

### 1. Clone the Repository
git clone https://github.com/Prafful-Mali/edulance.git

### 2. Install `uv`

If you don’t already have **uv**, install it using:
`pip install uv`

### 3. Create virtual environment
`uv .venv`

### 4. Activate the virtal environment
`source .venv/bin/activate`
(on Windows: .venv\Scripts\activate)

### 5. Install all dependencies
`uv sync`

### 6. Run Project
`python manage.py runserver`