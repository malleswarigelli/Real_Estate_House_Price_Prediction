

from housing.exception import HousingException
from housing.logger import logging
from housing.entity.config_entity import DataTransformationConfig
from housing.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
from housing.util.util import read_yaml_file, save_object, load_data, save_numpy_array_data
from housing.constant import * 

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer # concatenate columns
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

import sys, os
import numpy as np
import pandas as pd

# columns:
#  longitude: float
#  latitude: float
#  housing_median_age: float
#  total_rooms: float
#  total_bedrooms: float
#  population: float
#  households: float
#  median_income: float
#  median_house_value: float
#  ocean_proximity: category

#from sklearn.base import BaseEstimator, TransformerMixin
class FeatureGenerator(BaseEstimator, TransformerMixin):
    '''BaseEstimator is a base class, mandatory class for all ML applications; 
            SO, declare all parameters at class level i.e in __init__ function instead of using *args, **kwargs 
            
        TransformerMixin class contains fit_transform method i.e def fit_transform(self, X, y,**fit_params)
        **fit_params i.e dictionary of parameters
    '''
    def __init__(self, add_bedrooms_per_room = True,
                 total_rooms_ix = 3,
                 population_ix = 5,
                 households_ix = 6,
                 total_bedrooms_ix = 4, columns = None):
    
        """
        FeatureGenerator Initiation
        add_bedrooms_per_room : bool
        total_rooms_ix: int of index # of column, total_rooms
        population_ix: int of index # of column,population
        households_ix: int of index # of column,households
        total_bedrooms_ix: int of index # of column,total_bedrooms
        
        """   
        try:
            self.columns = columns
            if self.columns is not None:
                total_rooms_ix = self.columns.index(COLUMN_TOTAL_ROOMS)
                population_ix = self.columns.index(COLUMN_POPULATION)
                households_ix = self.columns.index(COLUMN_HOUSEHOLDS)
                total_bedrooms_ix = self.columns.index(COLUMN_TOTAL_BEDROOM)

            self.add_bedrooms_per_room = add_bedrooms_per_room
            self.total_rooms_ix = total_rooms_ix
            self.population_ix = population_ix
            self.households_ix = households_ix
            self.total_bedrooms_ix = total_bedrooms_ix
        except Exception as e:
            raise HousingException(e, sys) from e

    def fit(self, X, y=None):
        return self
            
    def transform(self, X, y=None):
        try:
            room_per_household = X[:, self.total_rooms_ix] / \
                                 X[:, self.households_ix]
            population_per_household = X[:, self.population_ix] / \
                                       X[:, self.households_ix]
            # if self.add_bedrooms_per_room = true
            if self.add_bedrooms_per_room:
                bedrooms_per_room = X[:, self.total_bedrooms_ix] / \
                                    X[:, self.total_rooms_ix]
                # concatenate features using np_c
                generated_feature = np.c_[
                    X, room_per_household, population_per_household, bedrooms_per_room]
            # if self.add_bedrooms_per_room != true
            else:
                generated_feature = np.c_[
                X, room_per_household, population_per_household]
                
            return generated_feature
        except Exception as e:
            raise HousingException(e, sys) from e

class DataTransformation:
    '''
    returns DataTransformationArtifact
    ["transformed_train_file_path", "transformed_test_file_path", "preprocessed_object_file_path","is_transformed", "message"]'''
    
    # parameter is "which config"? is from config_entity # a:b (b is datatype of a i.e type(a))
    # another parameter is "which artifact" (we r going to use o/p of DataIngestionArtifact ---> tells where is my train, test dir, 
                                                                    # DataValidationArtifact --> uses schemafile as input for DataTransformation)     
    def __init__(self, data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact
                 ):
        try:
            logging.info(f"{'>>'*20}Data Transformation log started.{'<<'*20} ")
            self.data_transformation_config= data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact

        except Exception as e:
            raise HousingException(e,sys) from e 
        
        
  
    def get_data_transformer_object(self) -> ColumnTransformer:
        '''
        function returns preprocessing object
        '''
        try:
            # read schema file, get numerical and categorical column names from schema
            schema_file_path = self.data_validation_artifact.schema_file_path

            dataset_schema = read_yaml_file(file_path=schema_file_path)

            numerical_columns = dataset_schema[NUMERICAL_COLUMN_KEY]
            categorical_columns = dataset_schema[CATEGORICAL_COLUMN_KEY]
            
            # transformations for numerical columns   
            num_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy="median")),
                ('feature_generator', FeatureGenerator(
                    add_bedrooms_per_room=self.data_transformation_config.add_bedroom_per_room,
                    columns = numerical_columns
                )),
                ('scaler', StandardScaler())
            ]
            )
            # transformations for categorical columns   
            cat_pipeline = Pipeline(steps=[
                 ('impute', SimpleImputer(strategy="most_frequent")),
                 ('one_hot_encoder', OneHotEncoder()),
                 ('scaler', StandardScaler(with_mean=False))
            ]
            )
            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")
            
            # concatenate differnt pipeline processes
            # create an obj, accepts tuple takes 3 values (name, pipeline, columns to apply the transformation)
            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, numerical_columns),
                ('cat_pipeline', cat_pipeline, categorical_columns),
            ])
            return preprocessing
            # preprocessed object would be saved as numpy array (function is written in util)
                
        except Exception as e:
            raise HousingException(e, sys) from e 

    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")
            # returns preprocessing object
            preprocessing_obj = self.get_data_transformer_object()
            
            logging.info(f"Obtaining training and test file path.")
            # get train, test file paths, schema file path
            train_file_path = self.data_ingestion_artifact.train_file_path 
            # C:\Users\anjik\Desktop\iNeuron_FSDS\ML_end_to_end_projects\ML_project1\housing\artifact\data_ingestion\2023-02-10-17-01-52\ingested_data\train\housing.csv
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            schema_file_path = self.data_validation_artifact.schema_file_path
            
            logging.info(f"Loading training and test data as pandas dataframe.")
            # load train, test files and compare with schema file if dtype of columns is same? USE load_data function from util, returns dataframe
            train_df = load_data(file_path = train_file_path, schema_file_path = schema_file_path) # returns dataframe
            test_df = load_data(file_path = test_file_path, schema_file_path = schema_file_path)
            
            # schema file
            schema = read_yaml_file(file_path=schema_file_path)
            
            # from schema, get target column i.e 'median_housing_value'
            target_column_name = schema[TARGET_COLUMN_KEY]
            
            logging.info(f"Splitting input and target feature X,y from training and testing dataframe. ")
            # X_train, y_train
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name]

            # X_test, y_test
            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name]
            
            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df) # X-train_array
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df) # X_test_array


            train_arr = np.c_[ input_feature_train_arr, np.array(target_feature_train_df)]

            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            

            # save these arrays using def save_numpy_array_data(file_path: str, array: np.array)
            
            # where do i get train, test directories i.e from DataTransformationConfig
            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir
            
            # how do i get file name i.e housing.csv
                    # np file is not of csv file; so replace .csv with .npz
            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz") # housing.csv is replaced with housing.npz
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")
            
            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            #C:\Users\anjik\Desktop\iNeuron_FSDS\ML_end_to_end_projects\ML_project1\housing\artifact\data_transformation\2023-02-10-17-01-52\transformed_data\train\housing.npz
            
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            
            logging.info(f"Saving transformed training and testing array. ")
            # save the array
            save_numpy_array_data(file_path=transformed_train_file_path, array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path, array=test_arr)

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing pickle object.")
            save_object(file_path=preprocessing_obj_file_path, obj=preprocessing_obj)
            
            # create data_transformation_artifact
            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
                                                message="Data transformation successfull.",
                                                transformed_train_file_path=transformed_train_file_path,
                                                transformed_test_file_path=transformed_test_file_path,
                                                preprocessed_object_file_path=preprocessing_obj_file_path

                                                )
            logging.info(f"Data transformationa artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        
        except Exception as e:
            raise HousingException(e,sys) from e
            
    def __del__(self):
        logging.info(f"{'>>'*20}Data Transformation log completed.{'<<'*20} \n\n")