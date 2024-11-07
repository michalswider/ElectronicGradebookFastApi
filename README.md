# **ElectronicGradeBookFastApi**

Application for managing students, teachers, administrators, subjects, grades and attendance in schools. This project is built with FastAPI, SQLAlchemy and PostgreSQL.

## **Features**
- **Student Management**: Add and manage student profiles.
- **Teacher Management**: Add and manage teacher profiles.
- **Subject Management**: Add and manage subjects.
- **Class Management**: Manage classes and their students.
- **Grade Management**: Record and view student grades by subject.
- **Attendance Management**: Track student attendance and manage records.

## **Technologies**
- **FastAPI**: Web framework for building APIs with Python.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library.
- **PostgreSQL**: Relational database management system.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Pydantic**: Data validation and settings management using Python type annotations, primarily used for request validation and data serialization in FastAPI.
- **RotatingFileHandler**: For managing log files with rotation.
- **Pytest**: Framework for writing unit tests to ensure application reliability and correctness.
- **Docker**: The application is containerized, making it easy to deploy and run in different environments.

## **Installation**

### **1. Clone the repository:**
   ```bash
   git clone https://github.com/michalswider/ElectronicGradeBookFastApi.git
   ```

## **Configuration**

### **1. Using Docker:**
To run the application with Docker, use the provided `compose.yml` file. Build and start the containers with:
   ```bash
   docker-compose up --build
   ```
Upon startup, the FastAPI application will automatically create an `admin` user in the database with the password `admin`.

The application will be available at the following ports:
- **FastAPI**: `http://localhost:8000`
- **pgadmin4**: `http://localhost:8080`

pgAdmin login:
- **Email Address**: `admin@example.com`
- **Password**: `admin`
