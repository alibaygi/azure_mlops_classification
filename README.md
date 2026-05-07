# Azure MLOps Classification

An end-to-end MLOps project on Azure Machine Learning (SDK v2) for binary classification on insurance data, using MLflow for experiment tracking and Managed Online Endpoints for deployment.

## Overview

This project trains a LightGBM model to predict insurance outcomes (binary classification, evaluated by AUC) and automates the full ML lifecycle — from training to deployment — using Azure ML SDK v2, MLflow, and Azure DevOps Pipelines.

## Project Structure

| Folder | Purpose |
|---|---|
| `training/` | Model training code (`train.py`, `train_aml.py`) and SDK v2 command job YAML |
| `deployment/` | Scoring script, managed online endpoint and deployment YAMLs |
| `environment_setup/` | ARM template and Azure Pipelines YAML for provisioning Azure ML resources |
| `tests/` | Integration tests for staging and production endpoints |
| `data/` | Insurance dataset (`insurance.csv`) |

## Tech Stack

- **Azure Machine Learning SDK v2** — command jobs, model registry, managed online endpoints
- **MLflow** — experiment tracking, metric logging, model logging and registration
- **LightGBM** — gradient boosting classifier
- **Azure DevOps Pipelines** — CI/CD and infrastructure provisioning via ARM templates

---

## Step-by-Step Setup

### Prerequisites

- Azure subscription with Contributor access
- Azure DevOps organisation
- Azure CLI installed: `az --version`
- Azure ML CLI v2 extension: `az extension add -n ml`

---

### Step 1 — Provision Azure ML Infrastructure

1. In Azure DevOps go to **Pipelines → Library → + Variable group**
2. Name it `mlops-insurance-classification` and add these variables:

   | Variable | Example value |
   |---|---|
   | `AZURE_RM_SVC_CONNECTION` | Name of your Azure service connection |
   | `RESOURCE_GROUP` | `rg-mlops-insurance` |
   | `LOCATION` | `eastus` |
   | `BASE_NAME` | `mlopsins` (max 10 chars) |
   | `WORKSPACE_NAME` | `mlops-insurance-ws` |

3. Go to **Pipelines → New pipeline** → connect to your repo → select **Existing Azure Pipelines YAML** → choose `environment_setup/iac-create-environment-pipeline-arm.yml`
4. Run the pipeline — it will create the resource group, Azure ML workspace, storage account, and key vault

---

### Step 2 — Upload the Dataset

```bash
az ml data create \
  --name insurance_dataset \
  --version 1 \
  --path data/insurance.csv \
  --type uri_folder \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

---

### Step 3 — Create a Compute Cluster for Training

```bash
az ml compute create \
  --name insurance-cluster \
  --type AmlCompute \
  --min-instances 0 \
  --max-instances 2 \
  --size Standard_DS3_v2 \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

---

### Step 4 — Run the Training Job

```bash
az ml job create \
  --file training/train_insurance.runconfig \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

This will:
- Run `train_aml.py` on the compute cluster
- Log parameters and AUC metric to MLflow
- Register the model as `insurance_model` in the Azure ML model registry

Monitor the run in **Azure ML Studio → Jobs**.

---

### Step 5 — Deploy the Managed Online Endpoint

**Create the endpoint:**
```bash
az ml online-endpoint create \
  --file deployment/inferenceConfig.yml \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

**Deploy to staging:**
```bash
az ml online-deployment create \
  --file deployment/aciDeploymentConfigStaging.yml \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME> \
  --all-traffic
```

**Deploy to production:**
```bash
az ml online-deployment create \
  --file deployment/aksDeploymentConfigProd.yml \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

**Route traffic (e.g. 10% canary to production):**
```bash
az ml online-endpoint update \
  --name insurance-endpoint \
  --traffic "staging=90 production=10" \
  --resource-group <RESOURCE_GROUP> \
  --workspace-name <WORKSPACE_NAME>
```

---

### Step 6 — Test the Endpoint

Get the endpoint URL and key:
```bash
az ml online-endpoint show --name insurance-endpoint \
  --resource-group <RESOURCE_GROUP> --workspace-name <WORKSPACE_NAME>

az ml online-endpoint get-credentials --name insurance-endpoint \
  --resource-group <RESOURCE_GROUP> --workspace-name <WORKSPACE_NAME>
```

Run integration tests:
```bash
pip install -r package_requirement/requirements.txt

pytest tests/integration/ \
  --scoreurl <ENDPOINT_URL>/score \
  --scorekey <ENDPOINT_KEY>
```

---

### Step 7 — Monitor & Retrain

- View metrics and runs in **Azure ML Studio → Jobs → Experiments**
- MLflow tracking is enabled automatically — compare runs, view AUC trends
- To retrain, re-run Step 4 with updated data or parameters in `training/parameters.json`
- New model versions are registered automatically in the model registry

