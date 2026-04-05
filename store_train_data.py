import os
from app.utils.utility import upload_training_data_to_db ,BASE_DIR





if __name__ == "__main__":
    data_path = os.path.join(BASE_DIR, "datasets", "fraud_train_data.csv")
    upload_training_data_to_db(data_path)