import os, sys
import yaml
import dill
import numpy as np
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
import boto3
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok= True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
            
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def save_numpy_array(file_path: str, array: np.array):
    try:
        logging.info(f"Saving numpy array")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok= True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)

        logging.info(f"Saved numpy array")
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info(f"Saving a pickle file")
        os.makedirs(os.path.dirname(file_path), exist_ok= True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)

        logging.info(f"Saved pickle file")
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    

def load_object(file_path: str) -> object:
    try:
        logging.info(f"Loading a pickle file")
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} does not exists")
        
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def load_numpy_array(file_path: str) -> np.array:
    try:
        logging.info(f"Loading a numpy array")
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)

def evaluate_model(X_train, y_train, X_test, y_test, models, params):
    try:
        logging.info(f"Evaluating models...")
        report = {}
        for i in range(len(list(models))):
            model = list(models.values())[i]
            para = params[list(models.keys())[i]]

            gs = GridSearchCV(model, para, cv = 3)
            gs.fit(X_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(y_true= y_train, y_pred= y_train_pred)
            test_model_score = r2_score(y_true= y_test, y_pred= y_test_pred)

            report[list(models.keys())[i]] = test_model_score

            return report
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name= os.getenv("AWS_REGION")
)

def load_object_from_s3(bucket_name: str, object_key: str):
    """Load pickle object from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        obj = pickle.load(BytesIO(response['Body'].read()))
        return obj
    except Exception as e:
        raise NetworkSecurityException(f"Error loading object from S3: {str(e)}", sys)
    
def get_latest_model_files():
    """Get the latest preprocessor and model files from S3"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=TRAINING_BUCKET_NAME, 
            Prefix="final_model/"
        )
        
        # print(f"Total objects found: {len(response.get('Contents', []))}")
        
        if 'Contents' not in response:
            raise Exception("No model files found in S3")
        
        # # Print all found files for debugging
        # for obj in response['Contents']:
        #     print(f"Found file: {obj['Key']}")
        
        # Filter files by type
        preprocessor_files = [obj for obj in response['Contents'] if obj['Key'].endswith('preprocessor.pkl')]
        model_files = [obj for obj in response['Contents'] if obj['Key'].endswith('model.pkl')]
        
        # print(f"Preprocessor files: {[f['Key'] for f in preprocessor_files]}")
        # print(f"Model files: {[f['Key'] for f in model_files]}")
        
        if not preprocessor_files:
            raise Exception("No preprocessor.pkl files found")
        if not model_files:
            raise Exception("No model.pkl files found")
        
        # Sort by LastModified and get the latest
        latest_preprocessor = sorted(preprocessor_files, key=lambda x: x['LastModified'], reverse=True)[0]
        latest_model = sorted(model_files, key=lambda x: x['LastModified'], reverse=True)[0]
        
        preprocessor_key = latest_preprocessor['Key']
        model_key = latest_model['Key']
        
        # print(f"Selected preprocessor: {preprocessor_key}")
        # print(f"Selected model: {model_key}")
        
        return preprocessor_key, model_key
        
    except Exception as e:
        print(f"Error in get_latest_model_files: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error finding latest model files: {str(e)}")