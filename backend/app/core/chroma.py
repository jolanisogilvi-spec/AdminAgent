import logging
from typing import Dict, List, Optional

import chromadb

logger = logging.getLogger(__name__)


class ChromaService:
    def __init__(self) -> None:
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection_name = "knowledge_base"
        self.collection = None

    def connect(self) -> None:
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "knowledge base vector store"},
        )

    def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
    ) -> bool:
        if not self.collection:
            return False
        try:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}],
            )
            return True
        except Exception as exc:
            logger.error("Failed to add document %s: %s", doc_id, exc)
            return False

    def search(self, query_embedding: List[float], n_results: int = 5) -> List[Dict]:
        if not self.collection:
            return []
        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        except Exception as exc:
            logger.error("Failed to search Chroma: %s", exc)
            return []

        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for index, doc_id in enumerate(results["ids"][0]):
                formatted_results.append(
                    {
                        "id": doc_id,
                        "document": results["documents"][0][index],
                        "metadata": results["metadatas"][0][index],
                        "distance": results["distances"][0][index],
                    }
                )
        return formatted_results

    def update_document(
        self,
        doc_id: str,
        text: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        if not self.collection:
            return False
        update_params = {"ids": [doc_id]}
        if text:
            update_params["documents"] = [text]
        if embedding:
            update_params["embeddings"] = [embedding]
        if metadata:
            update_params["metadatas"] = [metadata]
        self.collection.update(**update_params)
        return True

    def delete_document(self, doc_id: str) -> bool:
        if not self.collection:
            return False
        self.collection.delete(ids=[doc_id])
        return True

    def get_collection_count(self) -> int:
        return self.collection.count() if self.collection else 0


chroma_service = ChromaService()


def get_chroma() -> ChromaService:
    return chroma_service
