from fastapi import FastAPI
import pandas
import numpy as np
import random
from sklearn import datasets as da 
import kagglehub

employee_dataset = pandas.read_csv("./resources/employee_data.csv")
insurance_dataset = pandas.read_csv("./resources/insurance_data.csv")
vendor_dataset = pandas.read_csv("./resources/vendor_data.csv")

print("Employee dataset shape: ", employee_dataset.shape)
print("Insurance dataset shape: ", insurance_dataset.shape)
print("Vendor dataset shape: ", vendor_dataset.shape)