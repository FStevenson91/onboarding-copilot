from pydantic import BaseModel, Field

# --- Concepto 1: BaseModel ---
# En Pydantic, defines "schemas" como clases que heredan de BaseModel.
# Es como definir una interfaz de TypeScript, pero que VALIDA en runtime.
# Equivalente TS: interface Employee { name: string; department: string; }
class Employee(BaseModel):
    name: str
    department: str
    role: str
    email: str

# --- Concepto 2: Field con validaciones ---
# Field() te permite agregar restricciones, como min_length, max_length, etc.
# Equivalente TS: no existe nativamente, necesitarías Zod o Joi.
class Question(BaseModel):
    text: str = Field(min_length=3, max_length=500, description="La pregunta del empleado")
    employee_id: int = Field(gt=0, description="ID del empleado, debe ser positivo")

# --- Concepto 3: Valores por defecto y campos opcionales ---
# Optional se maneja con | None (Python 3.10+) o con default values.
class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")  # como un enum inline)
    content: str = Field(min_length=1)
    source: str | None = None # opcional, puede ser None
