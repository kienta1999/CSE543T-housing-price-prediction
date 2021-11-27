from data import X_train_scaled, y_train, X_test_scaled, y_test
import numpy as np

from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import VotingRegressor
from sklearn.model_selection import cross_val_score

# print('-------------------------------------------------------')
# print('KNN Regressor')
# k_values = np.arange(1, 31)
# accuracies = np.zeros(k_values.shape[0])
# for i, k in enumerate(k_values):
#     knn = KNeighborsRegressor(n_neighbors=k)
#     scores = cross_val_score(knn, X_train_scaled, y_train, cv=10)
#     accuracies[i] = np.mean(scores)

# max_k = k_values[np.argmax(accuracies)]
# print(f"The best k for KNN Regressor is {max_k}")

print('-------------------------------------------------------')
print('Random Forest Regressor')
max_features = ['auto', 'sqrt', 'log2']
n_estimators = np.arange(10, 201, 10)
comb = [(x, y) for x in max_features for y in n_estimators]
accuracies = np.zeros(len(comb))
for i, c in enumerate(comb):
    max_feature, n_estimator = c
    rf = RandomForestRegressor(max_features=max_feature, n_estimators=n_estimator, random_state=11)
    scores = cross_val_score(rf, X_train_scaled, y_train, cv=10)
    accuracies[i] = np.mean(scores)
    print(c, accuracies[i])
best_comb = comb[np.argmax(accuracies)]
print(f"The best comb for Random Forest Regressor is {best_comb}")
# print(list(zip(accuracies, comb)))
