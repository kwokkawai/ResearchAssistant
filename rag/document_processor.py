"""
Document Processor Module
Handles loading and processing of various document formats for RAG
"""

import os
import json
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
from pathlib import Path

class DocumentProcessor:
    """Handles processing of various document formats"""

    SUPPORTED_FORMATS = {
        '.pdf': 'PDF',
        '.docx': 'Word Document',
        '.doc': 'Word Document',
        '.md': 'Markdown',
        '.markdown': 'Markdown',
        '.txt': 'Text',
        '.json': 'JSON',
        '.html': 'HTML',
        '.htm': 'HTML'
    }

    def __init__(self, documents_dir: str = "documents"):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(exist_ok=True)

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Load and process a document from file path"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        file_extension = file_path.suffix.lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Generate document ID based on file path and content
        content = self._read_file_content(file_path)
        doc_id = self._generate_document_id(file_path, content)

        # Extract text content
        text_content = self._extract_text_content(file_path, content)

        # Create document metadata
        document = {
            'id': doc_id,
            'filename': file_path.name,
            'filepath': str(file_path),
            'format': self.SUPPORTED_FORMATS[file_extension],
            'size': file_path.stat().st_size,
            'created_at': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'content': text_content,
            'chunks': self._chunk_text(text_content)
        }

        return document

    def load_documents_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Load all supported documents from a directory"""
        directory = Path(directory_path).resolve()  # 解析绝对路径
        documents = []
        found_files = []

        print(f"Loading documents from directory: {directory}")

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # 首先列出目录内容进行调试
        try:
            all_files = list(directory.rglob('*'))
            print(f"Found {len(all_files)} total files/directories in {directory}")
        except PermissionError as e:
            raise PermissionError(f"No permission to access directory {directory}: {e}")

        # 查找支持的文件
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                found_files.append(str(file_path))
                if file_ext in self.SUPPORTED_FORMATS:
                    print(f"Processing supported file: {file_path} (format: {self.SUPPORTED_FORMATS[file_ext]})")
                    try:
                        document = self.load_document(str(file_path))
                        documents.append(document)
                        print(f"Successfully loaded document: {file_path.name}")
                    except Exception as e:
                        print(f"Error loading document {file_path}: {e}")
                        continue
                else:
                    print(f"Skipping unsupported file: {file_path} (format: {file_ext})")

        print(f"Directory scan complete. Found {len(found_files)} files, loaded {len(documents)} documents.")
        print(f"Supported formats: {list(self.SUPPORTED_FORMATS.keys())}")

        return documents

    def _read_file_content(self, file_path: Path) -> bytes:
        """Read raw file content"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    def _extract_text_content(self, file_path: Path, content: bytes) -> str:
        """Extract text content from various file formats"""
        file_extension = file_path.suffix.lower()

        if file_extension in ['.txt', '.md', '.markdown']:
            return content.decode('utf-8', errors='ignore')

        elif file_extension == '.json':
            try:
                data = json.loads(content.decode('utf-8'))
                # Convert JSON to readable text
                return self._json_to_text(data)
            except:
                return content.decode('utf-8', errors='ignore')

        elif file_extension in ['.html', '.htm']:
            return self._extract_text_from_html(content)

        elif file_extension == '.pdf':
            return self._extract_text_from_pdf(content)

        elif file_extension in ['.docx', '.doc']:
            return self._extract_text_from_word(content, file_extension)

        else:
            # Fallback to text decoding
            return content.decode('utf-8', errors='ignore')

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF files"""
        try:
            # Try to import PyPDF2 or pdfplumber if available
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(content)) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    raise ImportError("PDF processing requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2 or pip install pdfplumber")
        except Exception as e:
            print(f"Warning: Failed to extract text from PDF: {e}")
            return "PDF content could not be extracted. Please install PyPDF2 or pdfplumber."

    def _extract_text_from_word(self, content: bytes, extension: str) -> str:
        """Extract text from Word documents"""
        try:
            if extension == '.docx':
                try:
                    from docx import Document
                    doc = Document(io.BytesIO(content))
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    raise ImportError("DOCX processing requires python-docx. Install with: pip install python-docx")
            else:
                # For .doc files, we can't easily extract text without additional libraries
                raise ImportError("DOC file processing requires additional libraries. Please convert to DOCX format.")
        except Exception as e:
            print(f"Warning: Failed to extract text from Word document: {e}")
            return "Word document content could not be extracted. Please install python-docx."

    def _extract_text_from_html(self, content: bytes) -> str:
        """Extract text from HTML files"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content.decode('utf-8', errors='ignore'), 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except ImportError:
            print("Warning: HTML processing requires beautifulsoup4. Install with: pip install beautifulsoup4")
            return content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Warning: Failed to extract text from HTML: {e}")
            return content.decode('utf-8', errors='ignore')

    def _json_to_text(self, data: Any, indent: int = 0) -> str:
        """Convert JSON data to readable text"""
        text = ""

        if isinstance(data, dict):
            for key, value in data.items():
                text += "  " * indent + f"{key}: "
                if isinstance(value, (dict, list)):
                    text += "\n" + self._json_to_text(value, indent + 1)
                else:
                    text += str(value) + "\n"
        elif isinstance(data, list):
            for i, item in enumerate(data):
                text += "  " * indent + f"[{i}]: "
                if isinstance(item, (dict, list)):
                    text += "\n" + self._json_to_text(item, indent + 1)
                else:
                    text += str(item) + "\n"
        else:
            text += "  " * indent + str(data) + "\n"

        return text

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks for better retrieval"""
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If we're not at the end, try to find a good breaking point
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', end - 100, end)
                last_newline = text.rfind('\n', end - 100, end)

                # Use the latest sentence ending found
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1

            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, end - overlap)

        return chunks

    def _generate_document_id(self, file_path: Path, content: bytes) -> str:
        """Generate a unique document ID based on file path and content"""
        # Create a hash from file path and content
        hash_input = str(file_path) + content.decode('utf-8', errors='ignore')
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]

    def get_supported_formats(self) -> Dict[str, str]:
        """Get list of supported file formats"""
        return self.SUPPORTED_FORMATS.copy()

    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate if a file can be processed"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, "File does not exist"

            if not file_path.is_file():
                return False, "Path is not a file"

            file_extension = file_path.suffix.lower()
            if file_extension not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported file format: {file_extension}"

            # Try to read the file
            content = self._read_file_content(file_path)
            if len(content) == 0:
                return False, "File is empty"

            return True, "File is valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
