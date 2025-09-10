from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys


if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config= training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config= data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info(f"Data Initiation completed ------->>")
        print(data_ingestion_artifact)

        data_validation_config = DataValidationConfig(training_pipeline_config= training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact= data_ingestion_artifact, data_validation_config= data_validation_config)
        logging.info(f"inititate data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        print(data_validation_artifact)
        logging.info(f"Data validation completed ------>")


        data_transformation_config = DataTransformationConfig(training_pipeline_config= training_pipeline_config)
        data_transformation = DataTransformation(data_transformation_config= data_transformation_config, data_validation_artifact= data_validation_artifact)
        logging.info(f"Starting data transformation")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info(f"Data transformation done ------------->")

    except Exception as e:
        raise NetworkSecurityException(e, sys)