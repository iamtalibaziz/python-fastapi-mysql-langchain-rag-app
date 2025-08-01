from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from app.configs.config import settings
from app.schemas import user_schema
from fastapi import UploadFile, status
import os
from sqlalchemy.orm import Session
from app.helpers import chat_helper, document_helper
from langchain.schema import HumanMessage, AIMessage
from app.utils.common_utils import clean_company_name
from app.utils.file_system_utils import save_uploaded_file, save_downloaded_file
import time
import httpx
from app.helpers.exceptions import CustomException
from app.utils.logger import logger

# Initialize Pinecone
pinecone = PineconeClient(api_key=settings.PINECONE_API_KEY)

def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME
    if index_name not in pinecone.list_indexes().names():
        pinecone.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION)
        )
    
    vector_store = PineconeVectorStore.from_existing_index(index_name, embeddings)
    return vector_store, index_name

async def chat_with_llm(query: str, company: str, session_id: str, db: Session, user: user_schema.User):
    logger.info(f"chat_with_llm:company: {company}")
    effective_company = company
    if not effective_company and session_id:
        chat_session = chat_helper.get_chat_session_by_session_id_and_user(db, session_id, user.id)
        if chat_session and chat_session.company_name:
            effective_company = chat_session.company_name

    logger.info(f"chat_with_llm:effective_company: {effective_company}")
    if effective_company:
        vector_store, _ = get_vector_store()
        cleaned_company_name = clean_company_name(effective_company).lower()
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 3, "namespace": cleaned_company_name})
        docs = await retriever.aget_relevant_documents(query)
        if not docs:
            response_text = "I could not find any documents related to your query."
        else:
            prompt_template = """
            You are a helpful assistant. Your task is to answer the question strictly based on the provided context.
            If the answer is not present in the context, reply with: "The answer is not available in the context."

            Context:
            {context}

            Question:
            {question}

            Answer:
            """
            model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=settings.GOOGLE_API_KEY)
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
            response = await chain.ainvoke({"input_documents": docs, "question": query}, return_only_outputs=True)
            response_text = response["output_text"]
    else:
        history = chat_helper.get_chat_history(db, session_id)
        past_messages = []
        for message in history:
            past_messages.append(f"user: {message.query}")
            past_messages.append(f"model: {message.response}")
            
        past_messages.append(f"user: {query}")

        model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=settings.GOOGLE_API_KEY)
        chat_history_messages = []
        for i in range(0, len(past_messages) - 1, 2):
            chat_history_messages.append(HumanMessage(content=past_messages[i].split("user: ")[1]))
            chat_history_messages.append(AIMessage(content=past_messages[i+1].split("model: ")[1]))
        
        chat_history_messages.append(HumanMessage(content=query))

        response = await model.ainvoke(chat_history_messages)
        response_text = response.content
        
    chat_history = chat_helper.save_chat_history(db, user, session_id, company, query, response_text)
    return chat_history

async def process_and_store_document(document: UploadFile, company: str, db: Session, user: user_schema.User):
    cleaned_name = clean_company_name(company)
    _, file_extension = os.path.splitext(document.filename)
    unique_filename = f"{cleaned_name}_{int(time.time())}{file_extension}"
    file_path = os.path.join("storage", unique_filename)

    save_uploaded_file(document, file_path)

    saved_document = document_helper.save_document_to_db(
        db=db,
        user=user,
        company=company,
        file_name=unique_filename,
        file_path=file_path,
        file_type=document.content_type,
        file_size=document.size
    )

    if file_extension.lower() == ".pdf":
        loader = PyPDFLoader(saved_document.file_path)
    else:
        loader = UnstructuredFileLoader(saved_document.file_path)
        
    data = await loader.aload()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(data)

    vector_store, _ = get_vector_store()
    cleaned_company_name = clean_company_name(company).lower()
    await vector_store.aadd_texts([d.page_content for d in docs], namespace=cleaned_company_name)

def get_chat_sessions(db: Session, user: user_schema.User):
    return chat_helper.get_chat_sessions_by_user(db, user.id)

def get_chat_history_by_session(db: Session, session_id: str, user: user_schema.User):
    chat_session = chat_helper.get_chat_session_by_session_id_and_user(db, session_id, user.id)
    if not chat_session:
        return []
    return chat_helper.get_chat_history(db, session_id)

async def process_and_store_document_from_url(document_url: str, company: str, db: Session, user: user_schema.User):
    async with httpx.AsyncClient() as client:
        response = await client.get(document_url)
        response.raise_for_status()

    file_name = document_url.split("/")[-1]
    _, file_extension = os.path.splitext(file_name)
    
    allowed_extensions = {".pdf", ".docx"}
    if file_extension.lower() not in allowed_extensions:
        raise CustomException(message="Only .pdf and .docx files are allowed", status_code=status.HTTP_400_BAD_REQUEST)

    cleaned_name = clean_company_name(company)
    unique_filename = f"{cleaned_name}_{int(time.time())}{file_extension}"
    file_path = os.path.join("storage", unique_filename)
    
    save_downloaded_file(response.content, file_path)

    saved_document = document_helper.save_document_to_db(
        db=db,
        user=user,
        company=company,
        file_name=unique_filename,
        file_path=file_path,
        file_type=response.headers['content-type'],
        file_size=len(response.content)
    )

    if file_extension.lower() == ".pdf":
        loader = PyPDFLoader(saved_document.file_path)
    else:
        loader = UnstructuredFileLoader(saved_document.file_path)
        
    data = await loader.aload()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(data)

    vector_store, _ = get_vector_store()
    cleaned_company_name = clean_company_name(company).lower()
    await vector_store.aadd_texts([d.page_content for d in docs], namespace=cleaned_company_name)
