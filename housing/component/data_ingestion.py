

# structure for Data Ingestion component

from housing.entity.config_entity import DataIngestionConfig 
from housing.exception import HousingException
import sys, os
from housing.logger import logging
from housing.entity.artifact_entity import DataIngestionArtifact
import pandas as pd
import numpy as np
import pymongo
from sklearn.model_selection import StratifiedShuffleSplit

class DataIngestion:
    
    def __init__(self,data_ingestion_config:DataIngestionConfig ): # DataIngestionConfig is from configuration.py
        # parameters: which config? is from config_entity
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20} ")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise HousingException(e, sys) from e
        
    def get_data_from_mongodb(self):
        try:
            self.client = pymongo.MongoClient("mongodb+srv://gellima:mongohousing@cluster0.7sadqvu.mongodb.net/?retryWrites=true&w=majority")
            database = self.client["HousingDB1"]
            logging.info(f"Database:[{database}] is found!")
            
            collection1 = database['housing.collection_set']
            logging.info(f"Collection: [{collection1}] is found!")
            
            cursor = collection1.find()
            mongo_documents = list(cursor) # list of dictionaries
            
            # convert documents into pandas dataframe
            dataframe_csv = pd.DataFrame(mongo_documents, columns=["longitude", "latitude", "housing_median_age", "total_rooms", 
                                                                   "total_bedrooms", "population", "households", "median_income", 
                                                                   "median_house_value", "ocean_proximity"])
            logging.info(f"Converted data into pandas dataframe:[{dataframe_csv}]")
            
            # now, storing this data into raw_data folder
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)
            
            os.makedirs(raw_data_dir, exist_ok=True)
            logging.info(f"Raw_data folder:[{raw_data_dir}] is created.")
            
            # now, create raw_data_file_path to store dataframe_csv
            housing_file_path = 'housing.csv'
            raw_data_file_path = os.path.join(raw_data_dir, housing_file_path)
            
            logging.info(f"Storing pandas dataframe into csv file")
            dataframe_csv.to_csv(raw_data_file_path, index=False)
            
            logging.info(f"{'=='*20}Successfully accessed data from mongobd database [{database}].{'=='*20}")
            return dataframe_csv
        
        except Exception as e:
            raise HousingException(e, sys) from e

    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            file_name = os.listdir(raw_data_dir)[0]

            housing_file_path = os.path.join(raw_data_dir, file_name)


            logging.info(f"Reading csv file: [{housing_file_path}]")
            housing_data_frame = pd.read_csv(housing_file_path)

            housing_data_frame["income_cat"] = pd.cut(
                                                    housing_data_frame["median_income"],
                                                    bins=[0.0, 1.5, 3.0, 4.5, 6.0, np.inf],
                                                    labels=[1,2,3,4,5]
                                                )
            

            logging.info(f"Splitting data into train and test")
            strat_train_set = None
            strat_test_set = None

            split = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)

            for train_index,test_index in split.split(housing_data_frame, housing_data_frame["income_cat"]):
                strat_train_set = housing_data_frame.loc[train_index].drop(["income_cat"],axis=1)
                strat_test_set = housing_data_frame.loc[test_index].drop(["income_cat"],axis=1)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
                                            file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
                                        file_name)
            
            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting split training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)

            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok= True)
                logging.info(f"Exporting split test dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)
            

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                test_file_path=test_file_path,
                                is_ingested=True,
                                message=f"Data ingestion completed successfully."
                                )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise HousingException(e,sys) from e


    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            self.get_data_from_mongodb()
            return self.split_data_as_train_test()

        except Exception as e:
            raise HousingException(e,sys) from e
    

    def __del__(self):
        logging.info(f"{'>>'*20}Data Ingestion log completed.{'<<'*20} \n\n")