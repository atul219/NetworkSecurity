import os, sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)
from networksecurity.entity.artifact_entity import(
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArifact,
    ModelTrainerArtifact
)

class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()

    
    def start_data_ingestion(self):
        try:
            data_ingestion_config = DataIngestionConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info(f"Start Data Ingestion !!")
            data_ingestion = DataIngestion(data_ingestion_config= data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion Artifact !!")
            return data_ingestion_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            data_validation_config = DataValidationConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info(f"Start Data Validation !!")
            data_validation = DataValidation(data_ingestion_artifact= data_ingestion_artifact, data_validation_config= data_validation_config)
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f"Data Validation Artifact !!")
            return data_validation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info(f"Start Data Transformation !!")
            data_transformation = DataTransformation(data_validation_artifact= data_validation_artifact, data_transformation_config= data_transformation_config)
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info(f"Data Transformation Artifact !!")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArifact):
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info(f"Start Model Trainer !!")
            model_trainer = ModelTrainer(data_transformation_artifact= data_transformation_artifact, model_trainer_config= model_trainer_config)
            model_trainer_artifact = model_trainer.inititate_model_trainer()
            logging.info(f"Model Trainer Artifact !!")
            return model_trainer_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact= data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact= data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact= data_transformation_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)