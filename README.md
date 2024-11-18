# **Video Management API**

A Django-based RESTful API for managing video files. This application allows users to upload, trim, merge video clips, and generate shareable links with expiration. The system enforces configurable video size and duration limits.

---

## **Features**

- **Video Upload**: Users can upload videos with configurable size and duration limits.
- **Video Trimming**: Trim uploaded videos from the start or end.
- **Video Merging**: Combine multiple video clips into a single file.
- **Shareable Links**: Generate time-limited, shareable links for uploaded videos.
- **API Documentation**: Interactive API documentation available via [Postman]([https://example.com](https://github.com/suman1buie/Video-files-REST-API/blob/main/Video%20Management%20API.postman_collection.json).

---

## **Prerequisites**

Ensure the following are installed on your system:

- **Python 3.13+**
- **SQLite** (comes pre-installed with Python)
- **Virtual environment tool**: `pipenv` or `virtualenv`

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone https://github.com/suman1buie/Video-files-REST-API.git
cd Video-files-REST-API

```

### **2. Setup the project**

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r requirements.txt

```
### **4. command to run the API server**
```
create .env in the main project dir and assign the proper value same as like .env.dev file
before that, you need to create one s3 bucket and AWS cred to access the same. You need to provide this info as well
```

### **5. command to run the API server**

```bash
python manage.py runserver 8080

```

### **6. Run the testcase**

```bash
python manage.py test

```

### **7. check code covrage**

```bash
coverage run manage.py test
coverage report -m

```
For API DOC please import ```Video Management API.postman_collection.json ``` in your postman collection



