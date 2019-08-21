import datetime
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from fastapi import FastAPI
from app.models.machine import ModelData, PredictionModel, NewFakeData
from app.reg_client import MemoryRegressorClient

version = f"{sys.version_info.major}.{sys.version_info.minor}"

app = FastAPI()


session_num = '07fb416ec39411e9abdf80c5f21e8205'

client = MemoryRegressorClient(port=8400)
shoe_query = {
    "type": "shoes",
    "type_info": "basic",
    "session": session_num
}



@app.post("/train")
async def train_root(model_data: ModelData):
    """ Train the machine learning model on new data as it comes in."""
    
    train_frame = pd.DataFrame(model_data.dict()['train'])
    res = client.preprocess_and_train(shoe_query, train_frame)
    # print(res)
    message = f"Hello world! From FastAPI running on Uvicorn with Gunicorn. Using Python {version}"
    return {"message": message, "data": model_data.train}

@app.post("/pred")
async def predict_root(prediction_model: PredictionModel):
    """ Predict the trueSize for a single app """

    message = f"Get a true score. Using Python {version}"
    
    res = client.predict_scalar(shoe_query, prediction_model.make, prediction_model.year)
    print(res)
    return {"message": message, "data": res}


@app.post("/score")
async def score_root(model_data: NewFakeData):
    """ 
        # Get Score
        ---
        Gets the score of the machine learning application. 
        We get it by adding in many variables into a dataframe, we can get the score by figuring the difference between a train test split. 
        Except we're not training.
    """

    score_frame = pd.DataFrame(model_data.dict()['train'])
    score_frame['make'] = score_frame.maker
    score_frame = score_frame.drop(columns=['maker'])
    print(score_frame)
    res = client.score(shoe_query, score_frame)
    print(res)
    message = f"Get a true score. Using Python {version}"
    
    return {"message": message, "data": res}