
import yaml, dill, os, sys
import pandas as pd
from housing.exception import HousingException
from housing.logger import logging

# write yaml file
def write_yaml_file(file_path:str, data:dict=None):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        if data is not None:
            with open(file_path, "wb") as yaml_file:
                yaml.dump(data, yaml_file)
    except Exception as e:
        raise HousingException(e,sys) from e        

# read yaml file
def read_yaml_file(file_path:str):
    try:
        with open(file_path, "rb") as file_obj:
            yaml.safe_load(file_obj)
            
    except Exception as e:
        raise HousingException(e,sys) from e