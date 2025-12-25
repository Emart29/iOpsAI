from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Experiment
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["experiments"])

class ExperimentResponse(BaseModel):
    id: int
    session_id: str
    dataset_name: str
    timestamp: datetime
    rows: int
    columns: int
    status: str

    class Config:
        orm_mode = True

@router.get("/experiments", response_model=List[ExperimentResponse])
async def get_experiments(db: Session = Depends(get_db)):
    experiments = db.query(Experiment).order_by(Experiment.timestamp.desc()).all()
    return experiments

@router.delete("/experiments/{id}")
async def delete_experiment(id: int, db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(experiment)
    db.commit()
    return {"message": "Experiment deleted"}
