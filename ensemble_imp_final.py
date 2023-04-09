# -*- coding: utf-8 -*-
"""ML_TH_DA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14t1TW7fyHeraeEiZ5nzvQGB3PgxPXgY5
"""

#sample code to get streaming data:
import requests
import pandas as pd

# Define the streaming API endpoint URL
url = "http://your-api-url-here"

# Initialize an empty list to store the streaming data
data_list = []

# Make a GET request to the API endpoint and stream the data
response = requests.get(url, stream=True)

# Iterate over the streaming data and append each data point to the data_list
for line in response.iter_lines():
    if line:
        # Decode the JSON-encoded data and append it to the data_list
        data_list.append(json.loads(line.decode('utf-8')))

# Convert the data_list into a Pandas DataFrame
df = pd.DataFrame(data_list)

import time
import warnings
from math import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import neighbors
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (MinMaxScaler)
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore")
start = time.time()
# load datasets for two subjects, Math and Portuguese
mat = pd.read_csv("/content/student-mat.csv", sep=';')
por = pd.read_csv("/content/student-por.csv", sep=';')
end = time.time()
print("\nTime to load data:", end - start, "seconds")
print()
# preprocess the data
start = time.time()

mat['subject'] = 'Maths'
por['subject'] = 'Portuguese'
df = pd.concat([mat, por])

# Set the random seed for reproducibility
np.random.seed(123)

# 1. Shuffle the dataset
df = df.sample(frac=1).reset_index(drop=True)


# 2. Removing duplicated rows and missing values
duplicated_rows = df.duplicated()


# Print the number of duplicated rows
print(f"Number of duplicated rows: {duplicated_rows.sum()}")

# Drop the duplicated rows
df = df.drop_duplicates()

# 3. Drop the missing values
df.dropna(inplace=True)
# Print the number of remaining rows
print(f"Number of remaining rows: {len(df)}")

# rename features to be more understandable
df.columns = ['school', 'sex', 'age', 'address', 'family_size', 'parents_status', 'mother_education', 'father_education',
              'mother_job', 'father_job', 'reason', 'guardian', 'commute_time', 'study_time', 'failures', 'school_support',
              'family_support', 'paid_classes', 'activities', 'nursery', 'desire_higher_edu', 'internet', 'romantic', 'family_quality',
              'free_time', 'go_out', 'weekday_alcohol_usage', 'weekend_alcohol_usage', 'health', 'absences', 'p1_score', 'p2_score', 'final_score', 'subject']

# Feature Engineering
# final_grade = weighted sum of p1, p2, final score
df["final_grade"] = (0.15*df["p1_score"]) + (0.20*df["p2_score"]) + (0.65*df["final_score"])

# Student Group: 1,2,3,4 based on their final grade
# df['Student_Group'] = 0  # dhmiourgia neas sthlhs me times 'na'
# df.loc[(df.final_grade >= 0) & (df.final_grade < 10), 'Student_Group'] = 4
# df.loc[(df.final_grade >= 10) & (df.final_grade < 14), 'Student_Group'] = 3
# df.loc[(df.final_grade >= 14) & (df.final_grade < 17), 'Student_Group'] = 2
# df.loc[(df.final_grade >= 17) & (df.final_grade <= 20), 'Student_Group'] = 1
df['Student_Group'] = pd.cut(df.final_grade, bins=[-1, 10, 14, 17, 20], labels=[4, 3, 2, 1])


# 4.Normalization of continuous variables

cont_cols = ['age', 'mother_education', 'father_education', 'commute_time', 'study_time', 'failures', 'family_quality', 'free_time', 'go_out','weekday_alcohol_usage', 'weekend_alcohol_usage', 'health', 'absences', 'p1_score', 'p2_score', 'final_score', 'Student_Group']
# for col in cont_cols:
#    df[col] = (df[col]-min(df[col]))/(max(df[col])-min(df[col]))

# normalize continuous variables
df[cont_cols] = MinMaxScaler().fit_transform(df[cont_cols])

# 5. 'One Hot Encoding'

ohe_cols = ['school', 'sex', 'address', 'family_size', 'parents_status', 'mother_job', 'father_job','reason', 'guardian', 'school_support', 'family_support','paid_classes', 'activities', 'nursery','desire_higher_edu', 'internet', 'romantic', 'subject']

df = pd.get_dummies(df, columns=ohe_cols, drop_first=True)

# 6.remove  'Outliers'
print("Shape before removing outliers: ", df.shape)


def remove_outliers(df):
    for col in df.columns:
        if df[col].dtype != 'object':
            # Check the skewness of the column
            skewness = df[col].skew()
            if abs(skewness) > 1:
                # Use z-score method for outlier detection
                threshold = 3
                z_scores = (df[col] - df[col].mean()) / df[col].std()
                df.loc[abs(z_scores) > threshold, col] = np.nan
            else:
                # Use Tukey's method for outlier detection
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                df.loc[(df[col] < lower_bound) | (
                    df[col] > upper_bound), col] = np.nan

    # Drop rows with missing values
    df.dropna(inplace=True)

    return df


df = remove_outliers(df)

print("Shape after removing outliers: ", df.shape)
print()

# 7. Feature Selection

print("Shape before feature selection: ", df.shape)


def select_features(df, num_features):
    X = df.drop('final_grade', axis=1)
    y = df['final_grade']

    # instantiate SelectKBest with f_regression as the score function
    selector = SelectKBest(f_regression, k=num_features)

    # fit selector to data
    selector.fit(X, y)

    # create a boolean mask to select the columns that were selected by the selector
    mask = selector.get_support()

    # get the column names for the selected columns
    selected_columns = X.columns[mask]

    # return a dataframe with the selected columns and the target column
    return df[selected_columns.append(pd.Index(['final_grade']))]


df = select_features(df, 23)

print("Shape after feature selection: ", df.shape)
print()

# 8. Search "lean corralated" features:

# Compute the correlation matrix
corr_matrix = df.corr().abs()

# Iterate over all the columns to find pairs with a correlation coefficient above the threshold
cols_to_drop = set()
for i in range(len(corr_matrix.columns)):
    for j in range(i):
        if corr_matrix.iloc[i, j] > 0.90:
            colname_i = corr_matrix.columns[i]
            colname_j = corr_matrix.columns[j]
            cols_to_drop.add(colname_i)
            cols_to_drop.add(colname_j)

# Convert the set of columns to drop to a list
cols_to_drop = list(cols_to_drop)
print("\nColumns with 'high correlation' (> 92%): \n", cols_to_drop)
print()

# Storing the target variable before dropping
y = df['final_grade']

# Dropping highly correlated variables
df.drop(cols_to_drop, axis=1, inplace=True)
df.drop(['Student_Group'], axis=1, inplace=True)
print(df.shape)
# print(df.columns)

end = time.time()
print("\nTime to preprocess data:", end - start, "seconds")
print()
###############################################################################


# Modelling the data using Semi-Supervised Learning

x_train, x_test, y_train, y_test = train_test_split(
    df, y, test_size=0.65, random_state=42)

Lx = x_train
Ly = y_train
Ux = x_test
Uy = y_test
T = 0.1
MaxIter = 15
m = [T * len(Lx)]
m = [round(m) for m in m]
print("m: ", m[0])

model_1 = neighbors.KNeighborsRegressor(
    n_neighbors=2, metric='minkowski', weights='distance')
model_2 = neighbors.KNeighborsRegressor(
    n_neighbors=3, metric='minkowski', weights='distance')
model_3 = neighbors.KNeighborsRegressor(
    n_neighbors=4, metric='minkowski', weights='distance')

h1 = model_1.fit(Lx, Ly)
h2 = model_2.fit(Lx, Ly)
h3 = model_3.fit(Lx, Ly)

h1_y = h1.predict(Ux)
h2_y = h2.predict(Ux)
h3_y = h3.predict(Ux)

print("\nL shape before learning: \n", Lx.shape, Ly.shape)
print("\nU shape before learning: \n", Ux.shape, Uy.shape)

# Orizoume to synolo S
Sx = pd.DataFrame(columns=Lx.columns)
dropped_rows = []

for j in range(MaxIter):
    # the table with the various estimates of the 3 models for each element of O
    Dx = np.random.uniform(low=0.0, high=1.0, size=(len(Ux)))
    for i in range(len(Ux)):
        Dx[i] = max(h1_y[i], h2_y[i], h3_y[i]) - min(h1_y[i], h2_y[i], h3_y[i])

    # argpartition: short up to a specific value in an array
    # with the meaning that up to that value all the previous ones are smaller than that

    # idx: here the values ​​of the seats of the Dx are stored
    # which correspond to the records with the smallest various
    idx = np.argpartition(Dx, m[0])
    # print("idx ews m: \n", idx[0:m[0]])

    # the m most "certain" records of the set O are stored
    for k in range(0, m[0]):
        Sx.loc[k] = Ux.iloc[idx[k]]
        dropped_rows.append(idx[k])

    # Each algorithm predicts the values ​​of the most "true" records
    S1y = h1.predict(Sx)
    S2y = h2.predict(Sx)
    S3y = h3.predict(Sx)

    S_y = np.random.uniform(low=0.0, high=1.0, size=m[0])
    for l in range(m[0]):
        S_y[l] = (S1y[l]+S2y[l]+S3y[l])/3

    # The set Re is subtracted from Ux
    print("\nUx shape before Sx removal: \n", Ux.shape)

    Ux_new = pd.concat([Ux, Sx])
    Ux_new = Ux_new.drop_duplicates(keep=False)
    Ux = Ux_new
    print("\nUx shape after S removal: \n", Ux.shape)

    print("\nUy shape before Sy removal: \n", Uy.shape)
    # create boolean mask indicating which rows were dropped
    mask = np.zeros(Uy.shape[0], dtype=bool)
    mask[dropped_rows] = True
    # drop corresponding rows from Uy
    Uy = Uy[~mask]
    print("\nUy shape after Sy removal: \n", Uy.shape)
    dropped_rows = []
    # The set Λ is expanded by the addition of Σ
    S_y = pd.DataFrame(S_y)

    print("\nL shape before S addition: \n", Lx.shape, Ly.shape)
    Lx = pd.concat([Lx, Sx])
    Ly = pd.concat([Ly, S_y])
    print("\nL shape after S addition: \n", Lx.shape, Ly.shape)
    print()
    # The algorithms are retrained on the new expanded L
    h1 = model_1.fit(Lx, Ly)
    h2 = model_2.fit(Lx, Ly)
    h3 = model_3.fit(Lx, Ly)

    h1_y = h1.predict(Ux)
    h2_y = h2.predict(Ux)
    h3_y = h3.predict(Ux)

print("Final L shape after learning: \n", Lx.shape, Ly.shape)
print("Final U shape after learning: \n", Ux.shape, Uy.shape)

print()

# After Semi-Supervised Learning -we use RYRegressor in the expanded
# set Λ in order to increase the complexity and at the same time the
# system power

# Split the data into training and test sets
Lx_train, Lx_test, Ly_train, Ly_test = train_test_split(
    Lx, Ly, test_size=0.20, random_state=42)  # stratify na dw


# Split the training data into training and validation sets
Lx_train, Lx_val, Ly_train, Ly_val = train_test_split(
    Lx_train, Ly_train, test_size=0.15, random_state=42)

# Print the sizes of the resulting sets
print("Training set size:", len(Lx_train), len(Ly_train))
print("Testing set size:", len(Lx_test), len(Ly_test))
print("Validation set size:", len(Lx_val), len(Ly_val))
print()

# Define the parameter grid to search
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Defining the model
# RFR = RandomForestRegressor(random_state=42, max_depth=10,
#                            min_samples_leaf=2, min_samples_split=2, n_estimators=200)
RFR = RandomForestRegressor(random_state=42)
# Fitting the model to the training set
RFR.fit(Lx_train, Ly_train)

# Predicts and compares the validation set with the actual values
Ly_val_pred = RFR.predict(Lx_val)
print("MAE from SSR in validation data: ",
      mean_absolute_error(Ly_val, Ly_val_pred))
print("MSE from SSR in validation data: ",
      mean_squared_error(Ly_val, Ly_val_pred))
print("R2 Score from SSR in validation data: ", r2_score(Ly_val, Ly_val_pred))
print()
# Predicts the remaining labels from U and compares the with actual values
Uy_pred = RFR.predict(Ux)
mse = mean_squared_error(Uy, Uy_pred)

n = len(Uy)
y_mean = np.mean(y_test)
variance = sum((Uy_pred - y_mean) ** 2) / (n - 1)
std = sqrt(variance)
print("Variance from SSR in U: ", variance)
print("std from U: ", std)
print("MAE from SSR in U: ", mean_absolute_error(Uy, Uy_pred))
print("MSE from SSR in U: ", mse)
print("RMSE from SSR in U: ", np.sqrt(mse))
print("R2 Score from SSR in U: ", r2_score(Uy, Uy_pred))
print()

# correcting its dimensions for good printing
Uy = Uy.to_numpy()
Uy_pred = Uy_pred.reshape(len(Uy_pred), 1)
Uy = np.squeeze(Uy)
Uy.shape
Uy_pred = np.squeeze(Uy_pred)

fdf = pd.DataFrame({'Actual': Uy, 'Predicted': Uy_pred})
print(fdf)

plt.scatter(Uy, Uy_pred)
plt.plot([0, 20], [0, 20], 'r--')  # plot the y = x line in red dashed line
plt.xlabel('Actual Grades')
plt.ylabel('Predicted Grades')
plt.title('Actual Grades vs. Predicted Grades')

plt.show()

###############################################################################
# """
# Linear Regression
lr_model = LinearRegression()
lr_model.fit(Lx_train, Ly_train)
y_pred_lr = lr_model.predict(Ux)
print("MAE from LR in U: ", mean_absolute_error(Uy, y_pred_lr))
print("MSE from LR in U: ", mean_squared_error(Uy, y_pred_lr))
print("R2 Score from LR in U: ", r2_score(Uy, y_pred_lr))
print()
###############################################################################

# Decision Tree Regression
dt_model = DecisionTreeRegressor()
dt_model.fit(Lx_train, Ly_train)
y_pred_dt = dt_model.predict(Ux)
print("MAE from DT in U: ", mean_absolute_error(Uy, y_pred_dt))
print("MSE from DT in U: ", mean_squared_error(Uy, y_pred_dt))
print("R2 Score from DT in U: ", r2_score(Uy, y_pred_dt))
print()
###############################################################################
# Feature Ranking
feature_list = list(df.columns)
feature_imp = pd.Series(RFR.feature_importances_,
                        index=feature_list).sort_values(ascending=False)
print(feature_imp)
# """

import time
import warnings
from math import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import (MinMaxScaler)
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore")
start = time.time()
# load datasets for two subjects, Math and Portuguese

mat = pd.read_csv("/content/student-mat.csv", sep=';')
por = pd.read_csv("/content/student-por.csv", sep=';')
end = time.time()
print("\nTime to load data:", end - start, "seconds")
print()
# preprocess the data
start = time.time()

mat['subject'] = 'Maths'
por['subject'] = 'Portuguese'
df = pd.concat([mat, por])

# Set the random seed for reproducibility
np.random.seed(123)

# 1. Shuffle the dataset
df = df.sample(frac=1).reset_index(drop=True)


# 2. Removing duplicated rows and missing values
duplicated_rows = df.duplicated()


# Print the number of duplicated rows
print(f"Number of duplicated rows: {duplicated_rows.sum()}")

# Drop the duplicated rows
df = df.drop_duplicates()

# 3. Drop the missing values
df.dropna(inplace=True)
# Print the number of remaining rows
print(f"Number of remaining rows: {len(df)}")

# we are renaming the attributes to make them easier to understand
df.columns = ['school', 'sex', 'age', 'address', 'family_size', 'parents_status', 'mother_education', 'father_education','mother_job', 'father_job', 'reason', 'guardian', 'commute_time', 'study_time', 'failures', 'school_support','family_support', 'paid_classes', 'activities', 'nursery', 'desire_higher_edu', 'internet', 'romantic', 'family_quality','free_time', 'go_out', 'weekday_alcohol_usage', 'weekend_alcohol_usage', 'health', 'absences', 'p1_score', 'p2_score', 'final_score', 'subject']

# Feature Engineering
# final_grade = weighted sum of p1, p2, final score
df["final_grade"] = (0.15*df["p1_score"]) + (0.20*df["p2_score"]) + (0.65*df["final_score"])

# Student Group: 1,2,3,4 me vash ton teliko vathmo tous
# df['Student_Group'] = 0  # dhmiourgia neas sthlhs me times 'na'
# df.loc[(df.final_grade >= 0) & (df.final_grade < 10), 'Student_Group'] = 4
# df.loc[(df.final_grade >= 10) & (df.final_grade < 14), 'Student_Group'] = 3
# df.loc[(df.final_grade >= 14) & (df.final_grade < 17), 'Student_Group'] = 2
# df.loc[(df.final_grade >= 17) & (df.final_grade <= 20), 'Student_Group'] = 1
df['Student_Group'] = pd.cut(df.final_grade, bins=[-1, 10, 14, 17, 20], labels=[4, 3, 2, 1])


# 4.Normalization of continuous variables
cont_cols = ['age', 'mother_education', 'father_education', 'commute_time', 'study_time', 'failures', 'family_quality', 'free_time', 'go_out','weekday_alcohol_usage', 'weekend_alcohol_usage', 'health', 'absences', 'p1_score', 'p2_score', 'final_score', 'Student_Group']
# for col in cont_cols:
#    df[col] = (df[col]-min(df[col]))/(max(df[col])-min(df[col]))

# normalize continuous variables
df[cont_cols] = MinMaxScaler().fit_transform(df[cont_cols])

# 5. 'One Hot Encoding' of accidental variables
ohe_cols = ['school', 'sex', 'address', 'family_size', 'parents_status', 'mother_job', 'father_job','reason', 'guardian', 'school_support', 'family_support','paid_classes', 'activities', 'nursery','desire_higher_edu', 'internet', 'romantic', 'subject']

df = pd.get_dummies(df, columns=ohe_cols, drop_first=True)

# 6. removal of  'Outliers'
print("Shape before removing outliers: ", df.shape)


def remove_outliers(df):
    for col in df.columns:
        if df[col].dtype != 'object':
            # Check the skewness of the column
            skewness = df[col].skew()
            if abs(skewness) > 1:
                # Use z-score method for outlier detection
                threshold = 3
                z_scores = (df[col] - df[col].mean()) / df[col].std()
                df.loc[abs(z_scores) > threshold, col] = np.nan
            else:
                # Use Tukey's method for outlier detection
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                df.loc[(df[col] < lower_bound) | (
                    df[col] > upper_bound), col] = np.nan

    # Drop rows with missing values
    df.dropna(inplace=True)

    return df


df = remove_outliers(df)

print("Shape after removing outliers: ", df.shape)
print()

# 7. Feature Selection

print("Shape before feature selection: ", df.shape)


def select_features(df, num_features):
    X = df.drop('final_grade', axis=1)
    y = df['final_grade']

    # instantiate SelectKBest with f_regression as the score function
    selector = SelectKBest(f_regression, k=num_features)

    # fit selector to data
    selector.fit(X, y)

    # create a boolean mask to select the columns that were selected by the selector
    mask = selector.get_support()

    # get the column names for the selected columns
    selected_columns = X.columns[mask]

    # return a dataframe with the selected columns and the target column
    return df[selected_columns.append(pd.Index(['final_grade']))]


df = select_features(df, 23)

print("Shape after feature selection: ", df.shape)
print()

# 8. Anazhthsh "highly corrrelated" xarakthristikwn:

# Compute the correlation matrix
corr_matrix = df.corr().abs()

# Iterate over all the columns to find pairs with a correlation coefficient above the threshold
cols_to_drop = set()
for i in range(len(corr_matrix.columns)):
    for j in range(i):
        if corr_matrix.iloc[i, j] > 0.90:
            colname_i = corr_matrix.columns[i]
            colname_j = corr_matrix.columns[j]
            cols_to_drop.add(colname_i)
            cols_to_drop.add(colname_j)

# Convert the set of columns to drop to a list
cols_to_drop = list(cols_to_drop)
print("\nColumns with 'high correlation' (> 92%): \n", cols_to_drop)
print()

# Storing the target variable before dropping
y = df['final_grade']

# Dropping highly correlated variables
df.drop(cols_to_drop, axis=1, inplace=True)
df.drop(['Student_Group'], axis=1, inplace=True)
print(df.shape)
# print(df.columns)

end = time.time()
print("\nTime to preprocess data:", end - start, "seconds")
print()
###############################################################################
# FF Neural Network for modelling
start = time.time()

x_train, x_test, y_train, y_test = train_test_split(
    df, y, test_size=0.3, random_state=20)


# Define the model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(14, activation='relu',
                          input_shape=(x_train.shape[1],)),
    tf.keras.layers.Dense(1, activation='linear')
])

# Compile the model
optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.0025)

model.compile(optimizer=optimizer, loss='mean_squared_error')

# Train the model
history = model.fit(x_train, y_train, validation_data=(
    x_test, y_test), batch_size=9, epochs=50)

end = time.time()

print("\nTime to model data using NN:", end - start, "seconds")
print()
# plot the training and validation loss at each epoch
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, 'y', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()


# predict on test data
predictions = model.predict(x_test)
# diorthwnontas tis diastaseis gia kalh ektiposi
y_test = y_test.to_numpy()
# y_pred = y_pred.reshape(len(y_pred), 1)
y_test = np.squeeze(y_test)
# y_test.shape
predictions = np.squeeze(predictions)
# y_pred.shape

fdf = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
print(fdf)


mse_nn = mean_squared_error(y_test, predictions)
n = len(y_test)
y_mean = np.mean(y_test)
variance = sum((predictions - y_mean) ** 2) / (n - 1)
std = sqrt(variance)
print("Variance of the NN model:", variance)
print("Std of the NN model:", std)
print("MAE from NN: ", mean_absolute_error(y_test, predictions))
print("MSE from NN: ", mse_nn)
print("RMSE from NN: ", np.sqrt(mse_nn))
print("R2 Score from NN: ", r2_score(y_test, predictions))
print()

# Assuming y_test and predictions are numpy arrays
plt.scatter(y_test, predictions)
plt.plot([0, 20], [0, 20], 'r--')  # plot the y = x line in red dashed line
plt.xlabel('Actual Grades')
plt.ylabel('Predicted Grades')
plt.title('Actual Grades vs. Predicted Grades')
r2list=[]
plt.show()

###############################################################################

# Linear Regression
start = time.time()

lr_model = LinearRegression()
lr_model.fit(x_train, y_train)
y_pred_lr = lr_model.predict(x_test)

end = time.time()
print("Time to model data using LR:", end - start, "seconds")
print()
mae_lr = mean_absolute_error(y_test, y_pred_lr)
mse_lr = mean_squared_error(y_test, y_pred_lr)
variance_lr = sum((y_pred_lr - y_mean) ** 2) / (n - 1)
std_lr = sqrt(variance_lr)
print("Variance of the LR model:", variance_lr)
print("Std of the LR model:", std_lr)
print("MAE from LR: ", mae_lr)
print("MSE from LR: ", mse_lr)
print("RMSE from LR: ", np.sqrt(mse_lr))
print("R2 Score from LR: ", r2_score(y_test, y_pred_lr))
r2list.append(r2_score(y_test, y_pred_lr))
print()

###############################################################################

# Decision Tree Regression
dt_model = DecisionTreeRegressor()
dt_model.fit(x_train, y_train)
y_pred_dt = dt_model.predict(x_test)
mae_dt = mean_absolute_error(y_test, y_pred_dt)
mse_dt = mean_squared_error(y_test, y_pred_dt)
variance_dt = sum((y_pred_dt - y_mean) ** 2) / (n - 1)
std_dt = sqrt(variance_dt)
print("Variance of DT model: ", variance_dt)
print("Std deviation of DT model: ", std_dt)
print("MAE from DT: ", mae_dt)
print("MSE from DT: ", mse_dt)
print("RMSE from DT: ", np.sqrt(mse_dt))
print("R2 Score from DT: ", r2_score(y_test, y_pred_dt))
r2list.append(r2_score(y_test, y_pred_dt))
print()

###############################################################################

# Random Forest Regression
rf_model = RandomForestRegressor(n_estimators=20)
rf_model.fit(x_train, y_train)
y_pred_rf = rf_model.predict(x_test)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
mse_rf = mean_squared_error(y_test, y_pred_rf)
variance_rf = sum((y_pred_rf - y_mean) ** 2) / (n - 1)
std_rf = sqrt(variance_rf)
print("Variance of RF model: ", variance_rf)
print("Std deviation of RF model: ", std_rf)
print("MAE from RF: ", mae_rf)
print("MSE from RF: ", mse_rf)
print("RMSE from RF: ", np.sqrt(mse_rf))
print("R2 Score from RF: ", r2_score(y_test, y_pred_rf))
r2list.append(r2_score(y_test, y_pred_rf))
print()

###############################################################################

# Support Vector Machine Regression

svm_model = SVR(kernel='linear')
svm_model.fit(x_train, y_train)
y_pred_svm = svm_model.predict(x_test)
mae_svm = mean_absolute_error(y_test, y_pred_svm)
mse_svm = mean_squared_error(y_test, y_pred_svm)
variance_svm = sum((y_pred_svm - y_mean) ** 2) / (n - 1)
std_svm = sqrt(variance_svm)
print("Variance of SVM model: ", variance_svm)
print("Std deviation of SVM model: ", std_svm)
print("MAE from SVM: ", mae_svm)
print("MSE from SVM: ", mse_svm)
print("RMSE from SVM: ", np.sqrt(mse_svm))
print("R2 Score from SVM: ", r2_score(y_test, y_pred_svm))
r2list.append(r2_score(y_test, y_pred_svm))
print()
###############################################################################

# K Nearest Neighbor Regression
knn_model = KNeighborsRegressor(n_neighbors=6)
knn_model.fit(x_train, y_train)
y_pred_knn = knn_model.predict(x_test)
mae_knn = mean_absolute_error(y_test, y_pred_knn)
mse_knn = mean_squared_error(y_test, y_pred_knn)
variance_knn = sum((y_pred_knn - y_mean) ** 2) / (n - 1)
std_knn = sqrt(variance_knn)
print("Variance of KNN model: ", variance_knn)
print("Std deviation of KNN model: ", std_knn)
print("MAE from KNN: ", mae_knn)
print("MSE from KNN: ", mse_knn)
print("RMSE from KNN: ", np.sqrt(mse_knn))
print("R2 Score from KNN: ", r2_score(y_test, y_pred_knn))
r2list.append(r2_score(y_test, y_pred_knn))
print()

# plot linear regression
plt.plot(y_test, y_pred_lr, 'yo', label='Linear Regression')

# plot decision tree regression
plt.plot(y_test, y_pred_dt, 'bo', label='Decision Tree Regression')

# plot random forest regression
plt.plot(y_test, y_pred_rf, 'go', label='Random Forest Regression')

# plot support vector machine regression
plt.plot(y_test, y_pred_svm, 'ro', label='Support Vector Machine Regression')

# plot k nearest neighbor regression
plt.plot(y_test, y_pred_knn, 'co', label='K Nearest Neighbor Regression')

# plot neural network regression
plt.plot(y_test, predictions, 'mo', label='Neural Network Regression')

plt.plot([0, 20], [0, 20], 'k--', label='Ideal Line')

# set labels and title
plt.xlabel('Actual Grades')
plt.ylabel('Predicted Grades')
plt.title('Actual vs Predicted Grades for Different Regression Models')

# set legend
plt.legend()

# show plot
plt.show()

# Feature Ranking
print("Feature Ranking: \n")
feature_list = list(df.columns)
feature_imp = pd.Series(rf_model.feature_importances_,
                        index=feature_list).sort_values(ascending=False)
print(feature_imp)

from sklearn.ensemble import VotingRegressor
# Split the dataset into training and testing sets
# X = df.drop(['final_grade', 'final_score'], axis=1)
# y = df['final_grade']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# Initialize the base models
lin_reg = LinearRegression()
tree_reg = DecisionTreeRegressor(random_state=123)
knn_reg = KNeighborsRegressor()
svr_reg = SVR(kernel='linear')
rf_reg = RandomForestRegressor(random_state=123)

# Initialize the voting regressor
from sklearn.ensemble import VotingRegressor 
voting_reg = VotingRegressor(estimators=[('lin_reg', lin_reg), ('tree_reg', tree_reg), ('knn_reg', knn_reg), ('svr_reg', svr_reg), ('rf_reg', rf_reg)])

# Fit the voting regressor on the training data
voting_reg.fit(x_train, y_train)

# Evaluate the performance of the voting regressor
y_pred = voting_reg.predict(x_test)
print('Ensemble Model Performance:')
print('MAE:', mean_absolute_error(y_test, y_pred))
print('MSE:', mean_squared_error(y_test, y_pred))
print('R2 Score:', r2_score(y_test, y_pred))
print('average R2 score',np.mean(r2list))
if(np.mean(r2list)<r2_score(y_test, y_pred)):
  print("the ensemble model overcomes the average performance of all models")
else:
  print("need to improve the performance of ensemble model")

import requests
import pandas as pd

# Define the streaming API endpoint URL
url = "http://your-api-url-here"

# Initialize an empty list to store the streaming data
data_list = []

# Make a GET request to the API endpoint and stream the data
response = requests.get(url, stream=True)

# Iterate over the streaming data and append each data point to the data_list
for line in response.iter_lines():
    if line:
        # Decode the JSON-encoded data and append it to the data_list
        data_list.append(json.loads(line.decode('utf-8')))

# Convert the data_list into a Pandas DataFrame
df = pd.DataFrame(data_list)