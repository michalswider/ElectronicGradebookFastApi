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

## **Installation**

### **1. Clone the repository:**
   ```bash
   git clone https://github.com/michalswider/ElectronicGradeBookFastApi.git
   ```

## **Configuration**

### **1. Rename the file:**
 - Go to the project directory ElectronicGradebook .
 - Change the name of the `.env.example` file to `.env`.

### **2. Update environment variables**
Open the `.env` file and update the environmental variable values with the appropriate data for your environment.

```plaintext
DATABASE_URL=postgresql://<username>:<password>@<host>/<database_name>
```
