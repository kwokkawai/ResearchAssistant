"""
Vector Store Module
Handles vector embeddings and document retrieval for RAG
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available. Install with: pip install chromadb sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Install with: pip install faiss-cpu")

class VectorStore:
    """Vector database for document storage and retrieval"""

    def __init__(self, persist_directory: str = "data/vector_store",
                 embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None

        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_store()

    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model with offline support"""
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB and sentence-transformers are required for VectorStore")

        # Set local_files_only for offline mode
        model_cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        # Try to load models in order: cached primary -> cached fallback -> download primary -> download fallback
        models_to_try = [
            (self.embedding_model_name, True, "从缓存加载主模型"),
            ('all-MiniLM-L6-v2', True, "从缓存加载备用模型"),
            (self.embedding_model_name, False, "下载主模型"),
            ('all-MiniLM-L6-v2', False, "下载备用模型")
        ]
        
        last_error = None
        for model_name, local_only, description in models_to_try:
            try:
                print(f"🔄 尝试{description}: {model_name} (offline={local_only})")
                
                # Prepare kwargs for SentenceTransformer
                model_kwargs = {
                    'cache_folder': model_cache_dir,
                    'device': 'cpu'
                }
                
                # Add local_files_only if trying to load from cache
                if local_only:
                    model_kwargs['local_files_only'] = True
                
                self.embedding_model = SentenceTransformer(
                    model_name,
                    **model_kwargs
                )
                
                if local_only:
                    # Verify model loaded from cache
                    self.embedding_model.eval()
                
                self.embedding_model_name = model_name
                print(f"✅ 成功加载模型: {model_name} ({'离线模式' if local_only else '在线模式'})")
                return
                
            except Exception as e:
                last_error = e
                print(f"⚠️ 失败: {description} - {str(e)[:100]}")
                continue
        
        # If all attempts failed, raise the last error
        raise Exception(f"❌ 无法加载任何嵌入模型。最后错误: {last_error}\n\n"
                       f"解决方案:\n"
                       f"1. 连接网络后首次运行以下载模型\n"
                       f"2. 或手动下载模型到: {model_cache_dir}\n"
                       f"3. 或使用简化版RAG（不需要向量存储）")

    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get collection
            collection_name = "documents"
            try:
                self.collection = self.chroma_client.get_collection(name=collection_name)
                print(f"Loaded existing collection: {collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"Created new collection: {collection_name}")

        except Exception as e:
            raise Exception(f"Failed to initialize vector store: {e}")

    def add_document(self, document: Dict[str, Any]) -> bool:
        """Add a document to the vector store"""
        try:
            doc_id = document['id']
            chunks = document.get('chunks', [])

            if not chunks:
                print(f"Warning: No chunks found for document {doc_id}")
                return False

            # Generate embeddings for chunks
            embeddings = []
            chunk_texts = []
            metadata_list = []
            ids = []

            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist()
                embeddings.append(embedding)

                chunk_texts.append(chunk)
                ids.append(f"{doc_id}_chunk_{i}")

                # Create metadata for the chunk
                metadata = {
                    'document_id': doc_id,
                    'filename': document.get('filename', ''),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'format': document.get('format', ''),
                    'created_at': document.get('created_at', ''),
                    'modified_at': document.get('modified_at', '')
                }
                metadata_list.append(metadata)

            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadata_list,
                ids=ids
            )

            print(f"Added document {doc_id} with {len(chunks)} chunks")
            return True

        except Exception as e:
            print(f"Error adding document {document.get('id', 'unknown')}: {e}")
            return False

    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Add multiple documents to the vector store"""
        success_count = 0
        total_count = len(documents)

        for document in documents:
            if self.add_document(document):
                success_count += 1

        return {
            'total': total_count,
            'successful': success_count,
            'failed': total_count - success_count
        }

    def search(self, query: str, top_k: int = 5, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant document chunks"""
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepare search parameters
            search_params = {
                'query_embeddings': [query_embedding],
                'n_results': top_k,
                'include': ['documents', 'metadatas', 'distances']
            }

            # Filter by document IDs if specified
            if document_ids:
                search_params['where'] = {
                    'document_id': {'$in': document_ids}
                }

            # Search the collection
            results = self.collection.query(**search_params)

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'chunk': doc,
                        'metadata': metadata,
                        'similarity': 1 - distance,  # Convert cosine distance to similarity
                        'rank': i + 1
                    })

            return formatted_results

        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={'document_id': document_id},
                include=['documents', 'metadatas']
            )

            chunks = []
            if results['documents']:
                for doc, metadata in zip(results['documents'], results['metadatas']):
                    chunks.append({
                        'chunk': doc,
                        'metadata': metadata
                    })

            # Sort by chunk index
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            return chunks

        except Exception as e:
            print(f"Error getting document chunks: {e}")
            return []

    def remove_document(self, document_id: str) -> bool:
        """Remove a document from the vector store"""
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={'document_id': document_id},
                include=['metadatas']
            )

            if results['ids']:
                # Delete all chunks
                self.collection.delete(ids=results['ids'])
                print(f"Removed document {document_id} with {len(results['ids'])} chunks")
                return True
            else:
                print(f"Document {document_id} not found")
                return False

        except Exception as e:
            print(f"Error removing document {document_id}: {e}")
            return False

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the store"""
        try:
            # Get all unique document IDs
            results = self.collection.get(include=['metadatas'])

            document_info = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('document_id')
                if doc_id and doc_id not in document_info:
                    document_info[doc_id] = {
                        'id': doc_id,
                        'filename': metadata.get('filename', ''),
                        'format': metadata.get('format', ''),
                        'created_at': metadata.get('created_at', ''),
                        'modified_at': metadata.get('modified_at', ''),
                        'chunk_count': 0
                    }

                if doc_id in document_info:
                    document_info[doc_id]['chunk_count'] += 1

            return list(document_info.values())

        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            documents = self.list_documents()
            total_chunks = sum(doc['chunk_count'] for doc in documents)

            return {
                'total_documents': len(documents),
                'total_chunks': total_chunks,
                'embedding_model': self.embedding_model_name,
                'collection_name': self.collection.name if self.collection else 'unknown'
            }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def clear_all(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            # Delete the entire collection and recreate it
            collection_name = self.collection.name
            self.chroma_client.delete_collection(name=collection_name)

            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            print("Cleared all documents from vector store")
            return True

        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return False
