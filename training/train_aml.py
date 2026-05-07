import os
import argparse
import json
import mlflow
import mlflow.lightgbm
import pandas as pd
from train import split_data, train_model, get_model_metrics


def main():
    print("Running train_aml.py")

    parser = argparse.ArgumentParser("train")
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model",
        default="insurance_model",
    )

    parser.add_argument(
        "--data_path",
        type=str,
        help="Path to the input data folder (URI folder input)",
        default="./data",
    )

    args = parser.parse_args()

    print("Argument [model_name]: %s" % args.model_name)
    print("Argument [data_path]: %s" % args.data_path)

    mlflow.lightgbm.autolog(disable=True)

    with mlflow.start_run():
        print("Getting training parameters")

        with open("parameters.json") as f:
            pars = json.load(f)
        try:
            train_args = pars["training"]
        except KeyError:
            print("Could not load training values from file")
            train_args = {}

        print(f"Parameters: {train_args}")
        mlflow.log_params(train_args)

        # Load data from the mounted input path
        data_file = os.path.join(args.data_path, "insurance.csv")
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} rows from {data_file}")

        # Split, train, evaluate
        data = split_data(df)
        model = train_model(data, train_args)
        model_metrics = get_model_metrics(model, data)

        # Log model to MLflow and register it
        mlflow.lightgbm.log_model(
            model,
            artifact_path=args.model_name,
            registered_model_name=args.model_name,
        )

        print(f"Model '{args.model_name}' registered via MLflow.")
        print(f"Metrics: {model_metrics}")


if __name__ == '__main__':
    main()


    parser = argparse.ArgumentParser("train")
if __name__ == '__main__':
    main()
