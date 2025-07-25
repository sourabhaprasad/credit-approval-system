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

Create a `.env` file:

```
POSTGRES_DB=creditdb
POSTGRES_USER=credituser
POSTGRES_PASSWORD=creditpass
```

---

## **3. Start Services (Automated)**

We have automated the setup steps (starting services, running migrations, fixing sequences, and initial data ingestion) using an **`init.sh`** script.

Run:

```bash
bash init.sh
```

This script will:

- Start all services (Django API, PostgreSQL, Redis, Celery Worker)
- Apply database migrations
- Fix database sequences
- Run initial data ingestion via Celery (from `customer_data.xlsx` and `loan_data.xlsx`)
- Test the `/api/customers/register/` API with a sample customer

**Expected output:**

- **API response:**

  ```json
  {
    "customer_id": 1,
    "first_name": "Init",
    "last_name": "Test",
    "age": 25,
    "phone_number": "9999999999",
    "monthly_salary": 50000,
    "approved_limit": 1800000,
    "current_debt": 0.0
  }
  ```

- **Final message:**

  ```
  >>> Setup completed successfully!
  ```

---

## **4. Manual Setup (Optional)**

If you prefer to run the steps manually:

### **Start Services**

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
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### **Fix Sequences**

```bash
docker-compose exec web python manage.py fix_sequences
```

### **Data Ingestion**

The initial `customer_data.xlsx` and `loan_data.xlsx` files are ingested via Celery:

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
  "customer_id": 301,
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
-d '{
  "first_name": "Alice",
  "last_name": "Smith",
  "age": 28,
  "monthly_income": 80000,
  "phone_number": "9876543215"
}'
```

---

### **2. Check Loan Eligibility**

**POST** `/api/loans/check-eligibility/`

**Request:**

```json
{
  "customer_id": 301,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}
```

**Response:**

```json
{
  "customer_id": 301,
  "approval": true,
  "interest_rate": 10,
  "corrected_interest_rate": 10,
  "tenure": 12,
  "monthly_installment": 17583.18
}
```

**Example CURL:**

```bash
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 301,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}'
```

---

### **3. Create Loan**

**POST** `/api/loans/create-loan/`

**Request:**

```json
{
  "customer_id": 301,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}
```

**Response:**

```json
{
  "loan_id": 1,
  "customer_id": 301,
  "loan_approved": true,
  "message": "Loan approved",
  "monthly_installment": 17583.18
}
```

**Example CURL:**

```bash
curl -X POST http://localhost:8000/api/loans/create-loan/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 301,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}'
```

---

### **4. View Loan**

**GET** `/api/loans/view-loan/{loan_id}/`

**Response:**

```json
{
  "loan_id": 1,
  "customer": {
    "customer_id": 301,
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

**Example CURL:**

```bash
curl -X GET http://localhost:8000/api/loans/view-loan/1/
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

**Example CURL:**

```bash
curl -X GET http://localhost:8000/api/loans/view-loans/301/
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

## Edge Cases

### **1. Invalid `customer_id` during Loan Eligibility Check**

```bash
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 9999,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}'
```

**Expected Response (Example):**

```json
{
  "error": "Customer not found."
}
```

---

### **2. Negative Loan Amount**

```bash
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 301,
  "loan_amount": -50000,
  "interest_rate": 10,
  "tenure": 12
}'
```

**Expected Response (Example):**

```json
{
  "error": "loan_amount must be greater than 0."
}
```

---

### **3. Negative or Zero Tenure**

```bash
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 301,
  "loan_amount": 100000,
  "interest_rate": 10,
  "tenure": 0
}'
```

**Expected Response (Example):**

```json
{
  "error": "tenure must be greater than 0"
}
```

---

### **4. Loan Amount Exceeding 50% EMI Limit**

```bash
curl -X POST http://localhost:8000/api/loans/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 301,
  "loan_amount": 5000000,
  "interest_rate": 12,
  "tenure": 12
}'
```

**Expected Response (Example):**

```json
{
  "customer_id": 301,
  "approval": false,
  "interest_rate": 12.0,
  "corrected_interest_rate": 12.0,
  "tenure": 12,
  "monthly_installment": 444243.94,
  "reason": "EMI exceeds 50% of monthly salary"
}
```

---

### **5. Non-Existing Loan ID in View Loan**

```bash
curl -X GET http://localhost:8000/api/loans/view-loan/999/
```

**Expected Response (Example):**

```json
{
  "error": "No loan matches the given query."
}
```

## **Docker Services**

- **web** – Django API service
- **db** – PostgreSQL
- **redis** – Redis broker for Celery
- **worker** – Celery background worker

---

## **Project Features**

- Credit Score Calculation (based on past loans & EMIs)
- EMI Limit Checks (≤ 50% of salary)
- Automatic Interest Rate Correction based on credit score slab
- Data ingestion from Excel via Celery tasks
- PostgreSQL persistence
- Dockerized setup (single `docker-compose up` to run all services)
