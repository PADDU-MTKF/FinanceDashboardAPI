# Finance Dashboard API Documentation
This API is built using Django REST Framework to manage users and financial transactions.

> **Getting Started:** Set up and run this project locally:
> [Setup Instructions (SETUP.md)](./SETUP.md).

---

# Tech Stack

- Python 3.x
- Django 4.x
- Django REST Framework
- Django Cache as database (In-Memory)

---
 
## Authentication & Authorization
Most endpoints require authentication. To access protected endpoints, you must include the following headers in your HTTP request:
- `TOKEN`: Your authentication token (obtained via the `/api/login` endpoint).
- `USERNAME`: Your username.

Users have specific roles (e.g., viewer, analyst, Admin, transactionAdmin, userAdmin, masterAdmin) that determine their permissions for each API. If a user attempts to access an endpoint they don't have permission for, the API will return a `403 Forbidden` response.

| Role | Access |
|------|-------|
| viewer | Read transactions |
| analyst | Read + insights |
| transactionAdmin | Full transaction access |
| userAdmin | Manage users |
| masterAdmin | Full system access |

---

## 1. General & Authentication APIs

### 1.1 Home / Health Check
- **Endpoint:** `/` or `/api/`
- **Method:** `GET`
- **Protected:** No
- **Access Level:** Anyone (No authentication required)
- **Description:** Checks if the API is running correctly.
- **Parameters:** None
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "API is working",
      "data": {
          "status": "ok"
      },
      "errors": null
  }
  ```

### 1.2 Login
- **Endpoint:** `/api/login`
- **Method:** `POST`
- **Protected:** No
- **Access Level:** Anyone (No authentication required)
- **Description:** Authenticates a user and returns their data along with a session token.
- **Body Parameters:**
  - `username` (string, **required**)
  - `password` (string, **required**)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Login successful",
      "data": {
          "user": {
              "uid": "9924bd96-00be-4e24-b03c-763e453ad985",
              "username": "johndoe",
              "name": "John Doe",
              "role": "admin",
              "status": "active"
          },
          "token": "valid_token_string..."
      },
      "errors": null
  }
  ```

---

## 2. User Management APIs

### 2.1 Create User
- **Endpoint:** `/api/createUser`
- **Method:** `POST`
- **Protected:** Yes
- **Access Level:** Restricted based on role hierarchy.
- **Description:** Creates a new user in the system.
- **Body Parameters:**
  - `name` (string, **required**)
  - `username` (string, **required**)
  - `password` (string, **required**)
  - `role` (string, optional, default: `"viewer"`)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 201,
      "message": "User created successfully",
      "data": {
          "uid": "9924bd96-00be-4e24-b03c-763e453ad985",
          "name": "Jane Smith",
          "username": "janesmith",
          "role": "viewer",
          "status": "active"
      },
      "errors": null
  }
  ```

### 2.2 Delete User
- **Endpoint:** `/api/deleteUser`
- **Method:** `DELETE`
- **Protected:** Yes
- **Access Level:** Administrators with appropriate rights.
- **Description:** Deletes an existing user by username.
- **Body Parameters:**
  - `username` (string, **required**)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "User deleted successfully",
      "data": null,
      "errors": null
  }
  ```

### 2.3 Update User Role
- **Endpoint:** `/api/updateUserRole`
- **Method:** `PUT`
- **Protected:** Yes
- **Access Level:** Administrators with appropriate rights.
- **Description:** Updates the role of an existing user.
- **Body Parameters:**
  - `username` (string, **required**)
  - `role` (string, **required**)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "User role updated successfully",
      "data": {
          "uid": "9924bd96-00be-4e24-b03c-763e453ad985",
          "name": "Jane Smith",
          "username": "janesmith",
          "role": "analyst",
          "status": "active"
      },
      "errors": null
  }
  ```

### 2.4 Update User Status
- **Endpoint:** `/api/updateUserStatus`
- **Method:** `PUT`
- **Protected:** Yes
- **Access Level:** Administrators with appropriate rights.
- **Description:** Updates the active/inactive status of an existing user.
- **Body Parameters:**
  - `username` (string, **required**)
  - `status` (string, **required**)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "User status updated successfully",
      "data": {
          "uid": "9924bd96-00be-4e24-b03c-763e453ad985",
          "name": "Jane Smith",
          "username": "janesmith",
          "role": "analyst",
          "status": "inactive"
      },
      "errors": null
  }
  ```

### 2.5 List Users
- **Endpoint:** `/api/listUsers`
- **Method:** `GET`
- **Protected:** Yes
- **Access Level:** Users with view permissions for the directory.
- **Description:** Fetches a list of all users in the system.
- **Parameters:** None
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Users fetched successfully",
      "data": [
          { "uid": "9924bd96-00be-4e24-b03c-763e453ad985", "username": "admin", "name": "System Admin", "role": "admin", "status": "active" },
          { "uid": "1bd3792d-30d4-4ff6-a666-091b362f7a1b", "username": "janesmith", "name": "Jane Smith", "role": "analyst", "status": "active" }
      ],
      "errors": null
  }
  ```

---

## 3. Transaction Management APIs

### 3.1 Add Transaction
- **Endpoint:** `/api/addTransaction`
- **Method:** `POST`
- **Protected:** Yes
- **Access Level:** Users authorized to create a transaction.
- **Description:** Creates a new financial transaction.
- **Body Parameters:**
  - `amount` (float/decimal, **required**)
  - `type` (string, **required**)
  - `category` (string, **required**)
  - `notes` (string, optional, default: `""`)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 201,
      "message": "Transaction added",
      "data": {
          "tid": "txn_89adf8a98f",
          "amount": 1500.00,
          "type": "income",
          "category": "freelance",
          "notes": "Website project payment"
      },
      "errors": null
  }
  ```

### 3.2 Update Transaction
- **Endpoint:** `/api/updateTransaction`
- **Method:** `PUT`
- **Protected:** Yes
- **Access Level:** Users authorized to edit transactions.
- **Description:** Updates an existing financial transaction.
- **Body Parameters:**
  - `tid` (string, **required**) - Transaction ID
  - `amount` (float/decimal, optional)
  - `type` (string, optional)
  - `category` (string, optional)
  - `notes` (string, optional)
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Transaction updated",
      "data": {
          "tid": "txn_89adf8a98f",
          "amount": 1600.00,
          "type": "income",
          "category": "freelance",
          "notes": "Updated final payment"
      },
      "errors": null
  }
  ```

### 3.3 Delete Transaction
- **Endpoint:** `/api/deleteTransaction`
- **Method:** `DELETE`
- **Protected:** Yes
- **Access Level:** Users authorized to delete transactions.
- **Description:** Deletes a financial transaction from the records.
- **Body Parameters:**
  - `tid` (string, **required**) - Transaction ID
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Transaction deleted",
      "data": null,
      "errors": null
  }
  ```

### 3.4 Get Transactions
- **Endpoint:** `/api/getTransactions`
- **Method:** `GET`
- **Protected:** Yes
- **Access Level:** Users authorized to view transactions.
- **Description:** Fetches a paginated list of transactions, optionally filtered by `type` and `category`.
- **Query Parameters:**
  - `page` (integer, optional, default: `0`)
  - `limit` (integer, optional, default: `10`)
  - `type` (string, optional)
  - `category` (string, optional)
- **Example Request:** `/api/getTransactions?page=0&limit=25&type=expense&category=food`
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Transactions fetched",
      "data": [
          { "tid": "txn_abc123", "amount": 45.5, "type": "expense", "category": "food", "notes": "Lunch" },
          { "tid": "txn_def456", "amount": 12.0, "type": "expense", "category": "food", "notes": "Coffee" }
      ],
      "errors": null
  }
  ```

### 3.5 Get Transaction Insights
- **Endpoint:** `/api/getInsights`
- **Method:** `GET`
- **Protected:** Yes
- **Access Level:** Users authorized to view aggregated financial metrics.
- **Description:** Fetches aggregated insights or summaries for the user's transactions based on records.
- **Parameters:** None
- **Example Response:**
  ```json
  {
      "success": true,
      "code": 200,
      "message": "Insights fetched",
      "data": {
          "total_income": 5000.00,
          "total_expense": 2500.00,
          "netBalance": 2500.00,
          "categoryTotal": {
              "freelance": 5000.00,
              "food": 500.00,
              "rent": 2000.00
          },
          "recentAct": [
              {
                "tid": "txn_abc123",
                "amount": 5000.0,
                "type": "income",
                "category": "freelance",
                "notes": ""
              },
              {
                "tid": "txn_def456",
                "amount": 500.0,
                "type": "expense",
                "category": "food",
                "notes": "Lunch"
              }
          ],
          "topCategory": "food"
        },
      "errors": null
  }
  ```
