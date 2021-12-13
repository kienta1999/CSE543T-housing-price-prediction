from sklearn.ensemble import VotingRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from data import X_train_scaled, y_train, X_test_scaled, y_test

# obtain hyperparameters from cross-validation and grid search results
knn = KNeighborsRegressor(n_neighbors=13)
rf = RandomForestRegressor(max_features='sqrt', n_estimators=480)
gb = GradientBoostingRegressor(n_estimators=100, max_features='auto')

er = VotingRegressor([('knn', knn), ('rf', rf), ('gb', gb)])
er.fit(X_train_scaled, y_train)
score = er.score(X_test_scaled, y_test)
print('Accuracy on test set', score)
# Accuracy on test set 0.5554419568633473