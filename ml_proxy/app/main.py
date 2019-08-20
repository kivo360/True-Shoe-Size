import datetime
import sys



import pandas as pd
from fastapi import FastAPI
from ml_proxy.app.models.machine import ModelData, PredictionModel
from ml_proxy.reg_client import MemoryRegressorClient

version = f"{sys.version_info.major}.{sys.version_info.minor}"

app = FastAPI()




client = MemoryRegressorClient(port=8400)
shoe_query = {
    "type": "shoes",
    "type_info": "basic"
}



@app.post("/train")
async def train_root(model_data: ModelData):
    """ Train the machine learning model on new data as it comes in."""
    
    train_frame = pd.DataFrame(model_data.dict()['train'])
    client.preprocess_and_train(shoe_query, train_frame)
    message = f"Hello world! From FastAPI running on Uvicorn with Gunicorn. Using Python {version}"
    return {"message": message, "data": model_data.train}

@app.post("/score/many")
def predict_root(model_data: ModelData):
    """
        Gets the score for many items
    """
    # For each model inside of the training set, do the same check and queries
    
    message = f"Hello world! From FastAPI running on Uvicorn with Gunicorn. Using Python {version}"
    return {"message": message, "data": model_data.pred}

@app.post("/score/single")
async def predict_root(prediction_model: PredictionModel):
    message = f"Get a true score. Using Python {version}"
    # Check to see if anything is inside of the database already
    # If not, make a prediction and label it as such
    
    return {"message": message}
