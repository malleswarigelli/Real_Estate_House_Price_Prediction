


# compare the new trained best model with the model in production (we need their locations)
# check accuracy; create path for better model

from housing.logger import logging
from housing.exception import HousingException
from housing.entity.config_entity import ModelEvaluationConfig
from housing.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,ModelTrainerArtifact,ModelEvaluationArtifact
from housing.constant import *
import numpy as np
import os
import sys
from housing.util.util import write_yaml_file, read_yaml_file, load_object, load_data
from housing.entity.model_factory import evaluate_regression_model


class ModelEvaluation:

    def __init__(self, model_evaluation_config: ModelEvaluationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            logging.info(f"{'>>'*20}Model Evaluation log started.{'<<'*20} ")
            self.model_evaluation_config = model_evaluation_config # for model_evaluation_file_path
            self.data_ingestion_artifact = data_ingestion_artifact # for training, test datasets
            self.data_validation_artifact = data_validation_artifact # for schema file path
            self.model_trainer_artifact = model_trainer_artifact # for newly trained model path
            
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def get_best_model(self):
        '''
        get best_model exist in production
        '''
        try:
            # when we run pipeline first time, there is no best model in production; so setting model = None
            model = None
            # get location of model_evaluation.yaml
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path
            # if model_evaluation.yaml file not available; create empty model_evaluation.yaml file and return None
            if not os.path.exists(model_evaluation_file_path):
                write_yaml_file(file_path = model_evaluation_file_path) 
                return model
            
            # if model_evaluation.yaml exist, read yaml file as dictionary
            model_eval_file_content = read_yaml_file(file_path = model_evaluation_file_path)
            
            
            # if model_evaluation.yaml is None, get empty dictionary; else get yaml file contents in dictionary
            model_eval_file_content = dict() if model_eval_file_content is None else model_eval_file_content
            
            if BEST_MODEL_KEY not in model_eval_file_content:
                return model # returns None
            
            # if the top 2 scenarios are not there; load pickle file using load_object
            model = load_object(file_path = model_eval_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])
            return model
                    
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def update_evaluation_report(self, model_evaluation_artifact: ModelEvaluationArtifact):
        '''do comparison
        if trained model is better than best model in production, 
        update BEST_MODEL location in model_evaluation.yaml file with new trained model file location
        '''
        try:
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path
            model_eval_file_content  = read_yaml_file(file_path=model_evaluation_file_path)
            
            model_eval_file_content = dict() if model_eval_file_content is None else model_eval_file_content
            
            # if it's first time running the pipeline and there is no best model esixt in production; so set it as None
            previous_best_model = None
            # but make sure; if model exist, consider it as previous model, move to history; SO that new trained model can be best_model
            if BEST_MODEL_KEY in model_eval_file_content:
                previous_best_model = model_eval_file_content[BEST_MODEL_KEY]
            # log earlier model content from .yaml file
            logging.info(f"Prevous eval result: {model_eval_file_content}")
            
            # new evaluation result i.e with new trained model location
            eval_result = {
                BEST_MODEL_KEY: {
                    MODEL_PATH_KEY: model_evaluation_artifact.evaluated_model_path,
                    }
                }
            
            # if there is a best model exist in evaluation.yaml file    
            if previous_best_model is not None:
                model_history = {self.model_evaluation_config.time_stamp: previous_best_model}
                if HISTORY_KEY not in model_eval_file_content:
                    history = {HISTORY_KEY: model_history}
                    eval_result.update(history)
                else:
                    model_eval_file_content[HISTORY_KEY].update(model_history)

            model_eval_file_content.update(eval_result)
            logging.info(f"Updated eval result:{model_eval_file_content}")
            
            # create yaml file with updated evaluation content
            write_yaml_file(file_path=model_evaluation_file_path, data=model_eval_file_content)
        except Exception as e:
            raise HousingException(e, sys) from e
            
           
    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        '''function make comparison between new trained model vs best_model in production'''
        try:
            # path of trained model.pkl file
            trained_model_file_path = self.model_trainer_artifact.trained_model_file_path
            # load model.pkl file
            trained_model_object = load_object(file_path=trained_model_file_path)

            # load train,test files from data_ingestion_artifact
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            # load schem file from data_validation artifact
            schema_file_path = self.data_validation_artifact.schema_file_path
            
            # convert train,test files into pandas dataframes
            train_dataframe = load_data(file_path=train_file_path,
                                        schema_file_path=schema_file_path)
            test_dataframe = load_data(file_path=test_file_path,
                                        schema_file_path=schema_file_path)
            # read schema_yaml file
            schema_content = read_yaml_file(file_path= schema_file_path)
            
            # get target column name from schema
            target_column_name = schema_content[TARGET_COLUMN_KEY]
            
            # convert target column data to numpy array
            logging.info(f"Converting {target_column_name} column into numpy array")
            train_target_array = np.array(train_dataframe[target_column_name])
            test_target_array = np.array(test_dataframe[target_column_name])
            logging.info(f"Converted {target_column_name} into numpy array from both train, test dataframes")
            
            # dropping target column from train and test dataframes
            logging.info(f"Dropping {target_column_name} from both train, test dataframes")
            train_dataframe.drop(target_column_name, axis=1, inplace = True)
            test_dataframe.drop(target_column_name, axis=1, inplace=True)
            logging.info(f"Dropped {target_column_name} from both train, test dataframes")
            
            # Get the current production model; get None if there is no model exist in production
            model = self.get_best_model()
            
            # if there is no production model; code after return statement doesn't execute
            if model is None:
                logging.info("Not found any existing model in production. Hence accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
                return model_evaluation_artifact
            
            # list of proudction model, new trained model
            model_list = [model, trained_model_object]
            # compares two models listed, give the best model
            metric_info_artifact = evaluate_regression_model(model_list=model_list,
                                                               X_train=train_dataframe,
                                                               y_train=train_target_array,
                                                               X_test=test_dataframe,
                                                               y_test=test_target_array,
                                                               base_accuracy=self.model_trainer_artifact.model_accuracy,
                                                               )
            logging.info(f"Model evaluation completed. model metric artifact: {metric_info_artifact}")
            
            # if none of the two models had accuracy >base accuracy
            if metric_info_artifact is None:
                response = ModelEvaluationArtifact(is_model_accepted=False,
                                                   evaluated_model_path=trained_model_file_path
                                                   )
                logging.info(response)
                return response

            if metric_info_artifact.index_number == 1:
                # index_number 1 is trained_model
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")

            else:
                logging.info("Trained model is no better than existing model hence not accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=False)
            return model_evaluation_artifact
        except Exception as e:
            raise HousingException(e, sys) from e


    def __del__(self):
        logging.info(f"{'>>'*20}Model Evaluation log completed.{'<<'*20} ")
            
           