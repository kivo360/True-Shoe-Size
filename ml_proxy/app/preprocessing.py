import pandas as pd

def group_preprocessing(group: pd.DataFrame):
    make = str(group.make.iloc[0])
    brand = str(group.brand.iloc[0])
    year = int(group.year.iloc[0])

    mean = group.true_size.mean()
    std = group.true_size.std()

    return make, brand, year, mean, std