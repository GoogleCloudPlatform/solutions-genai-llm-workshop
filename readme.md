# Overview

This is part of the JAPAC Generative AI Technical Workshop qwiklabs. The workshop walk the audiences through:

* Google Generative AI Language offerings
* Langchain integration

## Environment Setup

1. Configure Google Cloud Environment

If you are running the lab in Qwiklabs environment, you do not have to manually configure the Google Project.

To manually configure the Google Cloud project:

2. Use Terraform to create and configure required resources.

```shell
cd terraform/qwiklabs

terraform init
terraform plan
terraform apply
```

This will create the following resources:
    1. A VPC with firewall rules which allows 80, 8080, 23 TCP inbound traffics.
    2. Service Network peering with the VPC.
    3. A GCE VM that runs in the VPC created previously.

3. ssh to the newly created GVE VM instance and clone the repository.
4. Switch to llm-workshop folder and open `1-setup-vm.sh`
5. Update the following line, replace the project id with your own project id.
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
