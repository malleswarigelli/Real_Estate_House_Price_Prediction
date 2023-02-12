

training_pipeline_config:
    pipeline_name: housing
    artifact_dir: artifact
    
data_ingestion_config:
    dataset_download_url: https://raw.githubusercontent.com/ageron/handson-ml/master/datasets/housing/housing.tgz
    raw_data_dir: raw_data
    tgz_download_dir: tgz_data
    ingested_dir: ingested_data
    ingested_train_dir: train
    ingested_test_dir: test

data_validation_config:
    
    
data_transformation_config:
    

model_trainer_config:
    
model_evaluation_config:
    
model_pusher_config:
    model_export_dir : saved_models
    
    
