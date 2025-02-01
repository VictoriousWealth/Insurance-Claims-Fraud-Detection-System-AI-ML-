from fastapi import FastAPI
import pandas
import numpy as np
import random
from sklearn import datasets as da 
import kagglehub
import shutil

source = r"C:\Users\efeon\.cache\kagglehub\datasets\mastmustu\insurance-claims-fraud-data\versions\2\employee_data.csv"  # Source file path
destination = r"C:\Users\efeon\Insurance Claims Fraud Detection System\backend\employee_data.csv"  # Destination directory
shutil.move(source, destination)

source = r"C:\Users\efeon\.cache\kagglehub\datasets\mastmustu\insurance-claims-fraud-data\versions\2\insurance_data.csv"  # Source file path
destination = r"C:\Users\efeon\Insurance Claims Fraud Detection System\backend\insurance_data.csv"  # Destination directory
shutil.move(source, destination)

source = r"C:\Users\efeon\.cache\kagglehub\datasets\mastmustu\insurance-claims-fraud-data\versions\2\vendor_data.csv"  # Source file path
destination = r"C:\Users\efeon\Insurance Claims Fraud Detection System\backend\vendor_data.csv"  # Destination directory
shutil.move(source, destination)
