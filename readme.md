# Overview

This is part of the JAPAC Generative AI Technical Workshop qwiklabs. The workshop walk the audiences through:

* Google Generative AI Language offerings
* Langchain integration

## Provision Cloud Resources

1. Configure Google Cloud Environment

    If you are running the lab in Qwiklabs environment, you can skip step 2.

To manually configure the Google Cloud project:

2. Use Terraform to create and configure required resources.

- Goto `terraform/qwiklabs` folder.

    ```shell
    cd terraform/qwiklabs
    ```

- create `terraform.tfvars` file with the following content

    ```ini
    gcp_project_id = <YOUR GCP PROJECT ID>
    gcp_region = <DEFAULT GCP PROJECT ID> 
    gcp_zone = <DEFAULT GCP PROJECT ID> 
    ```

- Apply terraform to privision Google Cloud Resources.

    ```shell
    terraform init
    terraform plan -var-file=terraform.tfvars
    terraform apply -var-file=terraform.tfvars
    ```

    This will create the following resources:
        1. A VPC with firewall rules which allows 80, 8080, 23 TCP inbound traffics.
        2. Service Network peering with the VPC.

At this point, you have provisioned required cloud resources.

## Create Vertex AI Workbench as the lab environment.

In this lab, we use Vertex AI Workbench as the lab environment.

1. Follow the [instruction](https://cloud.google.com/vertex-ai/docs/workbench/instances/create-console-quickstart) to provision Vertex AI Workbench Instance.

2. Once the Workbench instance is created. Open the notebook and 

```shell
export GOOGLE_PROJECT_ID=<YOUR PROJECT ID>
```
6. Install required packages.
```shell
cd llm-workshop
sudo apt install -y python3.11-distutils
sudo apt-get update -y
sudo apt install -y python3-virtualenv
virtualenv --python=/usr/bin/python3.11 .venv
source ./.venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

pip install --require-hashes -r requirements.txt

```
7. Sets the GOOGLE_CLOUD_PROJECT environment variable.
```shell
export GOOGLE_CLOUD_PROJECT=$(gcloud config get project)
export GOOGLE_CLOUD_REGIN=<REGION>
```

8. Run `0-setup-matching-engine.py`, this will create the Vertex Matching Engine which can take 40-60 minutes.

9. Create BigQuery Dataset and copy data from the public dataset.
```shell
bash ./1-create-and-copy-bq-data.py
```
