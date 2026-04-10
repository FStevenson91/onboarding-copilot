from app.services.rag import search_context, vectorstore
from app.services.llm import get_chat_response

def evaluate_rag(question: str) -> dict:
    """
    Evalua manualmente la calidad del RAG para una pregunta.
    Retorna la pregunta, el contexto recuperado, y la respuesta del LLM.
    """

    # 1. Recuperar contexto
    context = search_context(question)

    # 2. Obtener respuesta del LLM
    messages = [{"role": "user", "content": question}]
    answer = get_chat_response(messages)

    # 3. Retornar todo para inspección
    return {
        "question": question,
        "context_retrieved": context,
        "answer": answer
    }

def run_eval_tests() -> list[dict]:
    """
    Corre un conjunto de preguntas de prueba y evalua las respuestas.
    Estas son preguntas donde SABEMOS la respuesta correta (ground truth).
    """

    test_cases = [
        {
            "question": "¿Cuántos días de vacaciones tiene un empleado nuevo?",
            "ground_truth": "15 días hábiles al año"
        },
        {
            "question": "¿Cuál es el horario de trabajo?",
            "ground_truth": "Lunes a Viernes, 9:00 a 18:00"
        },
        {
            "question": "¿Qué beneficios tengo?",
            "ground_truth": "Seguro de salud, bono almuerzo $5.000 CLP, acceso Udemy/Coursera, día libre cumpleaños"
        },
        {
            "question": "¿Puedo ir en jeans a la oficina?",
            "ground_truth": "Sí, el código de vestimenta es casual"
        }
    ]

    results = []
    for test in test_cases:
        eval_result = evaluate_rag(test["question"])
        eval_result["ground_truth"] = test["ground_truth"]
        results.append(eval_result)

    return results