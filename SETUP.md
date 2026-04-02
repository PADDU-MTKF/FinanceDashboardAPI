# Setup Instructions

Follow these steps to set up and run the Finance Dashboard API on your local machine.

## Prerequisites
- **Python 3.8+**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).

## 1. Clone the Repository
Open your terminal or command prompt and run the following command to clone the project:
```bash
git clone https://github.com/PADDU-MTKF/FinanceDashboardAPI.git
cd FinanceDashboard_API/financeDashboard
```

## 2. Set Up a Virtual Environment (Recommended)
It's best practice to use a virtual environment to manage your project's dependencies without affecting your global Python installation.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Requirements
Install all the necessary Python packages using `pip`:
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, ensure you install `django` and `djangorestframework`.)*

## 4. Run the Development Server
This project implements server caching and might not strictly depend on a traditional database for its custom abstractions, but it's always safe to run generic migrations first:
```bash
python manage.py migrate
```

Start the Django development server:
```bash
python manage.py runserver
```

## 5. Accessing the API
Once the server is running, you can access the API endpoints locally. By default, Django runs on port 8000.

- **Base URL:** `http://127.0.0.1:8000/` or `http://localhost:8000/`
- **Health Check Endpoint:** `http://127.0.0.1:8000/api/`

## Next Steps
For detailed documentation on the available API endpoints, roles, request formats, and responses, please refer to the main [API Documentation (README.md)](./README.md).
