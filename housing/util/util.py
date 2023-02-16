
'''
Declare any helper functions in util.py, like reading yaml file, how to create pickle files, load pickle objects 
and util is used when needed to call helper functions..
'''

import os, sys, dill, yaml
import numpy as np
import pandas as pd
from housing.exception import HousingException
from housing.constant import *

def write_yaml_file(file_path:str, data:dict=None):
    '''
    write yaml file
    inputs: 
        file_path as str
        data as dictionary  
    '''
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w") as yaml_file:
            if data is not None:
                yaml.dump(data, yaml_file)
                
    except Exception as e:
        raise HousingException(e, sys) from e        
            
def read_yaml_file(file_path:str) -> dict:
    '''
    Reads YAML file, returs contents as a dictionary or .json
    file_path : str
    '''
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
        
    except Exception as e:
        raise HousingException(e, sys) from e   


# save transformed or preprocessed object as numpy array
def save_numpy_array_data(file_path: str, array: np.array):
    '''saves transformed data i.e numpy array data to file
    file_path: str (where you r going to save the file)
    array: np.array is the data to save 
    '''
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array) # saves file_path as np.array
            
    except Exception as e:
        raise HousingException(e, sys) from e 
    
def load_numpy_array_data(file_path: str) -> np.array:
    '''
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    
    '''
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj) # np.load gives numpy array
        
    except Exception as e:
        raise HousingException(e, sys) from e 
    
# saving pickle file
def save_object(file_path:str, obj):
    '''
    saves preprocessing object i.e pickle file to path specified
    file_path:str (where you are saving preprocessing object)
    obj: Any sort of preprocessing obj
    '''
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            dill.dump(obj, file_obj) # dumps pickle obj into file_path
            
    except Exception as e:
        raise HousingException(e, sys) from e
    
# loading pickle file
def load_object(file_path:str):
    '''
    file_path:str (pickle file path)
    '''
    try:
        with open(file_path, 'rb') as file_obj:
            return dill.load(file_obj)
        
    except Exception as e:
        raise HousingException(e, sys) from e
    
  
 
def load_data(file_path:str, schema_file_path:str) -> pd.DataFrame:
        '''
        is to read input data
        function takes input file path, schema file path locations as string
            read input file, check and change datatype of columns based on schema file 
            returns dataframe
        '''
        try:
            # read schema yaml_file as dictionary of column and datype; {column name: dtype}
            dataset_schema = read_yaml_file(schema_file_path)
            # slice column names from schema_file 
            schema = dataset_schema[DATASET_SCHEMA_COLUMNS_KEY]
            
            # read input data file as dataframe
            dataframe = pd.read_csv(file_path)
            error_message = ""
            
            # loop through columns of dataframe, check if column name exist in schema.keys()
            for column in dataframe.columns:
                if column in list(schema.keys()):
                    # convert dtype of column as schema column dtype
                    dataframe[column].astype(schema[column])
                else:
                    error_message = f"{error_message} \nColumn: [{column}] is not in the schema"
            if len(error_message) > 0:
                raise Exception(error_message)
            return dataframe
            
        except Exception as e:
            raise HousingException(e, sys) from e 
    
    
