# FinSentiments — Financial News Sentiment Analysis using Machine Learning & Deep Learning

FinSentiments is an end-to-end AI/ML application that combines **Machine Learning, Deep Learning, Natural Language Processing (NLP), and Django** to analyze sentiment in financial news.

The project bridges ML model experimentation with a web-based platform, enabling users to upload financial datasets, retrieve news through NewsAPI, analyze sentiment, and visualize company-specific sentiment trends. It also explores sentiment trend forecasting over 7-day and 14-day horizons.

The application is containerized using Docker and Docker Compose and is designed for deployment on AWS EC2 with PostgreSQL.

## Key Features

- **Machine Learning:** Train, compare, and evaluate traditional ML classifiers for financial sentiment classification.
- **Deep Learning & Transformers:** Experiment with FinBERT and RoBERTa for financial text classification.
- **NLP Preprocessing:** Clean financial text, remove stopwords, and apply lemmatization.
- **Multiple Data Sources:** Upload CSV datasets or retrieve financial news using NewsAPI.
- **Company-Specific Analysis:** Analyze financial news sentiment associated with companies.
- **Sentiment Trend Forecasting:** Visualize sentiment trends and Prophet-based forecasts over 7-day and 14-day horizons.
- **Interactive Dashboards:** Present sentiment analysis results through charts and visualizations.
- **Django Integration:** Integrate trained models into a web application with user authentication and analysis history.
- **Database Persistence:** Store application data and analysis results using PostgreSQL.
- **Containerization:** Package the application and database services using Docker and Docker Compose.
- **Cloud Deployment:** Deploy the containerized application on AWS EC2.

> **Note:** The forecasting component focuses on sentiment scores and trends, not necessarily future stock prices or market direction.

## Machine Learning Workflow

The project follows an end-to-end NLP and ML workflow:

1. **Data collection:** Load financial news from CSV files or retrieve articles through NewsAPI.
2. **Text preprocessing:** Clean text, remove stopwords, and apply lemmatization.
3. **Feature engineering:** Transform text into numerical representations using TF-IDF for traditional ML models.
4. **Model training:** Train and compare traditional classifiers and experiment with transformer-based models.
5. **Model evaluation:** Evaluate classification performance using appropriate metrics such as accuracy, precision, recall, and F1-score.
6. **Model integration:** Load trained models into Django for application-level inference.
7. **Sentiment analysis:** Generate sentiment classifications or scores for financial news.
8. **Trend analysis:** Aggregate company-related sentiment and visualize historical trends and supported forecasts.
9. **Deployment:** Run the application in Docker containers on AWS EC2.

## Models and Algorithms

### Traditional Machine Learning

The project's model experimentation includes the following classifiers, where implemented:

- Logistic Regression
- Support Vector Machine (SVM)
- Random Forest
- Naive Bayes
- XGBoost
- LightGBM
- CatBoost

**Feature engineering:** TF-IDF  
**Optimization:** Hyperparameter tuning, where applied  
**Evaluation:** Classification metrics and comparison of model performance

### Deep Learning and Transformer Models

- **FinBERT:** Transformer-based model designed for financial language and sentiment analysis.
- **RoBERTa:** Transformer architecture used for financial text classification experiments.
- **PyTorch:** Deep learning framework for model training and experimentation.
- **Hugging Face Transformers:** Tools for working with pretrained transformer models.

Class-weighted loss can be used in applicable training experiments to help address imbalanced sentiment classes.

### Sentiment Trend Forecasting

Prophet is used in the forecasting workflow to model sentiment-score trends over selected horizons of 7 or 14 days.

These forecasts describe sentiment trends and should not be interpreted as guaranteed stock-price predictions.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Machine Learning | Scikit-learn, XGBoost, LightGBM, CatBoost |
| Deep Learning | PyTorch |
| NLP & Transformers | TF-IDF, Hugging Face Transformers, FinBERT, RoBERTa |
| Data Processing | Pandas, NumPy |
| Forecasting | Prophet |
| Backend | Django, Gunicorn |
| Database | PostgreSQL |
| Visualization | Plotly, charts and dashboards |
| Data Source | NewsAPI |
| Containerization | Docker, Docker Compose |
| Cloud | AWS EC2, Ubuntu |
| Web Server | Gunicorn; Nginx where configured |

## System Architecture

```text
CSV Upload / NewsAPI
         |
         v
Financial News Collection
         |
         v
NLP Preprocessing
         |
         v
Feature Engineering
(TF-IDF / Transformer Tokenization)
         |
         v
Trained ML / Deep Learning Models
         |
         v
Sentiment Classification and Scores
         |
         v
Company-Specific Sentiment Analysis
         |
         v
Trend Analysis and Forecasting
         |
         v
Django Application and Dashboards
         |
         v
PostgreSQL + Docker + AWS EC2
```

## Project Structure

```text
FinSentiments_FYP/
├── analysis/               # Sentiment analysis application
├── base/                   # Base templates and static resources
├── finSentiments/          # Django project configuration
├── frontend/               # Frontend views and templates
├── users/                  # User authentication
├── ml/
│   └── model/
├── static/                 # CSS, JavaScript and images
├── templates/              # Project-level templates
├── logs/                   # Application logs
├── Dockerfile              # Application image configuration
├── docker-compose.yml      # Container orchestration
├── entrypoint.sh           # Container startup script
├── manage.py               # Django management utility
└── requirements.txt        # Python dependencies
```

*The exact directories and model artifacts should match the current repository.*

## Application Capabilities

- Register, log in, and manage user sessions.
- Upload CSV datasets for sentiment analysis.
- Retrieve financial news through NewsAPI.
- Preprocess financial text before model inference.
- Generate and store sentiment analysis results.
- Visualize results using charts and dashboards.
- Review historical analysis and export results where supported.
- Manage application data through Django's administrative interface.

## Installation and Setup

### Prerequisites

- Python 3.11
- Git
- Docker Engine
- Docker Compose
- An AWS EC2 Ubuntu instance for cloud deployment

### 1. Clone the Repository

```bash
git clone https://github.com/RimshaKanwal0/FinSentiments_FYP.git
cd FinSentiments_FYP
```

### 2. Configure Environment Variables

Create a `.env` file in the project root.

```env
DEBUG=0
SECRET_KEY=replace_with_a_secure_random_secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

NEWSAPI_KEY=replace_with_your_newsapi_key

POSTGRES_DB=fin_db
POSTGRES_USER=fin_user
POSTGRES_PASSWORD=replace_with_a_strong_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into your local `.env` file.

**Security recommendations:**

- Never commit `.env` files or API keys to GitHub.
- Add `.env` to `.gitignore`.
- Use strong, unique database credentials.
- Configure Django's `ALLOWED_HOSTS` for your actual deployment domain or IP.
- Restrict SSH access and database/network access through AWS security groups.
- Use HTTPS for a public-facing production deployment.

### 3. Build and Start the Containers

Ensure the repository contains a working Dockerfile and `docker-compose.yml`, then run:

```bash
docker compose build
docker compose up -d
```

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

### 4. Apply Database Migrations

```bash
docker compose exec web python manage.py migrate
```

Create an administrator account:

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Access the Application

Open the configured application URL in your browser.

For a local development setup, the URL may be:

```text
http://localhost:8000/
```

The actual URL depends on the port mapping and deployment configuration.

## AWS EC2 Deployment

The application can be deployed to an AWS EC2 Ubuntu instance using Docker and Docker Compose.

### Deployment workflow

1. Launch and configure an Ubuntu EC2 instance.
2. Install Docker Engine and the Docker Compose plugin.
3. Configure security groups to permit only the required inbound traffic.
4. Clone the repository or pull a trusted application image.
5. Configure environment variables securely on the server.
6. Build or pull the Docker image.
7. Start the application and database services.
8. Apply Django migrations and create an administrator account.
9. Configure a reverse proxy such as Nginx and enable HTTPS for public deployment.
10. Verify application health, database connectivity, and logs.

Example commands on the EC2 instance:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker

git clone https://github.com/RimshaKanwal0/FinSentiments_FYP.git
cd FinSentiments_FYP

# Create and securely configure the .env file first.
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```

The commands assume that Docker Compose configuration and environment variables have been prepared for the target server.

**Production considerations:**

- Do not expose PostgreSQL publicly.
- Avoid exposing the application port directly when using a reverse proxy.
- Keep application secrets out of source control.
- Configure persistent database and static-file storage.
- Monitor application logs, resource usage, and database health.
- Select EC2 resources appropriate for the memory and compute requirements of the selected ML models.

## Docker and Containerization

Docker provides a consistent runtime environment for the Django application and its dependencies.

Docker Compose coordinates the application and PostgreSQL services, simplifying local development and deployment.

Key benefits include:

- Consistent dependencies across environments.
- Reproducible application builds.
- Simplified service startup and configuration.
- Persistent database storage through Docker volumes.
- Easier deployment to cloud-hosted Linux instances.

## Results and Evaluation

Model performance should be reported using the actual evaluation results from the corresponding experiment.

Recommended metrics include:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

If reporting the 95% accuracy achieved in the separate RoBERTa experiment, specify the model, dataset, and test-set evaluation that produced the result. Do not generalize this figure to every classifier or to the entire web application.

## Learning Outcomes

Through this project, I gained hands-on experience in:

- Financial text classification using traditional ML and transformer-based approaches.
- NLP preprocessing, feature engineering, and model evaluation.
- Integrating trained models into a Django application.
- Building data-driven dashboards and sentiment trend visualizations.
- Managing persistent application data with PostgreSQL.
- Containerizing Python applications with Docker and Docker Compose.
- Deploying and configuring applications on AWS EC2.
- Understanding the engineering considerations involved in moving ML experiments into a usable application.

## Future Improvements

- Add automated model comparison and reproducible evaluation reports.
- Improve class-imbalance handling and test generalization across datasets.
- Add more robust model monitoring and inference logging.
- Optimize container images and resource usage for ML inference.
- Introduce automated tests and CI/CD workflows.
- Improve forecast evaluation using time-based validation and suitable error metrics.

## License

This project is released under the MIT License, subject to the license file included in the repository.

## Project Links

- **GitHub Repository:** https://github.com/RimshaKanwal0/FinSentiments_FYP
- **LinkedIn Project Deployment Post:** https://www.linkedin.com/feed/update/urn:li:activity:7368208997394350081/

---

**FinSentiments — From financial text and ML experimentation to an integrated, containerized AI application.**
