from sqlalchemy import create_engine, Column, Float, Integer, DateTime, Text,text, BigInteger, Numeric, Date,JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.utils.utility import PREDICTION_DATABASE_URL,METRICS_DB_URL




# python -m app.db.crud



# Database connection
engine = create_engine(PREDICTION_DATABASE_URL)
engine2=create_engine(METRICS_DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
SessionLocal2=sessionmaker(bind=engine2, autoflush=False, autocommit=False)
Base = declarative_base()


class ModelMetrics(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    model_name = Column(Text)
    model_version = Column(Text)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)

    metrics = Column(JSON)

def insert_metrics(model_name, model_version, accuracy, precision, recall, f1_score, metrics):
    session = SessionLocal2()
    try:
        new_row = ModelMetrics(
            model_name=model_name,
            model_version=model_version,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            metrics=metrics
        )

        session.add(new_row)
        session.commit()
        session.refresh(new_row)

        print("Inserted successfully:", new_row.id)
        return new_row.id

    except Exception as e:
        session.rollback()
        print("Insert failed:", str(e))
        return None

    finally:
        session.close()



class Prediction(Base):
    __tablename__ = "transactions_predictions"

    transaction_id = Column(UUID(as_uuid=True),primary_key=True,server_default=text("uuid_generate_v4()"))

    timestamp = Column(DateTime,nullable=False,server_default=text("CURRENT_TIMESTAMP"))

    fraud_probability = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    actual_label = Column(Integer, nullable=True)
    merchant = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    amt = Column(Numeric(12, 2), nullable=False)
    gender = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    state = Column(Text, nullable=False)
    zip = Column(Text, nullable=False)
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    city_pop = Column(BigInteger, nullable=False)
    job = Column(Text, nullable=False)
    unix_time = Column(BigInteger, nullable=False)
    merch_lat = Column(Float, nullable=False)
    merch_long = Column(Float, nullable=False)
    trans_date_trans_time = Column(DateTime, nullable=False)
    dob = Column(Date, nullable=False)





def insert_prediction(merchant,category,amt,gender,city,state,zip,lat,long,city_pop,job,unix_time,merch_lat, merch_long,
                      trans_date_trans_time,dob,fraud_probability,prediction,actual_label=None):
    
    session = SessionLocal()
    try:
        new_row = Prediction(
            merchant=merchant,
            category=category,
            amt=amt,
            gender=gender,
            city=city,
            state=state,
            zip=zip,
            lat=lat,
            long=long,
            city_pop=city_pop,
            job=job,
            unix_time=unix_time,
            merch_lat=merch_lat,
            merch_long=merch_long,
            trans_date_trans_time=trans_date_trans_time,
            dob=dob,
            fraud_probability=fraud_probability,
            prediction=prediction,
            actual_label=actual_label
        )

        session.add(new_row)
        session.commit()
        session.refresh(new_row)

        print("Inserted successfully:", new_row.transaction_id)
        return new_row.transaction_id

    except Exception as e:
        session.rollback()
        print("Insert failed:", str(e))
        return None

    finally:
        session.close()




def update_actual_label(transaction_id: str, actual_label: int):
    session = SessionLocal()
    try:
        row = (session.query(Prediction).filter(Prediction.transaction_id == transaction_id).first())

        if row is None:
            return False

        row.actual_label = actual_label
        session.commit()
        return True

    except Exception:
        session.rollback()
        raise          # keeps original error
    finally:
        session.close()


if __name__ == "__main__":
    insert_prediction(
        merchant="fraud_Kirlin and Sons",
        category="shopping_net",
        amt=2500.75,
        gender="M",
        city="Los Angeles",
        state="CA",
        zip="90001",
        lat=34.0522,
        long=-118.2437,
        city_pop=1000000,
        job="Engineer",
        unix_time=1711000000,
        merch_lat=34.0622,
        merch_long=-118.2537,
        trans_date_trans_time=datetime(2026, 4, 1, 10, 30, 0),
        dob=datetime(1995, 6, 15).date(),
        fraud_probability=0.91,
        prediction=1,
        actual_label=None
    )
















