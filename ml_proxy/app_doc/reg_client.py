import numpy as np
import pandas as pd
from funguauniverse.utils.web.serviceclient import ServiceClient
from sklearn import preprocessing
from pprint import pprint
from requests_futures.sessions import FuturesSession

class MemoryRegressorClient(ServiceClient):
    def initialize(self, query, **kwargs):
        # You should put the settings of the regressor into kwargs. This would be things like the length of memory
        # The memory should be short for non-stationary predictions
        res = self._send({
            "command": "initialize",
            "args": [query],
            "kwargs": kwargs
        })
        return res

    def train(self, query, X, y):
        trained_response = self._send({
            "command": "train",
            "args": [query, X, y],
            "kwargs": {}
        })
        return trained_response

    def preprocess_and_train(self, query, frame):
        trained_response = self._send({
            "command": "preprocess_and_train",
            "args": [query, frame],
            "kwargs": {}
        })
        return trained_response
    
    def score(self, query, frame):
        model_score = self._send({
            "command": "score",
            "args": [query, frame],
            "kwargs": {}
        })
        return model_score

    def predict(self, query, X):
        prediction = self._send({
            "command": "predict",
            "args": [query, X],
            "kwargs": {}
        })
        return prediction

    def predict_scalar(self, query, make, year):
        prediction = self._send({
            "command": "predict_scalar",
            "args": [query, make, year],
            "kwargs": {}
        })
        return prediction
    
    def train_score_predict(self, query:dict, X, y, X_pred, **kwargs):
        """ Train and score"""
        prediction = self._send({
            "command": "train_score_predict",
            "args": [query, X, y, X_pred],
            "kwargs": {}
        })
        return prediction

    def set_c(self, query, c):
        """ Sets the regularization rate to reduce"""
        self._send({
            "command": "set_c",
            "args": [query, c],
            "kwargs": {}
        })