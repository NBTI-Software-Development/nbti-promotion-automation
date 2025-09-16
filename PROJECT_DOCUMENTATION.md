


## 1. Introduction

This document provides a comprehensive overview of the NBTI Promotion Automation system, a full-stack web application designed to streamline and automate the employee promotion process at the National Board for Technology Incubation (NBTI). The system integrates a Performance Management System (PMS) and an Exam Management Module (EMM) to provide a holistic and data-driven approach to employee evaluation and promotion.

### 1.1. Purpose

The primary purpose of this project is to replace the manual, paper-based promotion process at NBTI with a modern, efficient, and transparent digital solution. The system aims to:

- **Automate Workflows:** Automate the entire promotion process, from performance evaluation to exam administration and scoring.
- **Improve Efficiency:** Reduce the time and effort required to manage promotions, freeing up HR staff to focus on more strategic initiatives.
- **Enhance Transparency:** Provide employees and supervisors with a clear and transparent view of the promotion process and criteria.
- **Ensure Fairness:** Standardize the evaluation process and reduce the potential for bias.
- **Data-Driven Decisions:** Enable data-driven decision-making by providing comprehensive analytics and reporting.

### 1.2. Scope

The scope of this MVP (Minimum Viable Product) includes the following key features:

- **User Management:** Secure user registration, authentication, and role-based access control.
- **Performance Management System (PMS):**
    - Creation and management of performance evaluations.
    - Goal setting, tracking, and rating.
    - Supervisor feedback and approval workflows.
    - Performance dashboard and analytics.
- **Exam Management Module (EMM):**
    - Question bank management.
    - Exam creation and configuration.
    - Secure exam-taking environment.
    - Automated grading for multiple-choice questions.
    - Exam results and performance analytics.
- **Integration:** Seamless integration between the PMS and EMM to link exam scores with performance evaluations.
- **Security:** Comprehensive security measures, including data encryption, secure coding practices, and infrastructure hardening.
- **Deployment:** Containerized deployment with Docker and a production-ready setup.

### 1.3. Target Audience

This document is intended for a wide range of stakeholders, including:

- **Project Managers:** To understand the project scope, timeline, and deliverables.
- **Developers:** To understand the system architecture, design, and implementation details.
- **System Administrators:** To understand the deployment and maintenance procedures.
- **NBTI Management:** To understand the business value and impact of the system.
- **End-Users:** To understand how to use the system effectively.






## 2. System Architecture

The NBTI Promotion Automation system is designed as a modern, scalable, and secure web application based on a microservices-oriented architecture. The system is composed of several loosely coupled components that communicate with each other through well-defined APIs.

### 2.1. Architectural Overview

The high-level architecture of the system consists of the following key components:

- **Frontend Application:** A single-page application (SPA) built with React that provides the user interface for the system.
- **Backend API:** A set of RESTful APIs built with Flask that provide the business logic and data access for the system.
- **Database:** A PostgreSQL database that stores all the application data.
- **Cache:** A Redis cache that is used for session management, rate limiting, and caching frequently accessed data.
- **Task Queue:** A Celery task queue (planned) for handling long-running and asynchronous tasks, such as sending email notifications and generating reports.

![System Architecture Diagram](https://i.imgur.com/example.png)  *<-- Placeholder for a real diagram to be generated later*

### 2.2. Frontend Architecture

The frontend is a modern, responsive single-page application (SPA) built with the following technologies:

- **React:** A popular JavaScript library for building user interfaces.
- **Vite:** A fast and modern build tool for web development.
- **React Router:** For client-side routing and navigation.
- **Tailwind CSS & Shadcn/UI:** For styling and UI components.
- **Axios:** For making HTTP requests to the backend API.
- **Vitest & React Testing Library:** For unit and component testing.

The frontend architecture is based on a component-based approach, with a clear separation of concerns between UI components, business logic, and data fetching.

### 2.3. Backend Architecture

The backend is a set of RESTful APIs built with the following technologies:

- **Flask:** A lightweight and flexible Python web framework.
- **SQLAlchemy:** A powerful and flexible Object-Relational Mapper (ORM) for Python.
- **Flask-RESTful:** An extension for Flask that adds support for quickly building REST APIs.
- **Flask-JWT-Extended:** For handling JSON Web Tokens (JWT) for authentication.
- **Gunicorn:** A production-ready WSGI server for deploying Flask applications.
- **Pytest:** For unit and integration testing.

The backend is designed to be modular and scalable, with a clear separation of concerns between different modules (e.g., authentication, PMS, EMM).

### 2.4. Database Architecture

The database is a PostgreSQL relational database that is designed to be scalable, reliable, and secure. The database schema is designed to be normalized and efficient, with clear relationships between different tables.

The database schema includes tables for:

- Users and Roles
- Performance Evaluations and Goals
- Exams and Questions
- Exam Submissions and Answers

### 2.5. Infrastructure and Deployment

The application is designed to be deployed in a containerized environment using Docker. The deployment architecture includes:

- **Docker:** For containerizing the frontend and backend applications.
- **Docker Compose:** For orchestrating the deployment of multiple containers.
- **Nginx:** As a reverse proxy and load balancer for the frontend and backend applications.
- **CI/CD Pipeline (planned):** For automating the build, testing, and deployment process.

This is a placeholder for a real diagram to be generated later








## 3. User Guide

This section provides a comprehensive guide for end-users on how to use the NBTI Promotion Automation system. It covers all the key features and workflows of the system, from logging in to completing performance evaluations and taking exams.

### 3.1. Getting Started

#### **Accessing the System**

To access the system, open your web browser and navigate to the following URL:

[https://nbti.your-domain.com](https://nbti.your-domain.com)

#### **Logging In**

To log in to the system, you will need a username and password provided by your system administrator. Enter your credentials in the login form and click the "Sign In" button.

If you have forgotten your password, you can use the "Forgot Password" link to reset it.

### 3.2. Dashboard

After logging in, you will be taken to your personalized dashboard, which provides an overview of your performance evaluations, exams, and other relevant information. The dashboard includes:

- **Statistics:** Key metrics such as the number of active evaluations, completed exams, and pending tasks.
- **Quick Actions:** Links to common tasks, such as starting a new evaluation or browsing available exams.
- **Recent Activity:** A feed of recent activities, such as new comments on your goals or upcoming exam deadlines.

### 3.3. Performance Management System (PMS)

The PMS module allows you to manage your performance evaluations and track your goals throughout the year.

#### **Viewing Evaluations**

To view your performance evaluations, navigate to the "Evaluations" section from the main menu. Here you will see a list of all your past and current evaluations. You can filter and search for specific evaluations based on quarter, year, or status.

#### **Creating a New Evaluation**

To create a new evaluation, click the "New Evaluation" button and fill out the required information, including the evaluation period and your goals for the quarter.

#### **Managing Goals**

Within each evaluation, you can add, edit, and track your goals. For each goal, you can provide a description, target, and weight. You can also add comments and receive feedback from your supervisor.

#### **Completing an Evaluation**

At the end of the evaluation period, you will need to complete your self-assessment by rating your performance on each goal. Your supervisor will then review your assessment and provide their own rating and feedback.

### 3.4. Exam Management Module (EMM)

The EMM module allows you to take exams as part of the promotion process and view your results.

#### **Browsing Exams**

To browse available exams, navigate to the "Exams" section from the main menu. Here you will see a list of all the exams that are available for you to take. You can filter and search for specific exams based on subject, difficulty, or other criteria.

#### **Taking an Exam**

To take an exam, click the "Start Exam" button. You will be taken to the exam-taking interface, which includes a timer, question navigation, and an auto-save feature. Make sure to read the instructions carefully before you begin.

#### **Viewing Results**

After completing an exam, you can view your results in the "Results" section. The results page provides a detailed breakdown of your performance, including your score, the time you took, and your answers to each question. You will also receive recommendations on areas where you can improve.

### 3.5. User Roles and Permissions

The system has different user roles with different levels of access and permissions:

- **Staff Member:** Can view their own evaluations and exams, and complete their self-assessments.
- **Supervisor:** Can view and manage the evaluations of their team members, and provide feedback and ratings.
- **HR Admin:** Has full access to all evaluations and exams, and can manage user accounts and system settings.
- **Exam Administrator:** Can create and manage exams and question banks.
- **Question Author:** Can create and manage questions in the question bank.






## 4. API Reference

This section provides a detailed reference for the NBTI Promotion Automation API. The API is organized into several modules, each with its own set of endpoints.

### 4.1. Authentication API

- **POST /api/auth/register**: Register a new user.
- **POST /api/auth/login**: Authenticate a user and receive a JWT token.
- **POST /api/auth/refresh**: Refresh an expired JWT token.
- **POST /api/auth/logout**: Log out a user and invalidate their token.
- **GET /api/auth/me**: Get the current authenticated user's information.

### 4.2. User Management API

- **GET /api/users**: Get a list of all users (admin only).
- **GET /api/users/{id}**: Get a specific user by ID (admin only).
- **PUT /api/users/{id}**: Update a user's information (admin only).
- **DELETE /api/users/{id}**: Delete a user (admin only).

### 4.3. PMS API

- **GET /api/pms/dashboard**: Get PMS dashboard statistics.
- **GET /api/pms/evaluations**: Get a list of all evaluations for the current user.
- **POST /api/pms/evaluations**: Create a new evaluation.
- **GET /api/pms/evaluations/{id}**: Get a specific evaluation by ID.
- **PUT /api/pms/evaluations/{id}**: Update an evaluation.
- **POST /api/pms/evaluations/{id}/goals**: Add a new goal to an evaluation.
- **PUT /api/pms/goals/{id}**: Update a goal.
- **DELETE /api/pms/goals/{id}**: Delete a goal.

### 4.4. EMM API

- **GET /api/emm/dashboard**: Get EMM dashboard statistics.
- **GET /api/emm/exams**: Get a list of all available exams.
- **POST /api/emm/exams**: Create a new exam (admin only).
- **GET /api/emm/exams/{id}**: Get a specific exam by ID.
- **PUT /api/emm/exams/{id}**: Update an exam (admin only).
- **DELETE /api/emm/exams/{id}**: Delete an exam (admin only).
- **POST /api/emm/exams/{id}/start**: Start an exam submission.
- **GET /api/emm/submissions/{id}**: Get a specific exam submission by ID.
- **POST /api/emm/submissions/{id}/answers**: Submit an answer for a question.
- **POST /api/emm/submissions/{id}/submit**: Submit an exam for grading.
- **GET /api/emm/results**: Get a list of all exam results for the current user.






## 5. Deployment and Maintenance

This section provides instructions for deploying and maintaining the NBTI Promotion Automation system.

### 5.1. System Requirements

- **Docker:** Version 20.10 or higher.
- **Docker Compose:** Version 1.29 or higher.
- **Git:** For cloning the repository.
- **A server with at least 2GB of RAM and 2 CPU cores.**

### 5.2. Deployment Instructions

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd nbti-promotion-automation
   ```

2. **Configure the Environment:**

   Copy the appropriate environment file for your deployment environment:

   ```bash
   # For development
   cp .env.development .env

   # For production
   cp .env.production .env
   ```

   Then, edit the `.env` file to set your database credentials, secret keys, and other configuration options.

3. **Run the Deployment Script:**

   ```bash
   ./scripts/deploy.sh -e <environment>
   ```

   Replace `<environment>` with `development`, `staging`, or `production`.

### 5.3. Maintenance

#### **Backups**

Regular backups of the database and application data are essential. The following commands can be used to create backups:

- **Database Backup:**

  ```bash
  docker-compose exec database pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
  ```

- **Application Data Backup:**

  ```bash
  docker run --rm -v nbti_app_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .
  ```

#### **Monitoring**

The system includes health check endpoints for monitoring the status of the services:

- **Backend:** `http://localhost:5000/api/health`
- **Frontend:** `http://localhost:80/health`

You can also view the logs for each service using the following command:

```bash
docker-compose logs -f <service_name>
```

#### **Updates**

To update the application, pull the latest changes from the Git repository and run the deployment script again:

```bash
git pull
./scripts/deploy.sh -e <environment>
```






## 6. Project Structure

This section provides an overview of the project structure and the purpose of each directory and file.

```
nbti-promotion-automation/
├── backend/
│   └── nbti_api/
│       ├── src/
│       │   ├── models/
│       │   ├── routes/
│       │   ├── services/
│       │   ├── main.py
│       │   └── ...
│       ├── tests/
│       ├── Dockerfile
│       └── ...
├── frontend/
│   └── nbti-frontend/
│       ├── src/
│       │   ├── components/
│       │   ├── contexts/
│       │   ├── pages/
│       │   ├── services/
│       │   └── ...
│       ├── public/
│       ├── Dockerfile
│       └── ...
├── database/
│   └── init.sql
├── scripts/
│   └── deploy.sh
├── .env.development
├── .env.production
├── docker-compose.yml
├── README.md
└── ...
```

- **backend/nbti_api/**: Contains the Flask backend application.
  - **src/**: The main source code for the backend.
    - **models/**: SQLAlchemy database models.
    - **routes/**: API endpoints and routes.
    - **services/**: Business logic and services.
    - **main.py**: The main entry point for the Flask application.
  - **tests/**: Unit and integration tests for the backend.
  - **Dockerfile**: Docker configuration for the backend.
- **frontend/nbti-frontend/**: Contains the React frontend application.
  - **src/**: The main source code for the frontend.
    - **components/**: Reusable React components.
    - **contexts/**: React context providers for state management.
    - **pages/**: Top-level page components.
    - **services/**: API communication services.
  - **public/**: Static assets for the frontend.
  - **Dockerfile**: Docker configuration for the frontend.
- **database/**: Contains database initialization scripts.
- **scripts/**: Contains deployment and maintenance scripts.
- **.env.development**: Environment configuration for development.
- **.env.production**: Environment configuration for production.
- **docker-compose.yml**: Docker Compose configuration for orchestrating the deployment.
- **README.md**: The main README file for the project.



