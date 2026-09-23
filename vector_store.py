from typing import List, Tuple
import chromadb
from chromadb.utils import embedding_functions
from config import PERSIST_DIRECTORY, COLLECTION_NAME, EMBEDDING_MODEL_NAME
from models import HistoricalDefect

class KnowledgeBase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def seed_mock_data(self):
        """Populates the database with historical bug records if empty."""
        if self.collection.count() > 0:
            return

        defects = [
            HistoricalDefect(
                defect_id="BUG-101",
                title="NullPointerException in UserAuthService during OAuth callback",
                description="Token extraction fails when provider returns missing scope field.",
                affected_component="AuthModule",
                exception_type="NullPointerException",
                root_cause="Unchecked dictionary key access on missing OAuth scope payload.",
                resolution_summary="Added null-safe check and default scope fallback handling in AuthUtils.java.",
                code_path="com.service.auth.UserAuthService:line 142"
            ),
            HistoricalDefect(
                defect_id="BUG-204",
                title="Database Connection Timeout under heavy load in Payment gateway",
                description="HikariCP connection pool exhausted during spike in transaction volume.",
                affected_component="PaymentGateway",
                exception_type="HikariPoolTimeoutException",
                root_cause="Database connection leaks caused by missing try-with-resources on raw SQL execution.",
                resolution_summary="Wrapped statement execution in try-with-resources blocks and increased pool size from 10 to 30.",
                code_path="com.service.payment.TransactionRepository:line 89"
            ),
            HistoricalDefect(
                defect_id="BUG-309",
                title="JWT Parsing Error on expired authorization header",
                description="Server returns 500 internal server error instead of 401 Unauthorized on expired JWT tokens.",
                affected_component="AuthModule",
                exception_type="ExpiredJwtException",
                root_cause="ExpiredJwtException was caught by unhandled global exception handler and mapped to HTTP 500.",
                resolution_summary="Explicitly caught ExpiredJwtException in SecurityFilter and rethrown as 401 Unauthorized.",
                code_path="com.service.auth.SecurityFilter:line 55"
            )
        ]

        ids = [d.defect_id for d in defects]
        documents = [f"{d.title}\n{d.description}\n{d.root_cause}" for d in defects]
        metadatas = [d.model_dump() for d in defects]

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_similar_defects(self, query_text: str, top_k: int = 3) -> List[Tuple[HistoricalDefect, float]]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["metadatas", "distances"]
        )

        output = []
        if results and results["metadatas"]:
            for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
                # Chroma cosine distance to similarity score
                similarity = round(1.0 - distance, 4)
                defect = HistoricalDefect(**metadata)
                output.append((defect, similarity))
        return output