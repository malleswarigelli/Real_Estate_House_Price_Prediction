

from housing.entity.config_entity import DataValidationConfig 
from housing.exception import HousingException
import sys, os, json
from housing.logger import logging
from housing.config.configuration import Configuration
from housing.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
import pandas as pd
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab

class DataValidation:
    
    def __init__(self, data_validation_config:DataValidationConfig,
                 data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'>>'*20} Data Validation log started. {'<<'*20} \n\n")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def get_train_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        
        except Exception as e:
            raise HousingException(e,sys) from e   
    
    def is_train_test_file_exist(self):
        try:
            is_train_file_exist = None
            is_test_file_exist = None
            
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)
            
            is_available = is_train_file_exist and is_test_file_exist
            logging.info(f"Is train and test file exist:[{is_available}]")
            
            # if train or test files not available; raise exception
            if not is_available :
                train_file_path = self.data_ingestion_artifact.train_file_path
                test_file_path = self.data_ingestion_artifact.test_file_path
                message = f"Training file:[{train_file_path}] or Testing file:[{test_file_path}] is not exist"
                raise Exception(message)
            
            return is_available
        
        except Exception as e:
            raise HousingException(e,sys) from e  
    
    def validate_dataset_schema(self, schema_file_path, file_path) -> bool:
        pass
    
    # import modules from evidently to generate json type of report  
    def get_and_save_data_drift_report(self):
        try:
            profile = Profile(sections = [DataDriftProfileSection()])
            # need atleast two datasets to checck is stats are different
            train_df, test_df = self.get_train_test_df()
            profile.calculate(train_df, test_df) #calculate data drift using calculate method from profile
            #profile.json() # save the drift into json format; but it's string
            report = json.loads(profile.json()) # convert json string to dictionary or list
            
            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir, exist_ok=True)
            
            with open(report_file_path, "w") as report_file:
                json.dump(report, report_file, indent=6) # save json report to file_path
                
            return report # through this report, now we can validate if there is datadrift or not
        
            
        except Exception as e:
            raise HousingException(e, sys) from e
    
    # now create report page, we need dataset, dashboard (import from evidently) to generate graphs
    def save_data_drift_report_page(self):
        try:
            dashboard = Dashboard(tabs = [DataDriftTab()]) # create dashboard object, need tabs
            train_df, test_df = self.get_train_test_df() # need train, test dataframes
            dashboard.calculate(train_df, test_df)
            
            # directory and file name to save drift_report_page
            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)
            # make report_page_dir if not exist
            os.makedirs(report_page_dir, exist_ok=True)
            
            dashboard.save(report_page_file_path) # saves the drift_report_page
            
        except Exception as e:
            raise HousingException(e, sys) from e  
    
    def is_data_drift_found(self)->bool: 
        try:
            report = self.get_and_save_data_drift_report() # first store the json report
            self.save_data_drift_report_page() # save the data_drift_report_page
            return True
        except Exception as e:
            raise HousingException(e, sys) from e   
   
    
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            # call above functions
            self.is_train_test_file_exist() # gives True or false for Train., test files exist or not
            #self.validate_dataset_schema()
            self.is_data_drift_found()
            
            data_validation_artifact = DataValidationArtifact(
                schema_file_path = self.data_validation_config.schema_file_path, 
                report_file_path = self.data_validation_config.report_file_path, 
                report_page_file_path = self.data_validation_config.report_page_file_path, 
                is_validated = True, 
                message = "Data validation is completed succesfully"
            )
            logging.info(f"Data validation artifact: {data_validation_artifact}")    
            return data_validation_artifact
            
        except Exception as e:
            raise HousingException(e, sys) from e   
        
    def __del__(self):
        logging.info(f"{'>>'*30}Data validation log completed.{'<<'*30}")