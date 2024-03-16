import pandas as pd

mock_dict = [
    # {
    #     "Date": "2023-03-20",
    #     "title": "Hello world world!!",
    #     "year": 20155555,
        # "quantity": 12
    # },
    {
        "Date": "2023-03-20",
        "title": "Hello universe!",
        "year": 2025,
        "quantity": 12
    },
    {
        "Date": "2023-03-21",
        "title": "Hello earth!",
        "year": 2022,
        "quantity": 12
    },
    # {
    #     "Date": "2023-03-21",
    #     "title": "Hello Mars!",
    #     "year": 2022,
    #     "quantity": 12
    # },
    # {
    #     "Date": "2023-03-21",
    #     "title": "Hello Venus!",
    #     "year": 2022,
        # "quantity": 12
    # },
    # {
    #     "Date": "2023-03-22",
    #     "title": "Hello Jupyter!",
    #     "year": 2022,
        # "quantity": 12
    # },
    # {
    #     "Date": "2023-03-22",
    #     "title": "Hello Uranus!",
    #     "year": 2022,
        # "quantity": 12
    # },
]

MOCK_DF = pd.DataFrame(mock_dict)
# MOCK_DF.set_index(["Date", "title", "year"], inplace=True)
