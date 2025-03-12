# %%
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
# %%
# %%

# Load PDF
pdf_path = "/home/ajai-krishna/Downloads/combinepdf-1.pdf"  # Update with your file path
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# %%
# %%
# Split into Chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs = splitter.split_documents(documents)

# %%
# %%
try:
    import faiss  # Ensure FAISS is available
    embed_model = OllamaEmbeddings(model="mxbai-embed-large")

    # If FAISS index exists, load it instead of recomputing
    try:
        vector_db = FAISS.load_local("faiss_index", embed_model)
        print("FAISS index loaded from storage.")
    except:
        print("FAISS index not found. Creating a new one...")
        vector_db = FAISS.from_documents(docs, embed_model)
        vector_db.save_local("faiss_index")  # Save for future use

except ImportError:
    raise ImportError("FAISS is not installed. Please install using `pip install faiss-cpu` or `faiss-gpu`.")


# %%
# %%
# Step 4: Initialize LLM
llm = OllamaLLM(model="llama2")

# Step 5: Set Up Retrieval
retriever = vector_db.as_retriever(search_kwargs={"k": 5})
# %%
# Custom Prompt
prompt_template = """You are a climate AI assistant specializing in India's future climate.
Your responses are based on the climate report *"Navigating India’s Future Climate"* published by Azim Premji University, 
along with insights from the *IPCC Technical Summary* and *IPCC Frequently Asked Questions (FAQs)*.

Use the retrieved information from these sources to provide accurate, evidence-based, and concise responses.
If relevant data is unavailable in these references, acknowledge it instead of speculating.

Query: {question}

Context: {context}

Answer:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["question", "context"])

# %%
# %%
# Build RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)

# Query Example
query = "Tell me about azim premji university"
response = qa_chain.invoke({"query": query})

# Output Response
print(response["result"])

# %%