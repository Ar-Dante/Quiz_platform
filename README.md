<h3>/Quiz_platform </h3>
Description:
A FastAPI-based web application following best practices for building a robust backend system. The project focuses on user management, company management, quizzes, analytics, notifications, and more.

**Key Features:**
- User management with authentication and authorization.
- Company creation and management with roles.
- Quiz creation and user participation.
- Data storage in PostgreSQL and Redis.
- Notifications and scheduled script for user engagement.
- Exporting data to JSON and CSV.
- Deployment on AWS with GitHub Actions.
- Role-based access control for secure operations.
- Integration with external services like Auth0.
- User profile customization with avatars.
- Email notifications for important events.
- Continuous Integration (CI) and Continuous Deployment (CD) workflows.
- Comprehensive test coverage for code quality assurance.
- Data import from Excel for quiz management.


<h3>To run the application locally , follow these steps:</h3>
Clone the Repository:

Copy code

<code>git clone https://github.com/Ar-Dante/Meduzzen_internship_fastapi.git </code>

<h3>Navigate to the Project Directory:</h3>

Copy code

<code>cd Meduzzen_internship_fastapi</code>

<h3>Install Dependencies and Create a Virtual Environment using Poetry:</h3>

Copy code

<code>poetry install</code>

<h3>Set Up Environment Variables:</h3>

Copy the .env.sample file to .env and fill in the necessary configuration variables.


<h3>Start the FastAPI Application:</h3>

<h3>You can start the FastAPI application using either of the following methods:</h3>

Method 1: Using Poetry and Uvicorn:

Copy code

<code>poetry run uvicorn main:app --host localhost --port 8000 --reload</code>

Method 2: Using if __name__ == '__main__': block in main.py:

You can use the following block:

<code>if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)</code>

This allows you to run the application directly from the main.py file.

<h3>Access the Application:</h3>

Open your web browser and visit http://localhost:8000/ to access the health check endpoint. 
You should receive a JSON response indicating the status of the application.

<h3>Running Tests</h3>

To run tests for the application using Poetry, follow these steps:

<h3>Run Tests using pytest:</h3>

Copy code

<code>pytest</code>

This will execute all the tests in your project.

<h3>Building the Docker Image<h3>

<code>docker build -t your-application</code>

<h3>Running the Application in Docker<h3>

<code>docker run -d -p 8080:80 --name your-app-container your-application</code>

<h3>Building the Docker Image for tests<h3>

<code>docker build -t test_image -f Dockerfile_test </code>

<h3>Running tests in Docker<h3>

<code>docker run --rm test_image</code>

 <h3>Create Migrations</h3>
 
<code>alembic revision --autogenerate -m "your_migration_message"</code>

 <h3>Apply Migrations</h3>
 
<code>alembic upgrade head</code>
