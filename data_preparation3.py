import pandas as pd
import numpy as np

source_raw = "data/housing_data_raw/0.csv"
housing_price = pd.read_csv(source_raw, encoding="cp1252", error_bad_lines=False)
# price filter
housing_price = housing_price[
    (housing_price["price"].notna()) & (housing_price["price"].str.startswith("$"))
]
housing_price["price"] = (
    housing_price["price"]
    .map(lambda x: x[1:])
    .map(lambda x: x if x[-1] != "+" else x[:-1])
)
housing_price.drop(columns=["lot_size.1", "parking_size"], inplace=True)
# bath, bed, and areas required
housing_price = housing_price[
    (housing_price["bath"] != "—")
    & (housing_price["beds"] != "—")
    & (housing_price["area"].str.isnumeric())
]
# Year column
mean_year = int(
    np.mean(
        housing_price[
            (housing_price["year_built"] != "—")
            & (housing_price["year_built"] != "None")
        ]["year_built"].astype(np.float)
    )
)
housing_price["year_built"] = (
    housing_price["year_built"]
    .map(lambda year: year if year != "—" and year != "None" else mean_year)
    .astype(np.int)
)
# Lot size
housing_price["lot_size"] = housing_price["lot_size"].map(
    lambda lot: lot if lot.isnumeric() else 0
)
# score
housing_price["transit_score"] = housing_price["transit_score"].map(
    lambda score: score if score != "None" else 0
)
housing_price["walk_score"] = housing_price["walk_score"].map(
    lambda score: score if score != "None" else 0
)
housing_price["bike_score"] = housing_price["bike_score"].map(
    lambda score: score if score != "None" else 0
)
# cooling & heating
housing_price["cooling"] = housing_price["cooling"].map(
    lambda x: len(x.split("|")) if x != "None" else 0
)
housing_price["heating"] = housing_price["heating"].map(
    lambda x: len(x.split("|")) if x != "None" else 0
)
# has_pool
housing_price["has_pool"] = housing_price["has_pool"].map(
    lambda score: 1 if score == "Yes" else 0
)

# append columns from other files

# export data
housing_price.to_csv("data/final_data.csv", index=False)
