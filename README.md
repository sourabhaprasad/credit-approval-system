# Credit Approval System

A backend service for managing **customer credit approvals**, **loan eligibility checks**, and **loan creation** using Django REST Framework, Celery, PostgreSQL, and Docker. The project includes ingestion of initial data from Excel files, automatic EMI calculation, and loan credit scoring.

---

## **Tech Stack**

- **Backend:** Python 3.11, Django 5+, Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Async Tasks:** Celery + Redis
- **Containerization:** Docker & Docker Compose
- **Testing:** Django Test Framework (unit tests)
- **Data ingestion:** Pandas (Excel data ingestion)

---

## **Project Setup**

### **1. Clone the repository**

```bash
git clone https://github.com/sourabhaprasad/credit-approval-system.git
cd credit-approval-system
```

### **2. Environment Variables**

Create a .env file:

```
POSTGRES_DB=creditdb
POSTGRES_USER=credituser
POSTGRES_PASSWORD=creditpass
```

### **3. Start Services**

```bash
docker-compose up --build
```

This starts:

- Django API ([http://localhost:8000](http://localhost:8000/))
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- Celery Worker

### **Database Migrations**

```bash
docker-compose exec web python manage.py migrate
```

### **Data Ingestion**

The initial customer_data.xlsx and loan_data.xlsx files are ingested via Celery:

```bash
docker-compose exec web python manage.py shell
```

```python
from customers.tasks import ingest_data
ingest_data.delay()
```

---

## **API Endpoints**

### **1. Register a Customer**

**POST** `/api/customers/register/`

**Request:**

```json
{
  "first_name": "Alice",
  "last_name": "Smith",
  "age": 28,
  "monthly_income": 80000,
  "phone_number": "9876543215"
}
```

**Response:**

```json
{
  "customer_id": 302,
  "first_name": "Alice",
  "last_name": "Smith",
  "age": 28,
  "phone_number": "9876543215",
  "monthly_salary": 80000,
  "approved_limit": 2900000,
  "current_debt": 0.0
}
```

**Example CURL:**

```bash
curl -X POST http://localhost:8000/api/customers/register/ \
-H "Content-Type: application/json" \
-d '{"first_name": "Alice","last_name": "Smith","age": 28,"monthly_income": 80000,"phone_number": "9876543215"}'
```

---

### **2. Check Loan Eligibility**

**POST** `/api/loans/check-eligibility/`

**Request:**

```json
{
  "customer_id": 302,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}
```

**Response:**

```json
{
  "customer_id": 302,
  "approval": true,
  "interest_rate": 10,
  "corrected_interest_rate": 10,
  "tenure": 12,
  "monthly_installment": 17583.18
}
```

---

### **3. Create Loan**

**POST** `/api/loans/create-loan/`

**Request:**

```json
{
  "customer_id": 302,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}
```

**Response:**

```json
{
  "loan_id": 1,
  "customer_id": 302,
  "loan_approved": true,
  "message": "Loan approved",
  "monthly_installment": 17583.18
}
```

---

### **4. View Loan**

**GET** `/api/loans/view-loan/{loan_id}/`

**Response:**

```json
{
  "loan_id": 1,
  "customer": {
    "customer_id": 302,
    "first_name": "Alice",
    "last_name": "Smith",
    "phone_number": "9876543215",
    "age": 28
  },
  "loan_amount": 200000.0,
  "interest_rate": 10.0,
  "monthly_installment": 17583.18,
  "tenure": 12
}
```

---

### **5. View All Loans for a Customer**

**GET** `/api/loans/view-loans/{customer_id}/`

**Response:**

```json
[
  {
    "loan_id": 1,
    "loan_amount": 200000.0,
    "interest_rate": 10.0,
    "monthly_installment": 17583.18,
    "repayments_left": 12
  }
]
```

---

## **Testing**

**Run Unit Tests:**

```bash
docker-compose exec web python manage.py test
```

**Test Coverage:**

- Customer Registration
- Loan Eligibility
- Loan Creation
- Loan Retrieval
- Edge Cases: Invalid customer_id, negative loan_amount/tenure

---

## **Docker Services**

- web – Django API service
- db – PostgreSQL
- redis – Redis broker for Celery
- worker – Celery background worker

---

## **Project Features**

- Credit Score Calculation (based on past loans & EMIs)
- EMI Limit Checks (≤ 50% of salary)
- Automatic Interest Rate Correction based on credit score slab
- Data ingestion from Excel via Celery tasks
- PostgreSQL persistence
- Dockerized setup (single docker-compose up to run all services)

---
