# -*- coding: utf-8 -*-
"""LinearRegression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BcdDqKJOsOU7QuO1UmkMxPFRocfQFNic

# **Flight Fare Prediction Linear Regression Project**
1. Load The Flight_Dataset
2. Perform Feature Exploration and Engineering
3. Feature Selection technique to select the most important features
4. Train a Linear Regression Model with hyper-parameter tuning
5. Save Model
6. Export Model

## Set up Environment
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
import seaborn as sns
sns.set()

"""## Load Flight_Dataset"""

# Load Flight_Dataset from Project folder
Flight_Dataset = pd.read_excel("Data_Train.xlsx")

# To stretch head function output to the notebook width
pd.set_option('display.max_columns', None)

Flight_Dataset.head()

Flight_Dataset.info()       # Print Data Types

"""### Check for missing values"""

Flight_Dataset.isnull().sum()

Flight_Dataset.dropna(inplace = True)

Flight_Dataset.isnull().sum()

"""## Feature Engineering"""

Flight_Dataset.head()

"""# **# Dealing with Object Data:**
# Convert the Object type into numeric features by employing the pandas to_datetime method to convert these object data types to datetime data type.

"""

# Date_of_Journey is the day when plane departs.
Flight_Dataset["journey_day"] = pd.to_datetime(Flight_Dataset.Date_of_Journey, format="%d/%m/%Y").dt.day
Flight_Dataset["journey_month"] = pd.to_datetime(Flight_Dataset["Date_of_Journey"], format = "%d/%m/%Y").dt.month
Flight_Dataset.head()

# Since we have converted Date_of_Journey column into integers, Now we can drop as it is of no use.
Flight_Dataset.drop(["Date_of_Journey"], axis = 1, inplace = True)

# Departure time is when a plane leaves the gate.
# Similar to Date_of_Journey we can extract values from Dep_Time
# Extracting Hours
Flight_Dataset["dep_hour"] = pd.to_datetime(Flight_Dataset["Dep_Time"]).dt.hour
# Extracting Minutes
Flight_Dataset["dep_min"] = pd.to_datetime(Flight_Dataset["Dep_Time"]).dt.minute
# Now we drop Dep_Time as it is of no use
Flight_Dataset.drop(["Dep_Time"], axis = 1, inplace = True)

# Arrival time is when the plane pulls up to the gate.
# Similar to Date_of_Journey we can extract values from Arrival_Time

# Extracting Hours
Flight_Dataset["arrival_hour"] = pd.to_datetime(Flight_Dataset["Arrival_Time"]).dt.hour
# Extracting Minutes
Flight_Dataset["arrival_min"] = pd.to_datetime(Flight_Dataset["Arrival_Time"]).dt.minute
# Now we can drop Arrival_Time as it is of no use
Flight_Dataset.drop(["Arrival_Time"], axis = 1, inplace = True)

Flight_Dataset.head()

# Duration is the time taken by plane to reach destination
# It is the difference betwen Arrival Time and Departure time
# Assigning and converting Duration column into list, for looping through
duration = list(Flight_Dataset["Duration"])
# In table above, Row Index=2, we have Duration = 19h (missing minutes)
# Looping through all duration values, to ensure it has both hours & mins: 'xh ym'
for i in range(len(duration)):
    if len(duration[i].split()) != 2:    # Check if duration contains only hour or mins
        if "h" in duration[i]:
            duration[i] = duration[i].strip() + " 0m"   # Adds 0 minute
        else:
            duration[i] = "0h " + duration[i]           # Adds 0 hour
# Prepare separate duration_hours and duration_mins lists
duration_hours = []
duration_mins = []
for i in range(len(duration)):
    duration_hours.append(int(duration[i].split(sep = "h")[0]))    # Extract hours from duration
    duration_mins.append(int(duration[i].split(sep = "m")[0].split()[-1]))   # Extracts only minutes from duration

# Add duration_hours and duration_mins list to our Flight_Dataset df
Flight_Dataset["Duration_hours"] = duration_hours
Flight_Dataset["Duration_mins"] = duration_mins
# Drop Duration column from the Flight_Dataset
Flight_Dataset.drop(["Duration"], axis = 1, inplace = True)

Flight_Dataset.head()

"""
# **Managing Categorical Data:**
### There are various methods to deal with categorical data, including:

### For nominal data, where the data has no inherent order, we use the OneHotEncoder to convert categorical values into binary vectors.
### For ordinal data, where the data has a specific order, we utilize the LabelEncoder to assign numeric labels to each category preserving the order."""

# Feature engineering on: Airline
Flight_Dataset["Airline"].value_counts()

# As Airline is Nominal Categorical data we will perform OneHotEncoding
Airline = Flight_Dataset[["Airline"]]
Current_Airline_List = Airline['Airline']
New_Airline_List = []

for carrier in Current_Airline_List:
  if carrier in ['Jet Airways', 'IndiGo', 'Air India', 'SpiceJet',
       'Multiple carriers', 'GoAir', 'Vistara', 'Air Asia']:
    New_Airline_List.append(carrier)
  else:
    New_Airline_List.append('Other')

Airline['Airline'] = pd.DataFrame(New_Airline_List)
Airline['Airline'].value_counts()

Airline = pd.get_dummies(Airline, drop_first= True)
Airline.head()

# Feature engineering on: Source
Flight_Dataset["Source"].value_counts()

# As Source is Nominal Categorical data we will perform OneHotEncoding
Source = Flight_Dataset[["Source"]]
Source = pd.get_dummies(Source, drop_first= True)
# drop_first= True means we drop the first column to prevent multicollinearity
Source.head()

# Feature engineering on: Destination
Flight_Dataset["Destination"].value_counts()

# Renaming destination 'New Delhi' to 'Delhi' - to match with Source
Destination = Flight_Dataset[["Destination"]]
Current_Destination_List = Destination['Destination']
New_Destination_List = []

for value in Current_Destination_List:
  if value in ['New Delhi']:
    New_Destination_List.append('Delhi')
  else:
    New_Destination_List.append(value)

Destination['Destination'] = pd.DataFrame(New_Destination_List)

# As Destination is Nominal Categorical data we will perform OneHotEncoding
Destination = pd.get_dummies(Destination, drop_first = True)
Destination.head()

# Additional_Info contains almost 80% no_info
# Route and Total_Stops are related to each other
Flight_Dataset.drop(["Route", "Additional_Info"], axis = 1, inplace = True)

# Feature engineering on: Total_Stops
Flight_Dataset["Total_Stops"].value_counts()

# As this is case of Ordinal Categorical type we perform LabelEncoder
# Here Values are assigned with corresponding keys
Flight_Dataset.replace({"non-stop": 0, "1 stop": 1, "2 stops": 2, "3 stops": 3, "4 stops": 4}, inplace = True)
Flight_Dataset.head()

# Concatenate dataframe --> train_data + Airline + Source + Destination
data_train = pd.concat([Flight_Dataset, Airline, Source, Destination], axis = 1) # axis = 1 signifies column
data_train.drop(["Airline", "Source", "Destination"], axis = 1, inplace = True)

data_train.head()

data_train.shape

"""## **Feature Selection**

The goal is to retain the most important features that contribute significantly to the target variable while discarding irrelevant or redundant ones.
"""

data_train.columns

X = data_train.loc[:, ['Total_Stops', 'journey_day', 'journey_month', 'dep_hour',
       'dep_min', 'arrival_hour', 'arrival_min', 'Duration_hours',
       'Duration_mins', 'Airline_Air India', 'Airline_GoAir', 'Airline_IndiGo',
       'Airline_Jet Airways', 'Airline_Multiple carriers', 'Airline_Other',
       'Airline_SpiceJet', 'Airline_Vistara', 'Source_Chennai', 'Source_Delhi',
       'Source_Kolkata', 'Source_Mumbai', 'Destination_Cochin',
       'Destination_Delhi', 'Destination_Hyderabad', 'Destination_Kolkata']]
y = data_train.iloc[:, 1]

print(X.shape, y.shape)

"""### feature_importance_
Features with higher importance scores are considered more significant.
"""

# Important feature using ExtraTreesRegressor
from sklearn.ensemble import ExtraTreesRegressor
selection = ExtraTreesRegressor()
selection.fit(X, y)

print(selection.feature_importances_)

#plot graph of feature importances for better visualization
plt.figure(figsize = (12,8))
feat_importances = pd.Series(selection.feature_importances_, index=X.columns)
feat_importances.nlargest(25).plot(kind='barh')
plt.show()

"""
## VIF - Multicollinearity
 A high VIF value indicates that the variable is highly collinear with other predictors, and its coefficient estimates may not be reliable."""

# Checking for Multicollinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor
def Calculate_VIF(z):
    # Calculating Variable Inflation Factor (VIF)
    vif = pd.DataFrame()
    vif["variables"] = z.columns
    vif["VIF"] = [variance_inflation_factor(z.values, i) for i in range(z.shape[1])]
    return(vif)

# Compute VIF on X
Calculate_VIF(X)

# Drop 'Source_Delhi'
X = data_train.loc[:, ['Total_Stops', 'journey_day', 'journey_month', 'dep_hour',
       'dep_min', 'arrival_hour', 'arrival_min', 'Duration_hours',
       'Duration_mins', 'Airline_Air India', 'Airline_GoAir', 'Airline_IndiGo',
       'Airline_Jet Airways', 'Airline_Multiple carriers', 'Airline_Other',
       'Airline_SpiceJet', 'Airline_Vistara', 'Source_Chennai',
       'Source_Kolkata', 'Source_Mumbai', 'Destination_Cochin',
       'Destination_Delhi', 'Destination_Hyderabad', 'Destination_Kolkata']]
X.head()

"""

## **Perform the LinearRegression Regressor:**


Divide the Flight_Dataset

Train the model.

Evaluate the model's performance.
"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

from sklearn.preprocessing import RobustScaler

# Create a scaler
scaler = RobustScaler()

# Scale the features
X_scaled = scaler.fit_transform(X_train)

# # Scale the data
# X_scaled = scaler.fit_transform(X_train)

lr = LinearRegression()
lr.fit(X_scaled, y_train)

X_scaled_test = scaler.fit_transform(X_test)

print('Model Performance on Training Set:', round(lr.score(X_scaled, y_train)*100,2))
print('Model Performance on Test Set:', round(lr.score(X_scaled_test, y_test)*100,2))

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV

# Create a linear regression model
clf = LinearRegression()

# Create a parameter grid for GridSearchCV
param_grid = {
    "copy_X": [True, False],
    "fit_intercept": [True, False],
    "n_jobs": [1, 2, 4],
    "positive": [True, False],
}

# Create a GridSearchCV object
grid_search = GridSearchCV(clf, param_grid, cv=5)

# Fit the GridSearchCV object to the data
grid_search.fit(X, y)

# Print the best parameters
print(grid_search.best_params_)

print('Model Performance on Training Set:', round(grid_search.score(X_train, y_train)*100,2))
print('Model Performance on Test Set:', round(grid_search.score(X_test, y_test)*100,2))

# Plot performance graph
y_pred = grid_search.predict(X_test)
plt.scatter(y_test, y_pred, alpha = 0.5)
plt.xlabel("y_test")
plt.ylabel("y_pred")
plt.show()

# Model Error Values
print('MAE:', metrics.mean_absolute_error(y_test, y_pred))
print('MSE:', metrics.mean_squared_error(y_test, y_pred))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
#RMSE = sqrt((PV-OV)^2/n)

# RMSE/(max(DV)-min(DV))
print('Normalized RMSE ', round(np.sqrt(metrics.mean_squared_error(y_test, y_pred))/(max(y_test)-min(y_test)),2))
print('Max Value: ', max(y), '\nMin Value: ', min(y))

"""### Save the model .pkl"""

import pickle
# open a file, where you ant to store the data
file = open('LinearRegression_For_Flight_Fare_Prediction.pkl', 'wb')
# dump information to that file
pickle.dump(grid_search, file)

"""# Prediction on Unseen data"""

import pickle
path = 'LinearRegression_For_Flight_Fare_Prediction.pkl'
model = open(path,'rb')
lr = pickle.load(model)

New_Flight_Dataset = pd.read_excel("./Test_set.xlsx")
New_Flight_Dataset.head()

# Perform feature engineering on object dt variables
# Feature Engineering on: 'Date_of_Journey'
New_Flight_Dataset["journey_day"] = pd.to_datetime(New_Flight_Dataset.Date_of_Journey, format="%d/%m/%Y").dt.day
New_Flight_Dataset["journey_month"] = pd.to_datetime(New_Flight_Dataset["Date_of_Journey"], format = "%d/%m/%Y").dt.month
New_Flight_Dataset.drop(["Date_of_Journey"], axis = 1, inplace = True)

# Feature Engineering on: 'Dep_Time'
New_Flight_Dataset["dep_hour"] = pd.to_datetime(New_Flight_Dataset["Dep_Time"]).dt.hour
New_Flight_Dataset["dep_min"] = pd.to_datetime(New_Flight_Dataset["Dep_Time"]).dt.minute
New_Flight_Dataset.drop(["Dep_Time"], axis = 1, inplace = True)

# Feature Engineering on: 'Arrival_Time'
New_Flight_Dataset["arrival_hour"] = pd.to_datetime(New_Flight_Dataset["Arrival_Time"]).dt.hour
New_Flight_Dataset["arrival_min"] = pd.to_datetime(New_Flight_Dataset["Arrival_Time"]).dt.minute
New_Flight_Dataset.drop(["Arrival_Time"], axis = 1, inplace = True)

# Feature Engineering on: 'Duration'
duration = list(New_Flight_Dataset["Duration"])
for i in range(len(duration)):
    if len(duration[i].split()) != 2:    # Check if duration contains only hour or mins
        if "h" in duration[i]:
            duration[i] = duration[i].strip() + " 0m"   # Adds 0 minute
        else:
            duration[i] = "0h " + duration[i]           # Adds 0 hour
duration_hours = []
duration_mins = []
for i in range(len(duration)):
    duration_hours.append(int(duration[i].split(sep = "h")[0]))    # Extract hours from duration
    duration_mins.append(int(duration[i].split(sep = "m")[0].split()[-1]))   # Extracts only minutes from duration
New_Flight_Dataset["Duration_hours"] = duration_hours
New_Flight_Dataset["Duration_mins"] = duration_mins
New_Flight_Dataset.drop(["Duration"], axis = 1, inplace = True)


# Perform feature engineering on Categorical dt variables
# Feature Engineering on: 'Airline'
Airline = New_Flight_Dataset[["Airline"]]
New_Airline_List = []
Current_Airline_List = Airline['Airline']
for carrier in Current_Airline_List:
  if carrier in ['IndiGo', 'Air India', 'Jet Airways', 'SpiceJet',
       'Multiple carriers', 'GoAir', 'Vistara', 'Air Asia']:
    New_Airline_List.append(carrier)
  else:
    New_Airline_List.append('Other')
Airline['Airline'] = pd.DataFrame(New_Airline_List)
Airline = pd.get_dummies(Airline, drop_first= True)

# Feature Engineering on: 'Source'
Source = New_Flight_Dataset[["Source"]]
Source = pd.get_dummies(Source, drop_first= True)
Source.head()

# Feature Engineering on: 'Destination'
Destination = New_Flight_Dataset[["Destination"]]
Current_Destination_List = Destination['Destination']
New_Destination_List = []
for value in Current_Destination_List:
  if value in ['New Delhi']:
    New_Destination_List.append('Delhi')
  else:
    New_Destination_List.append(value)
Destination['Destination'] = pd.DataFrame(New_Destination_List)
Destination['Destination'].value_counts()
Destination = pd.get_dummies(Destination, drop_first = True)
Destination.head()

# Feature Engineering on: 'Route', 'Additional_Info
New_Flight_Dataset.drop(["Route", "Additional_Info"], axis = 1, inplace = True)

# Feature Engineering on: 'Total_Stops'
New_Flight_Dataset.replace({"non-stop": 0, "1 stop": 1, "2 stops": 2, "3 stops": 3, "4 stops": 4}, inplace = True)

# Concatenate dataframe --> train_data + Airline + Source + Destination
data_test = pd.concat([New_Flight_Dataset, Airline, Source, Destination], axis = 1)
data_test.drop(["Airline", "Source", "Destination"], axis = 1, inplace = True)

# See how the test Flight_Dataset looks
data_test.head()

# Drop 'Source_Delhi'
X_test_new = data_test.loc[:, ['Total_Stops', 'journey_day', 'journey_month', 'dep_hour',
       'dep_min', 'arrival_hour', 'arrival_min', 'Duration_hours',
       'Duration_mins', 'Airline_Air India', 'Airline_GoAir', 'Airline_IndiGo',
       'Airline_Jet Airways', 'Airline_Multiple carriers', 'Airline_Other',
       'Airline_SpiceJet', 'Airline_Vistara', 'Source_Chennai',
       'Source_Kolkata', 'Source_Mumbai', 'Destination_Cochin',
       'Destination_Delhi', 'Destination_Hyderabad', 'Destination_Kolkata']]
y_test_new = data_test.iloc[:, 1]

y_pred = lr.predict(X_test_new)

print('R2 value: ', round(metrics.r2_score(y_test_new, y_pred),2))
print('Normalized RMSE: ', round(np.sqrt(metrics.mean_squared_error(y_test_new, y_pred))/(max(y_test_new)-min(y_test_new)),2))
print('Max Value: ', max(y_test_new), '\nMin Value: ', min(y_test_new))

# writing model output file
df_y_pred = pd.DataFrame(y_pred,columns= ['Predicted Price'])
original_Flight_Dataset = pd.read_excel("./Test_set.xlsx")
dfx = pd.concat([original_Flight_Dataset, df_y_pred], axis=1)
dfx.to_excel("LinearRegression.xlsx")
dfx.head()

