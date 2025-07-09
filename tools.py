# tools.py

from agents import function_tool
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex, ServiceContext, StorageContext
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

import faiss
import os

@function_tool
def local_file_search(query: str, max_results: int = 3) -> str:
    """
    FAISS (vektör) + BM25 (kelime) hybrid arama yapar.
    """
    # Belgeleri yükle
    documents = SimpleDirectoryReader("documents/json").load_data()

    # Embedding modeli (Open Source)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # FAISS index oluştur
    faiss_index = faiss.IndexFlatL2(embed_model.embedding_size)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        storage_context=storage_context,
        show_progress=False,
    )
    vector_retriever = vector_index.as_retriever(similarity_top_k=max_results)

    # BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(documents, similarity_top_k=max_results)

    # Fusion Retriever
    retriever = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )

    # Sorguyu çalıştır
    query_engine = RetrieverQueryEngine.from_args(retriever)
    response = query_engine.query(query)

    return str(response)
