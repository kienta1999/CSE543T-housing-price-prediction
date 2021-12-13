import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn import preprocessing

data = pd.read_csv('../data/final_data.csv')[[
    'beds', 'bath', 'area', 'year_built', 'lot_size', 'walk_score', \
    'transit_score', 'bike_score', 'cooling', 'heating', 'has_pool', \
    'crime_rate_per_100000', 'minimum_wage', 'college_completion', \
    'unemployment_rate', 'median_household_income', 'price' \
]]
X = data.drop('price', axis = 1)
y = data['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=41)

scaler = preprocessing.StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)