# -*- coding: utf-8 -*-
"""Stock_market_predtiction_lstm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18ctHT1zUANAHMH6Ad68etTefJsxXpET0
"""

# we will collect the stock data 
#preprocess the data-train and test 
#create an stacked LSTM model 
#predict the test data and plot the output 
#predict the future 30 days and plot the output

import pandas_datareader as pdr

key="2e9ad7d8849127eaeaf458a64638d948ea4fdd79"

df= pdr.get_data_tiingo("AAPL", api_key=key)

df.to_csv ("AAPL.csv")

import pandas as pd
dataframe=pd.read_csv ("AAPL.csv")

dataframe.head()

# These are basically apple stock price data. Here close column represents price

df1= dataframe.reset_index()["close"]

df1.head()

import matplotlib.pyplot as plt
plt.plot (df1)

#LSTM are sensitive to the scale of the data. so we apply MinMaxScaler

import numpy as np

from sklearn.preprocessing import MinMaxScaler 
scaler= MinMaxScaler(feature_range= (0,1))
df1= scaler.fit_transform (np.array(df1).reshape (-1,1))

df1.shape

# Train test split 
# There are various ways to do train-test-split. For example- cross validation, random seed. But these are more suitable for ml regression, classification
# But for time-series or sequential data, we have to apply different methods for train test split.
# In time series, each value is dependent on the previous value. for ex- 120,130,125,135. so the next value is dependent on these values. 
# for example- timesteps=3. that means the next value is dependent on previuos three values. and in this way, to get output, we have to shift one position so that we can get 3 features.

training_size= int(len(df1)*0.65) # 65 percent of data is training data 
test_size= len(df1)-training_size 
train_data, test_data= df1[0:training_size,:], df1[training_size:len(df1),:]

train_data[0:5, 0]

def create_dataset (dataset, time_stemp=1):
  data_x, data_y=[],[]
  for i in range((len (dataset)-time_stemp-1)):
    a=dataset[i:(i+time_stemp),0]
    data_x.append (a)
    data_y.append (dataset[i+time_stemp, 0])
  return np.array (data_x), np.array (data_y)

time_stemp=100 
x_train, y_train= create_dataset(train_data, time_stemp)
x_test, y_test= create_dataset (test_data, time_stemp)

x_train.shape, y_train.shape, x_test.shape, y_test.shape

# before feeding the dataset into lstm model, we have to reshape it in 3D axis 
# reshape input into[samples, timestemps, features] which is required for LSTM

x_train= x_train.reshape (x_train.shape[0], x_train.shape[1], 1)
x_test= x_test.reshape (x_test.shape[0], x_test.shape[1], 1)

x_train.shape, x_test.shape

from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Dense 
from tensorflow.keras.layers import LSTM

# defining stacked LSTM model 
model= Sequential () 
model.add(LSTM (50, return_sequences= True, input_shape= (100,1)))
model.add(LSTM (50, return_sequences=True))
model.add(LSTM (50))
model.add(Dense(1))

model.compile (optimizer="adam", loss="mse")

model.summary()

history= model.fit (x_train, y_train, epochs=100, validation_data= (x_test, y_test), batch_size=64, verbose=2)

train_predict= model.predict (x_train)
test_predict= model.predict (x_test)

print (y_train[0:5], train_predict[0:5])

# Transform back to orginal form 
train_predict_2= scaler.inverse_transform (train_predict)
test_predict_2= scaler.inverse_transform(test_predict)

train_predict_2[0:5]

# prediction for next 10 days

len (test_data)

# suppose we want to predict the values of next 10 days, for ex- if my last date of test data is 24th october, i will predict the data for next ten days starting 25th oct

x_input= test_data[341:].reshape (1,-1)

x_input.shape

temp_input= list (x_input) 
temp_input= temp_input[0].tolist()

temp_input

list_output=[]
n_steps=100 
i=0 
while (i<30): # prediction for next 30 days
  if (len(temp_input)>100):
    x_input= np.array (temp_input[1:]) #shifting one position 
    x_input= x_input.reshape (1,-1) 
    x_input= x_input.reshape (1,n_steps,1) 
    y_hat= model.predict (x_input) 
    temp_input.extend (y_hat[0].tolist()) 
    temp_input=temp_input[1:] 
    list_output.extend (y_hat.tolist()) 
    i=i+1
  else:
    x_input= x_input.reshape (1,n_steps,1) 
    y_hat= model.predict (x_input) 
    temp_input.extend(y_hat[0].tolist()) 
    list_output.extend (y_hat.tolist()) 
    i=i+1 

print (list_output)

# Now combining the next 30 days output to existing data 
df3= df1.tolist() 
df3.extend(list_output)

df3= scaler.inverse_transform (df3).tolist()

plt.plot (df3)

len (df3)