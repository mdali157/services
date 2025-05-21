## Getting Started

Follow the steps below to set up and run the project on your local machine.

### 1. Extract the ZIP

Extract the provided ZIP file to your desired directory.

### 2. Create a Virtual Environment

Open a terminal/command prompt inside the extracted project folder and run:

#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### For linux/MAC:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install Requirements
```bash
pip install -r requirements.txt
```
#### Make Db changes
```bash
python manage.py migrate
```
#### Create SuperUser:
```bash
python manage.py createsuperuser
```
#### Run Server:
```bash
python manage.py runserver
```