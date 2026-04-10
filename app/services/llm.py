import os
from dotenv import load_dotenv
# from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config.prompt import SYSTEM_PROMPT
from app.services.rag import search_context
from langfuse.langchain import CallbackHandler

load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# En vez de OpenAI() directo, usamos ChatOpenAI de LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_chat_response(messages: list[dict]) -> str:
    context = search_context(messages[-1]["content"])

    # LangChain usa objetos de mensaje en vez de dicts
    langchain_messages = [
        SystemMessage(content=SYSTEM_PROMPT + "\n\nContexto relevante:\n" + context )
    ]

    # Convertir cada dict a objeto de LangChain
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
            
    # Langfuse callback — loguea automáticamente el input, output, tokens, latencia y costo
    langfuse_handler = CallbackHandler()
    response = llm.invoke(langchain_messages, config={"callbacks": [langfuse_handler]})
    return response.content

# ¿Ves las diferencias con la versión anterior? En vez de dicts con role/content, LangChain usa objetos tipados: SystemMessage, HumanMessage, AIMessage. Y en vez de client.chat.completions.create() usas llm.invoke(). Mismo resultado, pero ahora tienes acceso a todo el ecosistema de LangChain

# def get_chat_response(messages: list[dict]) -> str:
#     """
#     Envia mensajes al LLM y retorna la respuesta.
#     messages debe tener formato: [{"role": "user", "content": "..."}]
#     """
#     context = search_context(messages[-1]["content"])
#     all_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nContexto relevante:\n" + context}] + messages
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=all_messages,
#         temperature=0.3 # bajo para respuestas más consistentes
#     )

#     return response.choices[0].message.content