# FinSentiments

FinSentiments is a Django-based web application for financial news sentiment analysis. It allows users to upload datasets or fetch financial news via APIs, preprocess text, run sentiment analysis using machine learning models, and visualize results.

---

##  Features

- User authentication (login, logout, register)  
- Upload CSV datasets or fetch news via NewsAPI  
- Preprocessing options (stopwords removal, lemmatization, etc.)  
- Sentiment analysis using trained ML models  
- Results storage and visualization with charts  
- Admin dashboard for model and user management  

---

##  Project Structure

```bash
finSentiments/
├── analysis/         # Main app for sentiment analysis
├── base/            # Base templates and static files
├── frontend/        # Frontend views and templates
├── ml/              # Machine learning models
│   └── model/
│       ├── classification/
│       └── regression/
├── static/          # Static files (js, css, images)
├── templates/       # Project-level templates
├── users/           # User authentication
├── Dockerfile
├── docker-compose.yml
├── .env
├── entrypoint.sh
├── finSentiments/   # Django project directory
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── manage.py
└── requirements.txt
```
.FinSentiments_FYP/screenshot/
---

---

---
##  Setup Instructions (AWS EC2, Ubuntu 24.04)

### 1. Start the EC2 Instance
- Instance: **i-0d8306e4e3ba62625** (t2.micro)  
- Public IP: **13.233.174.0**  
- Security group (`launch-wizard-3`) must allow ports:  
  - 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (temporary), 5432 (Postgres restricted to your IP).  

### 2. SSH into the Instance
```bash
ssh -i finSentiments-key.pem ubuntu@13.233.174.0
```

### 3. Install Docker & Docker Compose
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
exit
# reconnect
ssh -i finSentiments-key.pem ubuntu@13.233.174.0
```

### 4. Create Project Directory
```bash
mkdir ~/finSentiments
cd ~/finSentiments
mkdir logs static staticfiles media
chmod -R 755 logs static staticfiles media
```

### 5. Create Project Files

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
RUN mkdir -p /app/logs && chmod -R 755 /app/logs
ENV DJANGO_SETTINGS_MODULE=finSentiments.settings
RUN python manage.py collectstatic --noinput
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
```

#### docker-compose.yml
```yaml
version: "3.9"
services:
  web:
    build: .
    command: gunicorn finSentiments.wsgi:application --bind 0.0.0.0:8000 --workers=1 --threads=1
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - ./logs:/app/logs
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    restart: always
  db:
    image: postgres:15
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    expose:
      - "5432"
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      retries: 5
      timeout: 5s
volumes:
  postgres_data:
  static_volume:
```

#### .env
```env
DEBUG=0
SECRET_KEY=<generate-using-python-command-below>
NEWSAPI_KEY=077759f74514493185032c0e3ed16a14
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1],13.233.174.0
POSTGRES_DB=fin_db
POSTGRES_USER=fin_user
POSTGRES_PASSWORD=fin_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Generate a secure SECRET_KEY:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### entrypoint.sh
```bash
#!/bin/bash
python manage.py migrate
exec gunicorn finSentiments.wsgi:application --bind 0.0.0.0:8000 --workers=1 --threads=1
```
```bash
chmod +x entrypoint.sh
```

---

### 6. Build and Run
```bash
docker-compose build
docker-compose up -d
```

### 7. Apply Migrations & Create Superuser
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 8. Access the App
- Open: [http://13.233.174.0:8000/](http://13.233.174.0:8000/)  

---
✨ This deployment phase was a deep dive into cloud deployment, security-first architecture, and scalable design.

 𝗔𝗪𝗦 𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆 𝗚𝗿𝗼𝘂𝗽𝘀: http://3.110.30.152:8000/
 𝗗𝗼𝗰𝗸𝗲𝗿 𝗜𝗺𝗮𝗴𝗲𝘀: https://lnkd.in/gcxYdxMv
 
 ---

 ---
##  Usage
- **Login/Register** via navigation bar.  
- **Upload Dataset** (CSV).  
- **Fetch News** with NewsAPI.  
- **View Results** in charts and download.  
- **Admin** at `/admin/` for model management.  

---

##  Requirements
- Python 3.11 (via Docker)  
- Docker & Docker Compose  
- PostgreSQL 15  
- Dependencies: Django, gunicorn, psycopg2-binary, pandas, scikit-learn, nltk, textblob, imbalanced-learn, prophet, plotly, torch, spacy, etc.  

---

##  Notes
- **Resource Constraints:** t2.micro is weak → add 2GB swap:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
```
- Better: upgrade to **t3.medium**.  
- Place trained ML models under `ml/model/classification/` or `ml/model/regression/`.  

---

##  Troubleshooting
- **Build fails?** → check memory (`free -m`), add swap.  
- **Postgres error?** → verify `POSTGRES_HOST=db`.  
- **Timeouts?** → open ports in Security Group.  

---

## License
MIT License.  

---

##  Linkdin Post
https://www.linkedin.com/feed/update/urn:li:activity:7368208997394350081/

