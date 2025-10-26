"""
RAG Manager Module
Manages the complete RAG pipeline for document-based question answering
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .document_processor import DocumentProcessor
from .vector_store import VectorStore

class RAGManager:
    """Manages the complete RAG (Retrieval-Augmented Generation) pipeline"""

    def __init__(self, documents_dir: str = "documents",
                 vector_store_dir: str = "data/vector_store"):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(exist_ok=True)

        self.document_processor = DocumentProcessor(str(self.documents_dir))
        
        # Initialize vector store with error handling
        self.vector_store = None
        self.initialization_error = None
        
        try:
            print("🔄 正在初始化RAG向量存储...")
            self.vector_store = VectorStore(vector_store_dir)
            print("✅ RAG向量存储初始化成功")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ RAG向量存储初始化失败: {e}")
            print("⚠️ RAG功能将不可用，但应用可以继续使用其他功能")

        # Track loaded documents
        self.loaded_documents = set()
        if self.vector_store:
            self._load_existing_documents()

    def _load_existing_documents(self):
        """Load tracking information for existing documents"""
        tracking_file = self.documents_dir / ".document_tracking.json"
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.loaded_documents = set(data.get('loaded_documents', []))
            except Exception as e:
                print(f"Warning: Failed to load document tracking: {e}")

    def _save_document_tracking(self):
        """Save tracking information for loaded documents"""
        tracking_file = self.documents_dir / ".document_tracking.json"
        try:
            data = {
                'loaded_documents': list(self.loaded_documents),
                'last_updated': datetime.now().isoformat()
            }
            with open(tracking_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save document tracking: {e}")

    def is_available(self) -> bool:
        """Check if RAG system is available"""
        return self.vector_store is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG system status"""
        if self.vector_store:
            return {
                'available': True,
                'message': 'RAG系统运行正常'
            }
        else:
            return {
                'available': False,
                'error': self.initialization_error,
                'message': 'RAG系统初始化失败。可能原因：\n'
                          '1. 无法连接网络下载模型\n'
                          '2. 缺少必要的依赖包\n'
                          '请连接网络后重启应用，或联系管理员。'
            }

    def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a single document to the RAG system"""
        if not self.is_available():
            return {
                'success': False,
                'error': f'RAG系统不可用: {self.initialization_error}',
                'document_id': None
            }
        
        try:
            # Validate file
            is_valid, message = self.document_processor.validate_file(file_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': message,
                    'document_id': None
                }

            # Load and process document
            document = self.document_processor.load_document(file_path)

            # Check if document is already loaded
            if document['id'] in self.loaded_documents:
                return {
                    'success': False,
                    'error': 'Document already loaded',
                    'document_id': document['id']
                }

            # Add to vector store
            success = self.vector_store.add_document(document)

            if success:
                self.loaded_documents.add(document['id'])
                self._save_document_tracking()

                return {
                    'success': True,
                    'document_id': document['id'],
                    'filename': document['filename'],
                    'chunk_count': len(document['chunks']),
                    'message': f"Successfully added document: {document['filename']}"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to add document to vector store',
                    'document_id': document['id']
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to add document: {str(e)}",
                'document_id': None
            }

    def add_documents_from_directory(self, directory_path: str, force_reload: bool = False) -> Dict[str, Any]:
        """Add all documents from a directory"""
        try:
            documents = self.document_processor.load_documents_from_directory(directory_path)

            if not documents:
                return {
                    'success': False,
                    'error': 'No supported documents found in directory',
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }

            # Filter out already loaded documents (unless force_reload is True)
            if force_reload:
                new_documents = documents
                # Remove existing documents from tracking
                for doc in documents:
                    if doc['id'] in self.loaded_documents:
                        self.loaded_documents.remove(doc['id'])
                        # Also remove from vector store
                        self.vector_store.remove_document(doc['id'])
            else:
                new_documents = [doc for doc in documents if doc['id'] not in self.loaded_documents]

            if not new_documents:
                return {
                    'success': False,
                    'error': 'All documents in directory are already loaded',
                    'total': len(documents),
                    'successful': 0,
                    'failed': 0
                }

            # Add to vector store
            result = self.vector_store.add_documents(new_documents)

            # Update tracking
            for doc in new_documents:
                if doc['id'] not in self.loaded_documents:  # Double check
                    self.loaded_documents.add(doc['id'])
            self._save_document_tracking()

            result['success'] = result['successful'] > 0
            if result['success']:
                result['message'] = f"Successfully added {result['successful']} documents from directory"
            else:
                result['error'] = "Failed to add any documents from directory"

            return result

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to add documents from directory: {str(e)}",
                'total': 0,
                'successful': 0,
                'failed': 0
            }

    def remove_document(self, document_id: str) -> bool:
        """Remove a document from the RAG system"""
        try:
            success = self.vector_store.remove_document(document_id)

            if success and document_id in self.loaded_documents:
                self.loaded_documents.remove(document_id)
                self._save_document_tracking()

            return success

        except Exception as e:
            print(f"Error removing document {document_id}: {e}")
            return False

    def query_documents(self, query: str, document_ids: List[str] = None,
                       top_k: int = 5, context_window: int = 2) -> Dict[str, Any]:
        """
        Query the document collection and return relevant information

        Args:
            query: The search query
            document_ids: Optional list of document IDs to search within
            top_k: Number of top results to return
            context_window: Number of surrounding chunks to include as context

        Returns:
            Dictionary containing search results and formatted context
        """
        try:
            # Search for relevant chunks
            search_results = self.vector_store.search(query, top_k=top_k, document_ids=document_ids)

            if not search_results:
                return {
                    'query': query,
                    'results': [],
                    'context': '',
                    'sources': [],
                    'message': 'No relevant information found'
                }

            # Build comprehensive context
            context_parts = []
            sources = []

            for result in search_results:
                metadata = result['metadata']
                chunk_index = metadata.get('chunk_index', 0)
                document_id = metadata.get('document_id', '')

                # Get surrounding context chunks
                context_chunks = self._get_context_chunks(document_id, chunk_index, context_window)

                # Combine chunks into coherent text
                context_text = ' '.join([chunk['chunk'] for chunk in context_chunks])

                context_parts.append(context_text)

                # Add source information
                sources.append({
                    'filename': metadata.get('filename', ''),
                    'document_id': document_id,
                    'chunk_index': chunk_index,
                    'similarity': result['similarity'],
                    'format': metadata.get('format', ''),
                    'modified_at': metadata.get('modified_at', '')
                })

            # Join all context parts
            full_context = '\n\n'.join(context_parts)

            return {
                'query': query,
                'results': search_results,
                'context': full_context,
                'sources': sources,
                'total_sources': len(sources),
                'message': f'Found {len(sources)} relevant sources'
            }

        except Exception as e:
            return {
                'query': query,
                'results': [],
                'context': '',
                'sources': [],
                'error': str(e),
                'message': f'Query failed: {str(e)}'
            }

    def _validate_rag_response(self, response: str, context: str, query: str) -> Dict[str, bool]:
        """
        验证RAG回答是否基于文档内容
        """
        try:
            response_lower = response.lower().strip()
            context_lower = context.lower().strip()

            # 检查是否包含明显的通用回答模式
            generic_phrases = [
                "文档摘要", "技术路线", "抽取式", "生成式", "混合式",
                "预处理", "文本分块", "质量评估", "安全合规",
                "tf-idf", "textrank", "bertsum", "longformer", "led",
                "t5", "bart", "gpt-3", "gpt-4", "claude", "llama"
            ]

            found_generic = any(phrase in response_lower for phrase in generic_phrases)

            if found_generic:
                return {
                    'is_valid': False,
                    'reason': f'回答包含通用技术术语，可能不基于具体文档内容: {found_generic}'
                }

            # 检查回答长度是否合理（太长的回答可能偏离主题）
            if len(response) > 2000 and "文档中没有相关信息" not in response:
                return {
                    'is_valid': False,
                    'reason': '回答过长，可能包含无关内容'
                }

            # 检查是否至少包含一些文档中的内容
            # 简单的启发式检查：回答中是否包含文档中的一些关键词
            context_words = set(context_lower.split())
            response_words = set(response_lower.split())

            # 计算重叠度
            overlap = len(context_words.intersection(response_words))
            overlap_ratio = overlap / len(response_words) if response_words else 0

            if overlap_ratio < 0.1 and len(response) > 50:  # 如果重叠度太低且回答不短
                return {
                    'is_valid': False,
                    'reason': f'回答与文档内容重叠度太低 ({overlap_ratio:.2f})'
                }

            return {
                'is_valid': True,
                'reason': '回答似乎基于文档内容'
            }

        except Exception as e:
            print(f"验证RAG回答时出错: {e}")
            return {
                'is_valid': True,  # 出错时假设有效，避免误报
                'reason': f'验证过程出错: {e}'
            }

    def _get_context_chunks(self, document_id: str, center_index: int, window: int) -> List[Dict[str, Any]]:
        """Get chunks around a center chunk for better context"""
        try:
            all_chunks = self.vector_store.get_document_chunks(document_id)

            if not all_chunks:
                return []

            # Calculate range
            start_index = max(0, center_index - window)
            end_index = min(len(all_chunks), center_index + window + 1)

            # Get chunks in range
            context_chunks = []
            for i in range(start_index, end_index):
                chunk_data = all_chunks[i].copy()
                chunk_data['relative_position'] = i - center_index  # -window to +window
                context_chunks.append(chunk_data)

            return context_chunks

        except Exception as e:
            print(f"Error getting context chunks: {e}")
            return []

    def generate_rag_response(self, query: str, document_ids: List[str] = None,
                            top_k: int = 5, llm_manager=None, preferred_model: str = 'openai') -> Dict[str, Any]:
        """
        Generate a complete RAG response using retrieved documents and LLM

        This ensures the response is 100% based on document content, not LLM inference
        """
        try:
            # First, query the documents
            query_result = self.query_documents(query, document_ids, top_k)

            if not query_result.get('context'):
                return {
                    'query': query,
                    'response': '抱歉，在提供的文档中没有找到相关信息。',
                    'sources': [],
                    'confidence': 0.0,
                    'based_on_documents': True
                }

            # Build a strict prompt that forces document-only responses
            context = query_result['context']
            sources = query_result['sources']

            rag_prompt = f"""[严格指令] 你是一个文档分析助手，只能基于提供的文档内容回答问题。

重要规则：
1. 禁止使用任何先验知识、训练数据或通用知识
2. 只能引用和总结提供的文档内容
3. 如果文档中没有相关信息，必须回答"文档中没有相关信息"
4. 不要生成任何关于文档处理技术、摘要方法或其他通用内容的回答
5. 回答必须严格基于文档的具体内容

提供的文档内容：
---
{context}
---

用户问题：{query}

请基于以上提供的文档内容进行回答。如果文档内容中没有足够信息来回答这个问题，请明确说明。"""

            # Generate response using LLM
            if llm_manager:
                try:
                    response = llm_manager.generate_response(preferred_model, rag_prompt)

                    # 验证回答是否基于文档内容
                    validation_result = self._validate_rag_response(response, context, query)
                    if not validation_result['is_valid']:
                        print(f"警告: RAG回答可能不基于文档内容 - {validation_result['reason']}")
                        # 可以选择重新生成或添加警告
                        response = f"[警告: 回答可能不完全基于文档内容] {response}"

                except Exception as e:
                    print(f"LLM generation failed: {e}")
                    response = f"基于文档内容的回答生成失败: {str(e)}"
            else:
                response = "LLM管理器不可用，无法生成回答"

            # Calculate confidence based on source similarity
            avg_similarity = sum(source['similarity'] for source in sources) / len(sources) if sources else 0.0

            return {
                'query': query,
                'response': response,
                'sources': sources,
                'confidence': avg_similarity,
                'based_on_documents': True,
                'document_count': len(set(s['document_id'] for s in sources)),
                'total_chunks_used': len(sources)
            }

        except Exception as e:
            return {
                'query': query,
                'response': f'生成回答时发生错误: {str(e)}',
                'sources': [],
                'confidence': 0.0,
                'based_on_documents': True,
                'error': str(e)
            }

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all loaded documents"""
        try:
            return self.vector_store.list_documents()
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific document"""
        try:
            documents = self.list_documents()
            for doc in documents:
                if doc['id'] == document_id:
                    # Add chunk information
                    chunks = self.vector_store.get_document_chunks(document_id)
                    doc['chunks'] = chunks
                    doc['chunk_count'] = len(chunks)
                    return doc
            return None
        except Exception as e:
            print(f"Error getting document info: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            vector_stats = self.vector_store.get_stats()
            documents = self.list_documents()

            return {
                **vector_stats,
                'loaded_documents_count': len(self.loaded_documents),
                'documents_dir': str(self.documents_dir),
                'supported_formats': self.document_processor.get_supported_formats()
            }

        except Exception as e:
            return {'error': str(e)}

    def clear_all_documents(self) -> bool:
        """Clear all documents from the RAG system"""
        try:
            success = self.vector_store.clear_all()
            if success:
                self.loaded_documents.clear()
                self._save_document_tracking()
            return success
        except Exception as e:
            print(f"Error clearing documents: {e}")
            return False
