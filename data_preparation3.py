import pandas as pd
import numpy as np
from us_state_to_abbrev import us_state_to_abbrev

index = 2
source_raw = f"data/housing_data_raw/{index}.csv"
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
        ]["year_built"].astype(float)
    )
)
housing_price["year_built"] = (
    housing_price["year_built"]
    .map(lambda year: year if year != "—" and year != "None" else mean_year)
    .astype(int)
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
# extract state and zip
housing_price["state"] = housing_price["state_and_zip"].map(
    lambda x: x.split(" ")[1] if len(x.split(" ")) == 3 else None
)
housing_price["zip"] = housing_price["state_and_zip"].map(
    lambda x: x.split(" ")[2] if len(x.split(" ")) == 3 else None
)

# drop house with no county
housing_price.dropna(inplace=True)
housing_price = housing_price[housing_price["county"] != "None"]

# reset index
housing_price = housing_price.reset_index(drop=True)

# append columns from other files

# Crime rate
def get_crime_rate(county, state):
    county_name = county + ", " + state
    crime_rate_entry = crime_rate[
        crime_rate["county_name"].str.lower() == county_name.lower()
    ]
    return (
        crime_rate_entry.iloc[0]["crime_rate_per_100000"]
        if crime_rate_entry.shape[0]
        else None
    )


crime_rate = pd.read_csv("data/crime_data_w_population_and_crime_rate.csv")[
    ["county_name", "crime_rate_per_100000"]
]
house_crime_rate = []
for i in range(housing_price.shape[0]):
    house = housing_price.iloc[i]
    house_crime_rate.append(get_crime_rate(house["county"], house["state"]))
housing_price["crime_rate_per_100000"] = house_crime_rate

# Minimum wage
minimum_wage_data = pd.read_csv("./data/minimum_wage_data.csv", encoding="cp1252")
minimum_wage_data = minimum_wage_data[minimum_wage_data["Year"] == 2020][
    ["Year", "State", "State.Minimum.Wage"]
]
minimum_wage_data["State"] = minimum_wage_data["State"].map(
    lambda s: us_state_to_abbrev[s]
)


def get_minimum_wage(state):
    minimum_wage_entry = minimum_wage_data[minimum_wage_data["State"] == state]
    return (
        minimum_wage_entry.iloc[0]["State.Minimum.Wage"]
        if minimum_wage_entry.shape[0]
        else 7.25
    )


housing_price["minimum_wage"] = housing_price["state"].map(get_minimum_wage)

# education - college completion rate
education_completing_college_data = pd.read_excel(
    "data/education_completing_college.xlsx"
)
education_completing_college_data = education_completing_college_data[
    ["Name", "2015-2019"]
]


def get_education(county, state):
    if len(county.split(" ")) < 1:
        return None
    county = " ".join(county.split(" ")[:-1])
    county_name = county + ", " + state
    education_completing_college_entry = education_completing_college_data[
        education_completing_college_data["Name"].str.lower() == county_name.lower()
    ]
    return (
        education_completing_college_entry.iloc[0]["2015-2019"]
        if education_completing_college_entry.shape[0]
        else None
    )


college_completion = []
for i in range(housing_price.shape[0]):
    house = housing_price.iloc[i]
    college_completion.append(get_education(house["county"], house["state"]))
housing_price["college_completion"] = college_completion

# unemployment rate and median household income
unemployment_rate_data = pd.read_excel("data/unemployment_rate.xlsx")[
    ["Name", 2020, "Median Household Income (2019)"]
]


def get_unemployment_rate(county, state):
    if county == "San Francisco County":
        county = "San Francisco County/city"
    county_name = county + ", " + state
    unemployment_rate_entry = unemployment_rate_data[
        unemployment_rate_data["Name"].str.lower() == county_name.lower()
    ]
    return (
        unemployment_rate_entry.iloc[0][2020]
        if unemployment_rate_entry.shape[0]
        else None,
        unemployment_rate_entry.iloc[0]["Median Household Income (2019)"]
        if unemployment_rate_entry.shape[0]
        else None,
    )


unemployment_rate = []
median_household_income = []
for i in range(housing_price.shape[0]):
    house = housing_price.iloc[i]
    u, m = get_unemployment_rate(house["county"], house["state"])
    unemployment_rate.append(u)
    median_household_income.append(m)
housing_price["unemployment_rate"] = unemployment_rate
housing_price["median_household_income"] = median_household_income

# export data
housing_price.dropna(inplace=True)
housing_price = housing_price[
    [
        "href",
        "stress_address",
        "city",
        "state",
        "zip",
        "county",
        "img_href",
        "beds",
        "bath",
        "area",
        "year_built",
        "lot_size",
        "walk_score",
        "transit_score",
        "bike_score",
        "cooling",
        "heating",
        "has_pool",
        "crime_rate_per_100000",
        "minimum_wage",
        "college_completion",
        "unemployment_rate",
        "median_household_income",
        "price",
    ]
]
housing_price.to_csv("data/final_data{index}.csv", index=False)
