from langchain_community.vectorstores import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from pinecone import Pinecone as PineconeClient
from app.configs.config import settings
from app.schemas import user_schema
from fastapi import UploadFile
import os
from sqlalchemy.orm import Session
from app.helpers.chat_helper import save_chat_history, get_chat_history
from app.helpers.document_helper import save_document
from langchain.schema import HumanMessage, AIMessage

# Initialize Pinecone
pinecone = PineconeClient(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_API_ENV)

def get_vector_store(company: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-1.5-pro", google_api_key=settings.GOOGLE_API_KEY)
    index_name = f"rag-app-{company.lower().replace(' ', '-')}"
    if index_name not in pinecone.list_indexes().names():
        pinecone.create_index(name=index_name, dimension=768)
    vector_store = Pinecone.from_existing_index(index_name, embeddings)
    return vector_store, index_name

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=settings.GOOGLE_API_KEY)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def chat_with_llm(query: str, company: str, session_id: str, db: Session, user: user_schema.User):
    if company:
        vector_store, _ = get_vector_store(company)
        docs = vector_store.similarity_search(query)
        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
        response_text = response["output_text"]
    else:
        history = get_chat_history(db, session_id)
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

        response = model.invoke(chat_history_messages)
        response_text = response.content
        
    chat_history = save_chat_history(db, user, session_id, company, query, response_text)
    return chat_history

def process_and_store_document(document: UploadFile, company: str, db: Session, user: user_schema.User):
    saved_document = save_document(db, user, company, document)
    loader = UnstructuredFileLoader(saved_document.file_path)
    pages = loader.load_and_split()
    vector_store, index_name = get_vector_store(company)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
    Pinecone.from_texts([p.page_content for p in pages], embeddings, index_name=index_name)
