import tensorflow as tf
from tensorflow import keras
from model import process_df
import pandas as pd
import numpy as np

csv = pd.read_csv("data/test.csv")
csv2 = pd.read_csv("data/test2.csv")
csv2.drop(columns=["viajes"], inplace=True)

WINDOW_SIZE = 30
TARGET_COLUMN = 'viajes'

inputs = [col for col in csv.columns if col != TARGET_COLUMN]

target = csv[TARGET_COLUMN].values

X_data = [] 
y_data = [] 

# 2. Generar ventanas de entrenamiento (X_data y y_data)
for i in range(len(csv) - WINDOW_SIZE - 1): # Ajusta el '1' si quieres predecir 1 día, o más si quieres más días
    X_window = inputs[i : i + WINDOW_SIZE] 
    y_target = target[i + WINDOW_SIZE] # Si quieres predecir SOLO el día siguiente
    
    X_data.append(X_window)
    y_data.append(y_target)

# 3. Convertir a arrays de numpy
X_train = np.array(X_data)
y_train = np.array(y_data)