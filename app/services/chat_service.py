from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from app.configs.config import settings
from app.schemas import user_schema
from fastapi import UploadFile
import os
from sqlalchemy.orm import Session
from app.helpers import chat_helper, document_helper
from langchain.schema import HumanMessage, AIMessage
from app.utils.common_utils import clean_company_name
from app.utils.file_system_utils import save_uploaded_file
import time

# Initialize Pinecone
pinecone = PineconeClient(api_key=settings.PINECONE_API_KEY)

def get_vector_store(company: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
    cleaned_company_name = clean_company_name(company).lower()
    index_name = f"rag-app-{cleaned_company_name}"
    if index_name not in pinecone.list_indexes().names():
        pinecone.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    vector_store = PineconeVectorStore.from_existing_index(index_name, embeddings)
    return vector_store, index_name

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=settings.GOOGLE_API_KEY)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

async def chat_with_llm(query: str, company: str, session_id: str, db: Session, user: user_schema.User):
    if company:
        vector_store, _ = get_vector_store(company)
        docs = await vector_store.asimilarity_search(query)
        chain = get_conversational_chain()
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
        # The chat model expects a list of messages, so we simulate a conversation history
        chat_history_messages = []
        for i in range(0, len(past_messages) - 1, 2):
            chat_history_messages.append(HumanMessage(content=past_messages[i].split("user: ")[1]))
            chat_history_messages.append(AIMessage(content=past_messages[i+1].split("model: ")[1]))
        
        # Add the latest user query
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

    loader = UnstructuredFileLoader(saved_document.file_path)
    data = await loader.aload()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(data)

    vector_store, index_name = get_vector_store(company)
    await vector_store.aadd_texts([d.page_content for d in docs])
