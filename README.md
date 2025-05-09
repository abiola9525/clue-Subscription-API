# Subscription Management API

A Django REST Framework API for handling user subscriptions including subscribing, upgrading, and cancelling subscription plans.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/abiola9525/clue-Subscription-API.git
```

### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS&Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server

```bash
python manage.py runserver
```

---

## Optimization Choices

### Single Active Subscription Enforcement

Each user can only have **one active subscription** at a time. This ensures clean data logic and eliminates billing conflicts.

### Indexed Queries

Database indexing is used on frequently queried fields like:

- `is_active`
- `user`
- `end_date`

This significantly improves the lookup speed and performance for large datasets.

### Controlled Upgrade Flow

Users can only upgrade to **higher-priced** plans. This avoids downgrades that could lead to exploitation of plan benefits.

### Serializer Nesting

The `UserSubscriptionSerializer` uses a nested `SubscriptionPlanSerializer` to deliver clean and detailed responses, reducing client-side data mapping needs.

### Auto-Generated API Docs

All views are decorated with `@swagger_auto_schema`, enabling automatic documentation via Swagger UI perfect for quick onboarding and API testing.

---

## Authentication

All subscription-related endpoints require JWT or token-based authentication using `IsAuthenticated`.

---

## Key Endpoints

The Base URL: http:127.0.0.1:8000/api

| Method   | Endpoint                                 | Description               |
| -------- | ---------------------------------------- | ------------------------- |
| `POST` | `/subscription/subscribe/<plan_id>/`   | Subscribe to a plan       |
| `POST` | `/subscription/upgrade/<new_plan_id>/` | Upgrade current plan      |
| `POST` | `/subscription/cancel/`                | Cancel current plan       |
| `GET`  | `/subscription/active/`                | View active subscription  |
| `GET`  | `/subscription/history/`               | View subscription history |
| `POST` | `/account/register/`                   | Register User             |
| `POST` | `/account/login`                       | Login User                |
| `GET`  | `account/`                             | Get User Details          |
| `PUT`  | `account/`                             | Edit User Details         |
