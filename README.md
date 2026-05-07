# Azure MLOps Classification

An end-to-end MLOps project on Azure Machine Learning for binary classification on insurance data.

## Overview

This project trains a LightGBM model to predict insurance outcomes (binary classification, evaluated by AUC) and automates the full ML lifecycle — from training to deployment — using Azure ML and Azure DevOps Pipelines.

## Project Structure

| Folder | Purpose |
|---|---|
| `training/` | Model training code (`train.py`, `train_aml.py`) and Azure ML run config |
| `deployment/` | Scoring script and deployment configs for ACI (staging) and AKS (production) |
| `environment_setup/` | ARM template and Azure Pipelines YAML for provisioning Azure ML resources |
| `tests/` | Integration tests for staging and production endpoints |
| `data/` | Insurance dataset (`insurance.csv`) |

## Tech Stack

- **Azure Machine Learning** — experiment tracking, dataset registration, model registry
- **LightGBM** — gradient boosting classifier
- **Azure Container Instances (ACI)** — staging deployment
- **Azure Kubernetes Service (AKS)** — production deployment
- **Azure DevOps Pipelines** — CI/CD and infrastructure provisioning via ARM templates

## Quick Start

1. Provision Azure resources using `environment_setup/iac-create-environment-pipeline-arm.yml`.
2. Configure the variable group `mlops-wsh-vg` in Azure DevOps with your subscription connection, resource group, and workspace name.
3. Run the training pipeline — `training/train_aml.py` registers the dataset and model in Azure ML.
4. Deploy the model to ACI (staging) or AKS (production) using configs in `deployment/`.
5. Run integration tests in `tests/integration/` to validate the deployed endpoints.
