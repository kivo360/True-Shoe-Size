"""
    All machine learning specific basemodels
"""

from pydantic import BaseModel
from typing import List

class PredictionModel(BaseModel):
    make: str
    year: int

class TrainingModel(BaseModel):
    make: str
    year: int
    trueSize: float

class TrainingModelOrg(BaseModel):
    maker: str
    year: int
    trueSize: float


class ModelData(BaseModel):
    pred: List[PredictionModel] = []
    train: List[TrainingModel] = []



class NewFakeData(BaseModel):
    pred: List[PredictionModel] = []
    train: List[TrainingModelOrg] = []