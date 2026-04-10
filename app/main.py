from fastapi import FastAPI
from app.models.schemas import Employee, Question, ChatMessage
from app.routes.chat import router as chat_router
from app.routes.evaluation import router as eval_router


app = FastAPI(
    title="Onboarding Copilot API",
    description="Copilot interno para onboarding de empleados",
    version="0.1.0"
)
app.include_router(chat_router)
app.include_router(eval_router)


# --- Endpoint básico de health check ---
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Onboarding Copilot running"}

# --- POST que recibe y valida un Employee ---
# Fíjate: solo con poner Employee como tipo del parámetro,
# FastAPI + Pydantic validan automáticamente el body.
# En Express tendrías que usar middleware + Joi/Zod manualmente.
@app.post("/employees")
def create_employee(employee: Employee):
    return {"received": employee.model_dump()}

# --- POST que recibe una pregunta ---
@app.post("/questions")
def ask_question(question: Question):
    return {"received": question.model_dump(), "answer": "Próximamente conectado al LLM"}