import os, sys
import certifi
import pymongo
import pandas as pd
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME, TRAINING_BUCKET_NAME
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import load_object_from_s3, get_latest_model_files


ca = certifi.where()
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)


client = pymongo.MongoClient(mongo_db_url, tlsCAFile = ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = client[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

templates = Jinja2Templates(directory = "./templates")

@app.get("/", tags = ["authentication"])
async def index():
    return RedirectResponse(url = "/docs")


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successfull")
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.post('/predict')
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        # Get the latest model files
        preprocessor_key, model_key = get_latest_model_files()

        preprocessor = load_object_from_s3(bucket_name= TRAINING_BUCKET_NAME, object_key= preprocessor_key)
        final_model = load_object_from_s3(bucket_name= TRAINING_BUCKET_NAME ,object_key= model_key)

        network_model = NetworkModel(preprocessor= preprocessor, model= final_model)
        y_pred = network_model.predict(x= df)
        df['predicted_column'] = y_pred
        df.to_csv("prediction_output/output.csv")
        table_html = df.to_html(classes= 'table table-striped')

        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    app_run(app, host = "0.0.0.0", port = 8000)