# -*- coding: utf-8 -*-
"""ictak_exit_test_loan.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bRfOLxjMjLBug8Kwj8vxim6LqDfDJhwB
"""

# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

# Load data files (make sure these are uploaded to Colab first)
train_data = pd.read_csv('/content/train_ctrUa4K.csv')
test_data = pd.read_csv('/content/test_lAUu6dG.csv')
sample_submission = pd.read_csv('/content/sample_submission_49d68Cx.csv')

# Data Cleaning and Preprocessing
# Copy data to avoid modifying original
train_data_cleaned = train_data.copy()
test_data_cleaned = test_data.copy()

# Define imputers
mode_imputer = SimpleImputer(strategy="most_frequent")
median_imputer = SimpleImputer(strategy="median")

# Impute missing categorical values with the mode
categorical_cols = ['Gender', 'Married', 'Dependents', 'Self_Employed']
train_data_cleaned[categorical_cols] = mode_imputer.fit_transform(train_data_cleaned[categorical_cols])
test_data_cleaned[categorical_cols] = mode_imputer.transform(test_data_cleaned[categorical_cols])

# Impute missing numerical values with the median
numerical_cols = ['LoanAmount', 'Loan_Amount_Term', 'Credit_History']
train_data_cleaned[numerical_cols] = median_imputer.fit_transform(train_data_cleaned[numerical_cols])
test_data_cleaned[numerical_cols] = median_imputer.transform(test_data_cleaned[numerical_cols])

# Feature Engineering
train_data_cleaned['Total_Income'] = train_data_cleaned['ApplicantIncome'] + train_data_cleaned['CoapplicantIncome']
test_data_cleaned['Total_Income'] = test_data_cleaned['ApplicantIncome'] + test_data_cleaned['CoapplicantIncome']

train_data_cleaned['Loan_Income_Ratio'] = train_data_cleaned['LoanAmount'] / train_data_cleaned['Total_Income']
test_data_cleaned['Loan_Income_Ratio'] = test_data_cleaned['LoanAmount'] / test_data_cleaned['Total_Income']

# Encode target variable 'Loan_Status'
label_encoder = LabelEncoder()
train_data_cleaned['Loan_Status'] = label_encoder.fit_transform(train_data_cleaned['Loan_Status'])

# One-hot encode categorical columns
categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area']
train_data_encoded = pd.get_dummies(train_data_cleaned, columns=categorical_cols, drop_first=True)
test_data_encoded = pd.get_dummies(test_data_cleaned, columns=categorical_cols, drop_first=True)

# Align test data with train data
test_data_encoded = test_data_encoded.reindex(columns=train_data_encoded.columns.drop('Loan_Status'), fill_value=0)

# Drop 'Loan_ID' from both train and test datasets
X = train_data_encoded.drop(columns=['Loan_ID', 'Loan_Status'])
y = train_data_encoded['Loan_Status']
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train the model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate the model on validation set
y_val_pred = model.predict(X_val)
val_accuracy = accuracy_score(y_val, y_val_pred)
print("Validation Accuracy:", val_accuracy)
print("\nClassification Report:\n", classification_report(y_val, y_val_pred))

# Ensure 'Loan_ID' is dropped from the test data before making predictions
X_test = test_data_encoded.drop(columns=['Loan_ID'])

# Predict on the test data
test_predictions = model.predict(X_test)

# Prepare submission file
submission = pd.DataFrame({'Loan_ID': test_data['Loan_ID'], 'Loan_Status': label_encoder.inverse_transform(test_predictions)})
submission.to_csv('/content/submission.csv', index=False)
print("Submission file created successfully.")