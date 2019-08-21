import os
import time
import sys

import argparse
from loguru import logger
import numpy as np
from copy import copy

from funguauniverse import MemoizeAndOperate
from funguauniverse import start_service
from sklearn.linear_model import PassiveAggressiveRegressor

from sklearn.datasets import make_regression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.regression import max_error, mean_absolute_error, r2_score, mean_squared_log_error
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from dask.distributed import Client, as_completed
import pandas as pd

from crayons import blue

# client = Client(processes=False)

def ml_scoring(model, testX, testY):
    prediction = model.predict(testX)
    mxerr = max_error(testY, prediction)
    mabserr = mean_absolute_error(testY, prediction)
    r2d2 = r2_score(testY, prediction)
    # mlogerr = mean_squared_log_error(testY, prediction)

    return {
        "max_err": mxerr,
        "max_abs_err": mabserr,
        "r2": r2d2
        # "mlog": mlogerr
    }


class MemoryPassiveRegressor(MemoizeAndOperate):
    """ A class for online learning using the passive aggressive regressor """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 5581)
        self.backup_removal_interval = kwargs.get("backup_mins", 0.5) * 60
        self.deletion_mins = kwargs.get("deletion_mins", 50)
        self.file_name_hash = {}


    def initialize(self, query: dict, **kwargs):
        """ 
            The existing model should include the scalars because this isn't an immediate train and predict model
        """

        sample_model = {
            "model": PassiveAggressiveRegressor(
                warm_start=True,
                max_iter=100
            ),
            "make_scalar": preprocessing.LabelEncoder(),
            "year_scalar": preprocessing.StandardScaler(),
            "make_labels": []
        }

        existing_model = self.load(query)
        if existing_model is None:
            self.set_item(query, 
                sample_model, 
                overwrite=True
            )
        else:
            self.set_item(query, existing_model, overwrite=False)

    def check_and_load(self, query):
        q = copy(query)
        _hash = self.hash_dict(q)
        _keys = list(self.reg_dict.keys())
        if _hash not in _keys:
            self.initialize(query)

    def train_score_predict_long(self, query:dict, X, y, X_pred, **kwargs):
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
            regressor.fit(X_train, y_train)
            score = ml_scoring(regressor, X_test, y_test)
            regressor.fit(X, y)
            prediction = regressor.predict(X_pred)
            query_item["model"] = regressor
            self.set_item(query, query_item, overwrite=True)
            return {
                "score": score,
                "prediction": prediction
            }
        except Exception as e:
            logger.exception(e)
            return {

            }
    
    def preprocess_and_train(self, query:dict, frame: pd.DataFrame, **kwargs):
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            
            # make scalar
            make_scalar = None
            # year scalar
            years_scalar = None
            query_keys = query_item.keys()

            if "make_scalar" not in query_keys:
                logger.error("Make Scalar doesn't exist")
                return
            
            if "year_scalar" not in query_keys:
                logger.error("Year Scalar doesn't exist")
                return

            y_axis = frame.loc[:, 'trueSize'].to_numpy()
            frame = frame.drop(columns=['trueSize'])
            
            make_scalar = query_item["make_scalar"]
            years_scalar = query_item["year_scalar"]
            make_labels = query_item["make_labels"]
        

            year_shape = frame.year.to_numpy().reshape(-1, 1)
            
            for make in frame.make.values:
                if make not in make_labels:
                    make_labels.append(make)

            # Partial Fit
            make_scalar.fit(make_labels)
            years_scalar.partial_fit(year_shape)

            years = years_scalar.transform(year_shape)
            frame['make'] = make_scalar.transform(frame.make.values)
            frame['year'] = years[:, 0].tolist()
            
            query_item["model"] = regressor
            query_item["make_scalar"] = make_scalar
            query_item["year_scalar"] = years_scalar
            query_item["make_labels"] = make_labels

            x_axis = frame.to_numpy()
            regressor.partial_fit(x_axis, y_axis)
            # Testing and training job goes here
            # X_train, X_test, y_train, y_test = train_test_split(x_axis, y_axis, test_size=0.3)
            # regressor.fit(X_train, y_train)

            # Get the scoring information
            # score = ml_scoring(regressor, X_test, y_test)
            score = 0
            self.set_item(query, query_item, overwrite=True)
            return {
                "score": score,
                "is_trained": True,
            }
        except Exception as e:
            logger.exception(e)
            return {
                "score": 0,
                "is_trained": False
            }

    def train_score_predict(self, query:dict, X, y, X_pred, **kwargs):
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
            regressor.partial_fit(X_train, y_train)
            score = ml_scoring(regressor, X_test, y_test)
            regressor.partial_fit(X_test, y_test)
            prediction = regressor.predict(X_pred)
            query_item['model'] = regressor
            self.set_item(query, query_item, overwrite=True)
            return {
                "score": score,
                "prediction": prediction
            }
        except Exception as e:
            logger.exception(e)
            return {

            }

    def train(self, query: dict, X, y, **kwargs):
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            regressor.partial_fit(X, y)
            self.set_item(query, regressor, overwrite=True)
            return "DONE"
        except Exception as e:
            print(str(e))
            pass

    def predict(self, query: dict, X, **kwargs):
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            prediction = regressor.predict(X)
            return prediction
        except Exception as e:
            return []
    
    def predict_frame(self, query: dict, frame:pd.DataFrame, **kwargs):
        """ Online predict a set of variables via an online frame"""
        self.check_and_load(query)
        try:
            query_item = dict(self.get_item(query))
            regressor = query_item["model"]

            # make scalar
            make_scalar = None
            # shoe_size scalar
            shoesize_scalar = None
            # year scalar
            years_scalar = None
            query_keys = query_item.keys()

            if "make_scalar" not in query_keys:
                logger.error("Make Scalar doesn't exist")
                return {
                    "prediction": None,
                    "is_successful": False
                }
            
            if "year_scalar" not in query_keys:
                logger.error("Year Scalar doesn't exist")
                return {
                    "prediction": None,
                    "is_successful": False
                }

            # frame = frame.drop(columns=['brand'])
            make_scalar = query_item["make_scalar"]
            years_scalar = query_item["year_scalar"]
            make_labels = query_item["make_labels"]

            
            for make in frame.make.values:
                if make not in make_labels:
                    make_labels.append(make)
            

            year_shape = frame.year.to_numpy().reshape(-1, 1)
            
            make_scalar.fit(make_labels)
            years_scalar.partial_fit(year_shape)

            years = years_scalar.transform(year_shape)
            frame['make'] = make_scalar.transform(frame.make.values)
            frame['year'] = years[:, 0].tolist()


            query_item["model"] = regressor
            query_item["make_scalar"] = make_scalar
            query_item["year_scalar"] = years_scalar
            query_item["make_labels"] = make_labels

            x_axis = frame.to_numpy()
            
            prediction = regressor.predict(x_axis)
            return {
                "prediction": prediction,
                "is_successful": True
            }
        except Exception as e:
            return {
                "prediction": None,
                "is_successful": False
            }


    def predict_scalar(self, query: dict, make:str, year:int, **kwargs):
        self.check_and_load(query)
        try:
            query_item = dict(self.get_item(query))
            regressor = query_item["model"]

            # make scalar
            make_scalar = None
            # year scalar
            years_scalar = None
            query_keys = query_item.keys()

            if "make_scalar" not in query_keys:
                logger.info("Make scalar not found")
                return {
                    "prediction": None,
                    "is_successful": False,
                    "message": "Make scalar is missing"
                }
            
            if "year_scalar" not in query_keys:
                logger.info("Year scalar not found")
                return {
                    "prediction": None,
                    "is_successful": False,
                    "message": "Year scalar is missing"
                }
            

            make_scalar = query_item["make_scalar"]
            years_scalar = query_item["year_scalar"]
            make_labels = query_item["make_labels"]
            

            if make not in make_labels:
                make_labels.append(make)
            
            # make_arr = np.array([make])
            year_arr = np.array([year]).reshape(-1, 1)
            single_year_np = np.array([[year]])
            make_scalar.fit(make_labels)
            years_scalar.partial_fit(year_arr)

            m = make_scalar.transform([make])
            ye = years_scalar.transform(single_year_np)
    
            X = np.array([m[0], ye[0][0]]).reshape(1, -1)
            prediction = regressor.predict(X)
            
            
            query_item["model"] = regressor
            query_item["make_scalar"] = make_scalar
            query_item["year_scalar"] = years_scalar
            query_item["make_labels"] = make_labels
            
            return {
                'prediction': prediction[0],
                'message': "successfully predicted the trueSize",
                'is_successful': True
            }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return {
                "prediction": None,
                "is_successful": False,
                "message": str(e),
                "exception": {
                    "filename": fname, 
                    "line": exc_tb.tb_lineno
                }
            }


    def score(self, query, frame, **kwargs):
        # Generate the score for the model in X and Y
        # print(self.query_lookup_table)
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            
            # make scalar
            make_scalar = None
            # year scalar
            years_scalar = None
            query_keys = query_item.keys()

            if "make_scalar" not in query_keys:
                logger.error("Make Scalar doesn't exist")
                return {
                    "message": "Error ... scalar not found"
                }
            
            if "year_scalar" not in query_keys:
                logger.error("Year Scalar doesn't exist")
                return {
                    "message": "Error ... scalar not found"
                }

            y_axis = frame.loc[:, 'trueSize'].to_numpy()
            frame = frame.drop(columns=['trueSize'])
            
            make_scalar = query_item["make_scalar"]
            years_scalar = query_item["year_scalar"]
            make_labels = query_item["make_labels"]
        

            year_shape = frame.year.to_numpy().reshape(-1, 1)
            
            for make in frame.make.values:
                if make not in make_labels:
                    make_labels.append(make)

            # Partial Fit
            make_scalar.fit(make_labels)
            years_scalar.partial_fit(year_shape)

            years = years_scalar.transform(year_shape)
            frame['make'] = make_scalar.transform(frame.make.values)
            frame['year'] = years[:, 0].tolist()
            


            x_axis = frame.to_numpy()
            # Get the scoring information
            regressor.fit(x_axis, y_axis)
            score = ml_scoring(regressor, x_axis, y_axis)

            query_item["model"] = regressor
            query_item["make_scalar"] = make_scalar
            query_item["year_scalar"] = years_scalar
            query_item["make_labels"] = make_labels

            
            # score = 0
            self.set_item(query, query_item, overwrite=True)
            return {
                "score": score,
                "is_trained": True,
            }
        except Exception as e:
            print(str(e))
            return {
                "message": "You done goofed"
            }
        
    def set_c(self, query: dict, C, **kwargs):
        # Partially train the passive aggressive regressor
        # print(self.hash_dict)
        self.check_and_load(query)
        try:
            query_item = self.get_item(query)
            regressor = query_item["model"]
            regressor.C = C
            query_item["model"] = regressor
            self.set_item(query, query_item, overwrite=True)
            return "DONE"
        except Exception as e:
            print(str(e))

    def background_operation(self):
        reg_keys = list(self.reg_dict.keys())
        for rk in reg_keys:
            hash_query = self.query_by_hash(rk)
            self.save(hash_query, self.reg_dict[rk])
            current_timestamp = time.time()
            model_timestamp = self.timestamp_record.get(rk, None)
            if model_timestamp is None:
                logger.info("Skipping model deletion")
                continue
            logger.debug(blue("Checking to see if model should be deleted from memory"))
            s30_later = model_timestamp + self.backup_removal_interval # we check to see if the model is backup_removal_interval * 60 seconds to represent minutes.``
            if s30_later <= current_timestamp:
                # prune the model from memory
                del self.reg_dict[rk]
        now = time.time()

        # YOLO: We're gonna hard code this bitch. We'll softcore it 
        local_folder = "/tmp/checkpoint"
        for f in os.listdir(local_folder):
            if os.stat(os.path.join(local_folder,f)).st_mtime < now - (60*10):
                os.remove(os.path.join(local_folder, f))
            

    # TODO: Add prune example
    def save(self, query: dict, obj):
        q = copy(query)
        with self.space as space:
            space.store(obj, query=q, current_time=True)

    def load(self, query: dict):
        q = copy(query)
        try:
            with self.space as space:
                item = space.load(query=q)
                return item
        except Exception:
            return None
    def run(self):
        start_service(self, self.host, self.port)


if __name__ == "__main__":
    # Get the environment variables for the default variables
    mhost = os.getenv('MONGO_HOST', "localhost")
    current_port = os.getenv('CURRENT_PORT', 8400)
    parser = argparse.ArgumentParser()
    parser.add_argument("-hh", "--host", default="0.0.0.0", type=str, help="The host we intend to run on - Default: localhost")
    parser.add_argument("-p", "--port", default=current_port, type=int, help="The port we're intending to run on - Default: 5581")
    parser.add_argument("-mh", "--mongo_host", default=mhost, type=str, help="The default mongodb host intending to run on - Default: localhost ")
    parser.add_argument("-i", "--interval", default=2, type=int, help="The number of minutes between checking for changes")
    parser.add_argument("-mm", "--memorymin", default=2, type=int, help="the number of minutes that the model will remain in memory")
    parser.add_argument("-del", "--deletion", default=50, type=int, help="the number of minutes that the model will remain in memory")
    args = parser.parse_args()

    host = (args.host)
    port = (args.port)
    mongo_host = (args.mongo_host)
    minute_interval = (args.interval)
    backup_min = (args.memorymin)
    deletion_mins = (args.deletion)

    seconds_search = minute_interval*60

    MemoryPassiveRegressor(host=host, port=port, mongo_host=mongo_host, interval=seconds_search, backup_mins=backup_min, deletion_mins=deletion_mins).start()
    while True:
        time.sleep(5)
