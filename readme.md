# Onboarding Copilot 🤖

Copilot interno impulsado por IA para onboarding de empleados. Sistema RAG que responde preguntas sobre políticas, beneficios, procesos y cultura empresarial utilizando documentación interna como fuente de verdad.

## Demo

**Pregunta:** _"Trabajo hace más de 2 años, ¿cuáles son mis beneficios y horario laboral?"_

**Respuesta del Copilot:**
> Como llevas más de 2 años en TechCorp, tienes derecho a 20 días hábiles de vacaciones al año. Tus beneficios incluyen seguro de salud desde el día 1, bono de almuerzo de $5.000 CLP diarios, acceso a Udemy/Coursera y día libre en tu cumpleaños. El horario es de Lunes a Viernes, 9:00 a 18:00, con modalidad híbrida (3 presencial, 2 remoto).

## Stack Técnico

| Capa | Tecnología |
|------|-----------|
| Backend / API | Python, FastAPI, Pydantic, Uvicorn |
| LLM | OpenAI GPT-4o-mini via LangChain |
| RAG Pipeline | LangChain (document loaders, text splitters, embeddings) |
| Vector DB | Qdrant Cloud (migrado desde ChromaDB) |
| Embeddings | OpenAI text-embedding-ada-002 |
| Observabilidad | Langfuse (traces, tokens, latencia, costos) |
| Evaluación | RAGAS-style evaluation suite (faithfulness, relevancy) |
| Containerización | Docker |

## Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Cliente    │────▶│  FastAPI      │────▶│  LangChain +    │
│  (Swagger)   │◀────│  Endpoints   │◀────│  OpenAI GPT-4o  │
└─────────────┘     └──────┬───────┘     └────────┬────────┘
                           │                      │
                    ┌──────▼───────┐        ┌─────▼──────┐
                    │   Langfuse   │        │  RAG Pipeline│
                    │ Observability│        │  search_context()
                    └──────────────┘        └─────┬──────┘
                                                  │
                                           ┌──────▼───────┐
                                           │ Qdrant Cloud  │
                                           │ Vector Store   │
                                           └───────────────┘
```

## Estructura del Proyecto

```
onboarding-copilot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + endpoints principales
│   ├── config/
│   │   ├── __init__.py
│   │   └── prompt.py           # System prompt del copilot
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Schemas Pydantic (Employee, Question, ChatMessage)
│   ├── routes/
│   │   ├── chat.py             # Endpoints de chat (/chat/message, /chat/history)
│   │   └── evaluation.py       # Endpoints de evaluación (/eval/single, /eval/tests)
│   └── services/
│       ├── __init__.py
│       ├── llm.py              # Orquestación LangChain + OpenAI + Langfuse
│       ├── rag.py              # Pipeline RAG: loader → chunks → embeddings → Qdrant
│       └── evaluation.py       # Suite de evaluación con ground truth
├── docs/
│   ├── politicas.md            # Políticas internas (vacaciones, horario, beneficios)
│   └── procesos.md             # Procesos (solicitudes, onboarding, evaluaciones)
├── .env                        # Variables de entorno (no versionado)
├── .gitignore
├── .dockerignore
├── Dockerfile
├── requirements.txt
├── NOTES.md
└── README.md
```

## Pipeline RAG

El sistema implementa un pipeline RAG completo:

1. **Ingestión**: `DirectoryLoader` carga todos los `.md` de `docs/` (escalable a N documentos)
2. **Chunking**: `RecursiveCharacterTextSplitter` parte los documentos en chunks de 500 caracteres con overlap de 50
3. **Embeddings**: OpenAI genera vectores numéricos de cada chunk
4. **Indexación**: Los vectores se almacenan en Qdrant Cloud con verificación de collection existente para evitar duplicados
5. **Retrieval**: Búsqueda por similaridad semántica (`k=5` chunks más relevantes)
6. **Generación**: El contexto recuperado se inyecta en el system prompt y el LLM genera la respuesta

### Migración de Vector DB

El proyecto inició con ChromaDB (local) y fue migrado a Qdrant Cloud. Gracias a la abstracción de LangChain, la migración requirió cambiar únicamente la clase del vector store sin modificar el resto del pipeline.

## Evaluación

El sistema incluye una suite de evaluación automatizada que valida la calidad del RAG:

- **`/eval/single`**: Evalúa una pregunta individual mostrando el contexto recuperado y la respuesta
- **`/eval/tests`**: Ejecuta un conjunto de test cases con ground truth predefinido

Las métricas evaluadas incluyen:
- **Faithfulness**: ¿La respuesta es fiel al contexto proporcionado?
- **Answer Relevancy**: ¿La respuesta responde la pregunta del usuario?
- **Context Precision**: ¿Los chunks recuperados son relevantes?
- **Context Recall**: ¿Se recuperaron todos los chunks necesarios?

## Observabilidad

Cada llamada al LLM se traza automáticamente en Langfuse mediante callback de LangChain, registrando:

- Input (system prompt + contexto RAG + pregunta del usuario)
- Output (respuesta generada)
- Tokens consumidos (prompt + completion)
- Latencia de la llamada
- Costo estimado por request
- Metadata del modelo (provider, model, temperature)

## Instalación

### Opción 1: Local

```bash
# Clonar el repositorio
git clone https://github.com/FStevenson91/onboarding-copilot.git
cd onboarding-copilot

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate    # Windows
source venv/bin/activate   # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Levantar el servidor
uvicorn app.main:app --reload
```

### Opción 2: Docker

```bash
docker build -t onboarding-copilot .
docker run -p 8000:8000 -e OPENAI_API_KEY=tu-key -e QDRANT_URL=tu-url -e QDRANT_API_KEY=tu-key -e LANGFUSE_PUBLIC_KEY=tu-key -e LANGFUSE_SECRET_KEY=tu-key -e LANGFUSE_HOST=https://cloud.langfuse.com onboarding-copilot
```

### Variables de entorno requeridas

```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...cloud.qdrant.io
QDRANT_API_KEY=...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/employees` | Crear empleado (validación Pydantic) |
| POST | `/questions` | Enviar pregunta |
| POST | `/chat/message` | Enviar mensaje al copilot |
| GET | `/chat/history` | Obtener historial de chat |
| POST | `/eval/single` | Evaluar una pregunta |
| GET | `/eval/tests` | Ejecutar suite de evaluación |

Documentación interactiva disponible en: `http://localhost:8000/docs`

## Decisiones Técnicas

- **GPT-4o-mini con temperature 0.3**: Balance entre costo bajo y respuestas consistentes para un caso de uso enterprise
- **Chunk size 500 / overlap 50**: Chunks suficientemente grandes para mantener contexto, con overlap para no perder información en los cortes
- **k=5 en retrieval**: Permite responder preguntas que abarcan múltiples temas sin sobrecargar el contexto del LLM
- **Verificación de collection existente**: Evita duplicación de datos en Qdrant al reiniciar la aplicación
- **DirectoryLoader**: Escalable a N documentos sin modificar código

## Autor

**Felipe Stevenson** — AI Engineer

- GitHub: [FStevenson91](https://github.com/FStevenson91)
- LinkedIn: [Felipe Stevenson](https://linkedin.com/in/felipestevenson)