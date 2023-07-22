# Overview

This lab demonstrates running PaLM 2 powered Chatbot service on Cloud Run.

1. IAM Setup

Cloud Run service account (defaults to the default compute eninge service account) must have the following roles:

* AI Platform Admin
* BigQuery Data Editor
* BigQuery Job User
* BigQuery Read Session User
* Storage Admin
* Storage Object Admin
* Storage Object Creator
* Storage Object Viewer
* Vertex AI Administrator
* Vertex AI User

2. Install Requirements

```shell
pip3 install -r requirements
```

3. Running locally

```shell
export FLASK_SECRET_KEY=<YOUR SECRET KEY>
export GOOGLE_CLOUD_PROJECT=<YOUR GCP PROJECT ID>
export GOOGLE_CLOUD_REGIN=<REGION>
python3 app.py
```

4. Deploy to Cloud Run

```shell
export GOOGLE_CLOUD_PROJECT=<GOOGLE PROJECT ID>
export GOOGLE_CLOUD_REGIN=<us-central1...etc>
export FLASK_SECRET_KEY=<YOUR SECRET KEY>
export IMAGE=<IMAGE:TAG>

docker build . -t gcr.io/$GOOGLE_PROJECT_ID/$IMAGE
gcloud run deploy ${GOOGLE_CLOUD_PROJECT}-demo --max-instances=10 --memory=4Gi --cpu=2 \
    --set-env-vars=GOOGLE_CLOUD_PROJECT=$GOOGLE_PROJECT_ID \
    --set-env-vars=FLASK_SECRET_KEY=$FLASK_SECRET_KEY \
    --image=gcr.io/$GOOGLE_CLOUD_PROJECT/$IMAGE \
    --region=$GOOGLE_CLOUD_REGIN
```
