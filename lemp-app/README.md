# LEMP Flask App

This is a minimal Python web application running on a **LEMP stack**  
(Linux, Nginx, MySQL/MariaDB, Python).

It uses **Flask**, **Gunicorn**, and **Nginx** as a reverse proxy.  
This project is deployed and running on the **CSC cPouta** cloud service.

---

## 🧱 Project structure

```
lemp-app/
├── app.py
├── requirements.txt
├── venv/
└── README.md
```

---

## ⚙️ Setup instructions

### 1. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally (development)
```bash
python app.py
```

Then open your browser at:
```
http://<server_ip>:5000
```

---

## 🚀 Run in production (Gunicorn + Nginx)

Test with Gunicorn:
```bash
gunicorn --bind 127.0.0.1:5000 app:app
```

Nginx configuration file:
```
/etc/nginx/sites-available/lemp-app
```

Enable the site and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/lemp-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 Database connection

The app connects to a MySQL or MariaDB database using credentials defined in `.env`:
```
HOST=localhost
USER=exampleuser
PASSWORD=change_this_strong_password
NAME=exampledb
```

---

## 🧰 Requirements

```
# Virtual environment: venv
# (create with "python3 -m venv venv" before installation)

Flask==3.1.2
gunicorn==23.0.0
mysql-connector-python==9.5.0
python-dotenv==1.0.1
```

---

## ☁️ Cloud Environment

This project is hosted in the **CSC cPouta cloud environment**,  
a Finnish OpenStack-based infrastructure-as-a-service (IaaS) platform.  

cPouta allows users to create and manage virtual machines, networks, and storage  
resources for developing and running research and education-related applications.  

It provides a secure, scalable, and high-performance environment for deploying services  
like this Flask-based LEMP web application.

---

