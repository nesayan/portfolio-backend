import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from api.schemas import EmbeddingResponse


class EmbeddingService:
    embedding_model: HuggingFaceEmbeddings = HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL"),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
        show_progress=False,
    )

    @staticmethod
    async def aload_documents(document_folder: Path, perform_chunk: bool = True, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
        '''Asynchronously loads documents from a specified folder, with optional chunking.
        Args:
            document_folder: Path to the directory containing PDF files.
        Returns:
            A list of embedding vectors, one per text chunk.
        Raises:
            ValueError: If no documents are found in the folder.
        
        '''

        loader = DirectoryLoader(str(document_folder))
        documents = await loader.aload()

        if not documents:
            raise ValueError(f"No documents found in folder: {document_folder}")

        if perform_chunk and chunk_size and chunk_overlap:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            documents = text_splitter.split_documents(documents)
        return documents
    
    @staticmethod
    def load_documents(document_folder: Path, perform_chunk: bool = True, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
        '''Synchronously loads documents from a specified folder, with optional chunking.
        Args:
            document_folder: Path to the directory containing PDF files.
        Returns:
            A list of embedding vectors, one per text chunk.
        Raises:
            ValueError: If no documents are found in the folder.
        '''

        loader = DirectoryLoader(str(document_folder))
        documents = loader.load()

        if not documents:
            raise ValueError(f"No documents found in folder: {document_folder}")

        if perform_chunk and chunk_size and chunk_overlap:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            documents = text_splitter.split_documents(documents)
        return documents

    @staticmethod
    async def aembed(document_folder: Path, perform_chunk: bool = True, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[EmbeddingResponse]:
        '''Asynchronously loads and generates embeddings for documents in a specified folder, with optional chunking.'''

        documents = await EmbeddingService.aload_documents(document_folder, perform_chunk=perform_chunk, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        texts = [doc.page_content for doc in documents]
        embeddings = await EmbeddingService.embedding_model.aembed_documents(texts)

        return [EmbeddingResponse(embedding=e) for e in embeddings]
    
    @staticmethod
    def embed(document_folder: Path, perform_chunk: bool = True, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[EmbeddingResponse]:
        '''Synchronously loads and generates embeddings for documents in a specified folder, with optional chunking.'''

        documents = EmbeddingService.load_documents(document_folder, perform_chunk=perform_chunk, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        texts = [doc.page_content for doc in documents]
        embeddings = EmbeddingService.embedding_model.embed_documents(texts)

        return [EmbeddingResponse(embedding=e) for e in embeddings]