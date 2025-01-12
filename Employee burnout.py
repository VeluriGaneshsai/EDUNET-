import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
data_set = pd.read_csv("employee_burnout_analysis-AI.csv")  
# Print the shape of the dataset
print(f"Dataset shape: {data_set.shape}")

# Define the features and target variable
features = [
    'Date of Joining', 'Gender', 'Company Type', 'WFH Setup Available',
    'Designation', 'Resource Allocation', 'Mental Fatigue Score'
]
target = 'Burn Rate'

# Drop rows where the target variable is NaN
data_set = data_set.dropna(subset=[target])

# Print the shape of the dataset after dropping NaN values
print(f"Dataset shape after dropping NaNs in target: {data_set.shape}")

# Define the features and target variable again after dropping NaNs
X = data_set[features].copy()
y = data_set[target]

# Preprocess the data
# Convert 'Date of Joining' to a numeric feature representing the number of days since joining
X['Date of Joining'] = pd.to_datetime(X['Date of Joining'], dayfirst=True)
X['Days Since Joining'] = (pd.Timestamp.now() - X['Date of Joining']).dt.days
X = X.drop('Date of Joining', axis=1)

numeric_features = ['Days Since Joining', 'Resource Allocation', 'Mental Fatigue Score']
categorical_features = ['Gender', 'Company Type', 'WFH Setup Available', 'Designation']

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Create a pipeline that includes preprocessing and the regressor
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions on the training and test sets
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Predict burnout rates for the entire dataset
data_set['Predicted Burn Rate'] = model.predict(X)

print(f'Mean Squared Error (Test): {mean_squared_error(y_test, y_test_pred)}')
print(f'R^2 Score (Test): {r2_score(y_test, y_test_pred)}')
print(f'Mean Squared Error (Train): {mean_squared_error(y_train, y_train_pred)}')
print(f'R^2 Score (Train): {r2_score(y_train, y_train_pred)}')

# Plot actual vs predicted burnout rates for the test set
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_test_pred, alpha=0.5, label='Test')
plt.scatter(y_train, y_train_pred, alpha=0.5, label='Train')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs Predicted Burnout Rates')
plt.legend()
plt.show()

# Distribution of residuals for the test set
residuals_test = y_test - y_test_pred
residuals_train = y_train - y_train_pred
plt.figure(figsize=(10, 6))
sns.histplot(residuals_test, kde=True, color='red', label='Test Residuals', stat='density')
sns.histplot(residuals_train, kde=True, color='blue', label='Train Residuals', stat='density')
plt.xlabel('Residuals')
plt.title('Distribution of Residuals')
plt.legend()
plt.show()
