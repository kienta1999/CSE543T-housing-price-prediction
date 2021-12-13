from data import X_train_scaled, y_train, X_test_scaled, y_test

from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV

print('-------------------------------------------------------')
print('KNN Regressor')
parameters = {'n_neighbors': range(1, 50)}
knn = KNeighborsRegressor()
clf = GridSearchCV(knn, parameters)
clf.fit(X_train_scaled, y_train)
print('CV Result')
print(clf.cv_results_)
print('Best Parameter')
print(clf.best_params_)

print()
print()
print('-------------------------------------------------------')
print('Random Forest Regressor')
parameters = {'max_features': ['auto', 'sqrt', 'log2'], 'random_state': [4], 'n_estimators': range(10, 500, 10)}
rf = RandomForestRegressor()
clf = GridSearchCV(rf, parameters)
clf.fit(X_train_scaled, y_train)
print('CV Result')
print(clf.cv_results_)
print('Best Parameter')
print(clf.best_params_)

print()
print()
print('-------------------------------------------------------')
print('Gradient Boosting Regressor')
parameters = {'max_features': ['auto', 'sqrt', 'log2'], 'random_state': [1], 'n_estimators': range(10, 500, 10)}
gb = GradientBoostingRegressor()
clf = GridSearchCV(gb, parameters)
clf.fit(X_train_scaled, y_train)
print('CV Result')
print(clf.cv_results_)
print('Best Parameter')
print(clf.best_params_)