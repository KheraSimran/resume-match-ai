from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title='Resume Match AI', 
              description='ATS resume analyzer powered by LangChain RAG', 
              version='1.0.0')

# Register routes under api/v1
app.include_router(router, prefix='/api/v1')

@app.get('/')
async def root():
    return {
        'message': 'Resume Match AI is running',
        'docs': '/docs'
    }
