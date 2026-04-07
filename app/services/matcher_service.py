from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import chromadb
from app.core.config import settings
from app.models.analysis import ResumeAnalysis
from langsmith import Client
from app.core.logger import get_logger

logger = get_logger(__name__)

def get_chroma_client():
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port
    )

def build_vector_store(chunks: list, collection_name: str) -> Chroma:
    """
    Builds a Chroma vector store from a list of document chunks.

    Args:
        chunks (list): A list of document chunks to build the vector store from.
        collection_name (str): The name of the Chroma collection to create.

    Returns:
        Chroma: The built Chroma vector store.
    """
    logger.info('Building vector store from documents')
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        client=get_chroma_client(),
        collection_name=collection_name)
    return vector_store

def resume_jd_match(resume_chunks: list, job_description: str, collection_name: str = 'resume_analysis') -> dict:
    """
    Matches a resume to a job description using a LangChain AI.

    Args:
        resume_chunks (list): A list of document chunks representing the resume.
        job_description (str): The job description to match the resume to.
        collection_name (str): The name of the Chroma collection to create.

    Returns:
        dict: The AI response containing the analysis result.
    """
    logger.info('Matching resume to job description...')

    vector_store = build_vector_store(resume_chunks, collection_name=collection_name)
    
    retriever = vector_store.as_retriever(search_kwargs={'k': 5})

    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
    structured_llm = llm.with_structured_output(ResumeAnalysis)
    client = Client()
    prompt = client.pull_prompt('resume-analysis-prompt')

    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])
    
    analysis_chain = (
        {
            'context': retriever | format_docs,
            'job_description': RunnablePassthrough(),
        }
        | prompt
        | structured_llm
    )

    try:
        response = analysis_chain.invoke(job_description)
        logger.info('Successfully matched resume to description. AI output: ', response)
        return response
    except Exception as e:
        logger.error('Error invoking analysis chain', e)
