from fastapi import APIRouter
from app.services.evaluation import evaluate_rag, run_eval_tests

router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.post("/single")
def eval_single(question: str):
    return evaluate_rag(question)

@router.post("/tests")
def eval_tests():
    return {"results": run_eval_tests()}