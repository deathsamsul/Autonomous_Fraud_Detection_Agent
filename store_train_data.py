import os
from app.utils.utility import upload_training_data_to_db ,BASE_DIR


# python -m store_train_data
# python store_train_data.py


# cp /mnt/c/Users/samsu/Downloads/fraudTest.csv/fraud_train_data.csv /home/sam/projects/fraud_detection_mlops/datasets/fraud_train_data.csv

if __name__ == "__main__":
    data_path = os.path.join(BASE_DIR, "datasets", "fraud_train_data.csv")
    # data_path= "/mnt/c/Users/samsu/Downloads/fraudTest.csv/fraud_train_data.csv"
    upload_training_data_to_db(data_path)

