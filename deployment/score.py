import json
import numpy
import mlflow.lightgbm
import os
import time


def init():
    global model
    # AZUREML_MODEL_DIR is set automatically by Azure ML managed online endpoints
    model_dir = os.environ.get("AZUREML_MODEL_DIR", ".")
    model_path = os.path.join(model_dir, "insurance_model")
    model = mlflow.lightgbm.load_model(model_path)
    print("Model initialized at " + time.strftime("%H:%M:%S"))


def run(raw_data):
    data = json.loads(raw_data)["data"]
    data = numpy.array(data)
    result = model.predict(data)
    return {"result": result.tolist()}
