# Azure MLOps Classification

An end-to-end MLOps project on Azure Machine Learning (SDK v2) for binary classification on insurance data, using MLflow for experiment tracking and Managed Online Endpoints for deployment.

## Overview

This project trains a LightGBM model to predict insurance outcomes (binary classification, evaluated by AUC) and automates the full ML lifecycle — from training to deployment — using Azure ML SDK v2, MLflow, and Azure DevOps Pipelines.

## Project Structure

| Folder | Purpose |
|---|---|
| `training/` | Model training code (`train.py`, `train_aml.py`) and SDK v2 command job YAML |
| `deployment/` | Scoring script, managed online endpoint and deployment YAMLs |
| `environment_setup/` | ARM template and three Azure Pipelines YAMLs (infra, training, deployment) |
| `tests/` | Integration tests for staging and production endpoints |
| `data/` | Insurance dataset (`insurance.csv`) |

## Tech Stack

- **Azure Machine Learning SDK v2** — command jobs, model registry, managed online endpoints
- **MLflow** — experiment tracking, metric logging, model logging and registration
- **LightGBM** — gradient boosting classifier
- **Azure DevOps Pipelines** — CI/CD and infrastructure provisioning via ARM templates

## CI/CD Pipelines

All steps are automated via three Azure DevOps pipelines in `environment_setup/`:

| Pipeline file | Purpose | Trigger |
|---|---|---|
| `iac-create-environment-pipeline-arm.yml` | Provision Azure ML workspace, storage, key vault | Manual |
| `ml-train-pipeline.yml` | Register dataset, create compute, submit training job, register model | Auto on push to `training/`, `data/`, or `parameters.json` |
| `ml-deploy-pipeline.yml` | Deploy staging endpoint, run integration tests, deploy production with canary traffic | Manual (after training) |

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

### Step 2 — Register All Three Pipelines in Azure DevOps

Repeat **New pipeline** for each remaining YAML file:

| Pipeline | File | Trigger |
|---|---|---|
| Training | `environment_setup/ml-train-pipeline.yml` | Auto on push to `training/`, `data/`, or `parameters.json` |
| Deployment | `environment_setup/ml-deploy-pipeline.yml` | Manual (after training succeeds) |

> Once registered, Steps 3–5 are handled **automatically** by these pipelines. They are listed below for reference only.

---

### Step 3 — Training (automated by `ml-train-pipeline.yml`)

Every push to `training/` or `data/` triggers the pipeline which:
1. Registers the dataset in Azure ML
2. Creates the compute cluster if it doesn't exist
3. Submits the training job and waits for completion
4. Verifies the model is registered in the model registry

To trigger manually, push any change or run the pipeline from Azure DevOps.

---

### Step 4 — Deployment (automated by `ml-deploy-pipeline.yml`)

Run this pipeline manually from Azure DevOps after a successful training run. It:
1. Creates the managed online endpoint (`insurance-endpoint`) if it doesn't exist
2. Deploys the latest model to **staging** and routes 100% traffic to it
3. Runs integration tests against the staging endpoint
4. On test pass, deploys to **production** with 10% canary traffic split

---

### Step 5 — Monitor & Retrain

- View metrics and MLflow runs in **Azure ML Studio → Jobs → Experiments**
- Compare AUC across runs, view parameters, download artifacts
- To retrain: update `training/parameters.json` or `data/insurance.csv` and push — the training pipeline triggers automatically
- New model versions are registered automatically in the model registry

