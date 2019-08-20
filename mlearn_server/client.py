import itertools
import random
import time
import uuid
from statistics import mean

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


def linear_transformation(m, b, x):
    y = m*x + b
    return y


class GetPoly(object):
    def __init__(self, x=[0,1,2,3,4], y=[0,1,2,3,4], deg=2):
        fit = np.polyfit(x, y, deg)
        self.fit = np.poly1d(fit)

    def get_y(self, inp)->np.array:
        return self.fit(inp)

def create_year_true(year_frame:pd.DataFrame, year:int):
    df_row = year_frame[year_frame.year == year]
    mu = float(df_row["year_mu"])
    sigma = float(df_row["year_sigma"])
    return random.normalvariate(mu, sigma)

def create_make_true(make_frame:pd.DataFrame, make:str):
    df_row = make_frame[make_frame.make == make]
    mu = float(df_row["make_mu"])
    sigma = float(df_row["make_sigma"])
    return random.normalvariate(mu, sigma)

def average(seq: list):
    return sum(seq)/len(seq)


def pct_of_total(value:float, total:float):
    return value/total

def get_total_count(count_dict:dict):
    total = 0.0
    count_keys = count_dict.keys()
    for key in count_keys:
        total += count_dict[key]
    return total

def pct_total_by_number(value_dict:dict):
    value_keys = value_dict.keys()
    value_pcts = {}
    for value in value_keys:
        element_dict = value_dict[value]
        element_total = get_total_count(element_dict)
        current_pct = {}
        for element in element_dict.keys():
            if element_total == 0.0:
                if value < 2.0:
                    current_pct[1] = 1
                    current_pct[2] = 0
                    current_pct[3] = 0
                    current_pct[4] = 0
                    current_pct[5] = 0
                elif value > 4:
                    current_pct[1] = 0
                    current_pct[2] = 0
                    current_pct[3] = 0
                    current_pct[4] = 0
                    current_pct[5] = 1
                else:
                    current_pct[element] = 1/5
            else:
                current_pct[element] = (element_dict[element]/element_total)
        value_pcts[value] = list(current_pct.values())
    return value_pcts


def create_request_call(make, 
                        year, 
                        dist_by_make, 
                        dist_by_year, 
                        brand_list=[f"brand{x}" for x in range(40)]):
    """ For the front-end API """
    make_probability_list = dist_by_make[make]
    year_probability_list = dist_by_year[year]
    make_choice = np.random.choice([1, 2, 3, 4, 5], p=make_probability_list)
    year_choice = np.random.choice([1, 2, 3, 4, 5], p=year_probability_list)
    avg = np.array([make_choice, year_choice]).mean()
    brand = random.choice(brand_list)
    round_size = [x for x in range(7, 15)]
    
    rval = {
        "maker": make,
        "year": year,
        "brand": brand,
        "shoeSize": random.choice(round_size),
        "shoeFit": round((avg+0.5)),
        "isafter": random.choice([True, False])
    }
    return rval


# def create_request_call(make, 
#                         year, 
#                         dist_by_make, 
#                         dist_by_year, 
#                         brand_list=[f"brand{x}" for x in range(40)]):
#     """ For the front-end API """
#     make_probability_list = dist_by_make[make]
#     year_probability_list = dist_by_year[year]
#     make_choice = np.random.choice([1, 2, 3, 4, 5], p=make_probability_list)
#     year_choice = np.random.choice([1, 2, 3, 4, 5], p=year_probability_list)
#     avg = np.array([make_choice, year_choice]).mean()
#     brand = random.choice(brand_list)
#     round_size = [x * 0.5 for x in range(0, 30)]
    
#     rval = {
#         "maker": str(make),
#         "year": int(year),
#         "brand": str(brand),
#         "shoeSize": float(random.choice(round_size)),
#         "shoeFit": float(avg),
#         "isafter": bool(random.choice([True, False]))
#     }
#     return rval

if __name__ == "__main__":
    
    client = MemoryRegressorClient(port=8400)
    minimax = preprocessing.MinMaxScaler(feature_range=(-2, 2))    
    std_minmax = preprocessing.MinMaxScaler(feature_range=(0, 0.7))

    one_point_to_five_scalar = preprocessing.MinMaxScaler(feature_range=((2.2+random.uniform(-0.5, 0.5)), (4+random.uniform(-0.1, 0.6))))

    makes = ["adidas", "nike", "new_balance", "asics", "kering", "skechers", "fila", "bata", "burberry", "vf_corporation"]
    
    polynomial = GetPoly(
        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
        y=[6, 4, 2, 2, 4, 5, 4, 4, 3, 0, 0, 0, 0, 0, -1, -2, -1, -2, 0, -1], 
        deg=2
    )

    std_poly = GetPoly(
        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
        y=[1, 1, 2, 2, 2, 3, 2, 1, -1, 0, 0, 0, 1, 2, 2, 3, 2, 1, 0, 0], 
        deg=2
    )

    makes_len = len(makes)
    make_range = np.arange(makes_len)

    make_uniform = np.random.uniform(size=(makes_len,))

    make_polynomial = GetPoly(
        x=make_range,
        y=((make_uniform*make_uniform) + make_uniform), 
        deg=2
    )

    make_std_poly = GetPoly(
        x=make_range, 
        y=(((make_uniform*make_uniform) + make_uniform) * (make_uniform*random.uniform(-2, 2) + random.uniform(0, 3))), 
        deg=2
    )
    
    y = polynomial.get_y(np.arange(-3, 63)).reshape(-1, 1)
    std_y = std_poly.get_y(np.arange(-3, 63)).reshape(-1, 1)
    
    makes_data = ((make_polynomial.get_y(np.arange(-2, makes_len+3))[1:makes_len+1]) * 3).reshape(-1, 1)
    scaled_make = one_point_to_five_scalar.fit_transform(makes_data)[:, 0].tolist()
    # let's shuffle it
    shuffled = random.sample(scaled_make, len(scaled_make))
    
    transformed = minimax.fit_transform(y)[:, 0]
    transformed_std = std_minmax.fit_transform(std_y)[:, 0]
    
    true_score_std_by_year = transformed_std[2:62]
    true_score_by_year = (transformed[2:62]) + 3
    
    true_mu_std = {}

    fake_year_frame = pd.DataFrame({
        "year": [],
        "year_mu":[],
        "year_sigma": [],        
    })

    fake_make_frame = pd.DataFrame({
        "make": [],
        "make_mu": [],
        "make_sigma": [],
    })
    true_score_by_year = random.sample(true_score_by_year.tolist(), len(true_score_by_year)) 
    for index, value in enumerate(true_score_by_year):
        mu = true_score_by_year[index]
        sigma = true_score_std_by_year[index]
        
        year = (1960+index)

        fake_year_frame = fake_year_frame.append({
            "year": int(year),
            "year_mu": mu,
            "year_sigma": sigma
        }, ignore_index=True)
        # true_mu_std[year] = {
        #     "mu": mu,
        #     "sigma": sigma
        # }
    

    for index, item in enumerate(shuffled):
        fake_make_frame = fake_make_frame.append({
            "make": makes[index],
            "make_mu": item,
            "make_sigma": 0.1 + random.normalvariate(0.1, 0.05)
        }, ignore_index=True)

    # true_size_table = pd.DataFrame({
        #     "make": [],
        #     "year": [],
        #     "true_size": []
        # })
    

    decimal_numbers = np.linspace(1, 5, num=70)

    rounded = [round(x, 1) for x in decimal_numbers]
    dedup = list(set(rounded))
    
    
    numbers = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]

    dval = {}
    
    for number in dedup:
        avg = number
        result = [seq for i in range(len(numbers), 0, -1) for seq in itertools.combinations(numbers, i) if average(list(seq)) == avg]
        combination_count = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0
        }
        for combination in result:
            for ind in combination:
                combination_count[ind] = combination_count[ind] + 1
        print(combination_count)
        dval[avg] = combination_count
    

    pct_by_total = pct_total_by_number(dval)
    dist_by_make = {}
    dist_by_year = {}
    # Create a new dictionary about the probable 
    for index, row in fake_make_frame.iterrows():
        rounded_mu = round(row.make_mu, 1)
        dist_by_make[row.make] = pct_by_total[rounded_mu]
    
    for index, row in fake_year_frame.iterrows():
        rounded_mu = round(row.year_mu, 1)
        dist_by_year[row.year] = pct_by_total[rounded_mu]
    print("\n\n")
    pprint(dist_by_make)
    pprint(dist_by_year)
    print("\n\n")

    creation_calls = []
    # Create shoes
    brand_list=[f"brand{x}" for x in range(40)]
    for make in makes:
        for year in np.arange(1960, 2019):
            for brand in brand_list:
                creation_call = {
                    "maker": str(make),
                    "brand": str(brand),
                    "year": int(year)
                }
                creation_calls.append(creation_call)
    

    # Create a bunch of shoes
    
    num_of_iters = 2800
    sizecalls = []
    for index in range(num_of_iters):
        
        for make in makes:
            for _ in range(random.randint(2, 5)):
                user_id = random.randint(1, 12000)
                year = random.randint(1960, 2019)
                
                call_dict = create_request_call(make, year, dist_by_make, dist_by_year)
                call_dict["userid"] = user_id
                sizecalls.append(call_dict)
    
    
    host = "localhost"
    port = 3001
    
    address = f"http://{host}:{port}"
    session = FuturesSession()
    
    # Creating shoes
    # for creation in creation_calls:
    #     call = session.post(f"{address}/true/add", json=creation)
    #     print(call.result().json())

    

    for creation in sizecalls:
        call = session.post(f"{address}/true/addsize", json=creation)
        if random.uniform(0, 1) < 0.01:
            call_score = session.get(f"{address}/true/score")
            print(call_score.result().json())
            time.sleep(0.05)
        if random.uniform(0, 1) < 0.02:
            user_id = random.randint(1, 12000)
            year = random.randint(1960, 2019)
            make = random.choice(makes)
            call_val = create_request_call(make, year, dist_by_make, dist_by_year)
            call_val["brand"] = "brand{}".format(random.randint(40, 1000))

            call_predict = session.post(f"{address}/true/single", json=call_val)
            print(call_predict.result().json())
            time.sleep(5)
        print(call.result().json())


    
    

    # Create a master table to return results
    
    # We're going to create a fake data table
    # print(true_mu_std)

    
    # print(true_noise)
    # start = time.time()
    # for i in range(10):
    #     base_fake_model = query_obj = {
    #         "type": "fakemodel",
    #         "coin": "BTC_USD",
    #         "eid": uuid.uuid4().hex
    #     }
    
    #     X, y = make_regression(n_features=4, n_samples=100000, random_state=1)
    #     splitsX = np.split(X, 10)
    #     splitsy = np.split(y, 10)
    #     client.initialize(base_fake_model)
    
    #     for _ in range(len(splitsX)):
    #         _X = splitsX[_]
    #         _y = splitsy[_]
    #         X_train, X_test, y_train, y_test = train_test_split(
    #             _X, _y, test_size=0.1, random_state=0)
    #         pred = client.train_score_predict(base_fake_model, X_train, y_train, X_test)
    #         print(pred)
    

    # print(time.time() - start)
