# services/vector_service.py
from typing import List, Dict, Any
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
import os
import numpy as np


class VectorService:
    def __init__(self):
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.init_connection()
        self.init_collections()

    def init_connection(self):
        try:
            if connections.has_connection("default"):
                connections.remove_connection("default")
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                timeout=10
            )
            print(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {str(e)}")
            raise

    def init_collections(self):
        try:
            # Journal entries collection
            if "journal_entries" not in utility.list_collections():
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64,
                                is_primary=True, auto_id=True),
                    FieldSchema(name="entry_id", dtype=DataType.INT64),
                    FieldSchema(name="embedding",
                                dtype=DataType.FLOAT_VECTOR, dim=1536),
                    FieldSchema(name="mood", dtype=DataType.FLOAT),
                ]
                schema = CollectionSchema(
                    fields=fields, description="Journal entries embeddings")
                collection = Collection(name="journal_entries", schema=schema)
                collection.create_index(
                    field_name="embedding",
                    index_params={
                        "metric_type": "L2",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 1024}
                    }
                )

            # Chat messages collection
            if "chat_messages" not in utility.list_collections():
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64,
                                is_primary=True, auto_id=True),
                    FieldSchema(name="entry_id", dtype=DataType.INT64),
                    FieldSchema(name="embedding",
                                dtype=DataType.FLOAT_VECTOR, dim=1536)
                ]
                schema = CollectionSchema(
                    fields=fields, description="Chat messages embeddings")
                collection = Collection(name="chat_messages", schema=schema)
                collection.create_index(
                    field_name="embedding",
                    index_params={
                        "metric_type": "L2",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 1024}
                    }
                )
        except Exception as e:
            print(f"Failed to initialize collections: {str(e)}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        return list(np.random.rand(1536))

    def store_vector(self, entry_id: int, vector: List[float], collection_name: str, mood: float = None) -> int:
        try:
            collection = Collection(collection_name)
            data = [
                [entry_id],    # entry_id
                [vector],      # embedding
            ]

            if collection_name == "journal_entries" and mood is not None:
                data.append([float(mood)])  # mood

            mr = collection.insert(data)
            collection.flush()
            return mr.primary_keys[0]
        except Exception as e:
            print(f"Failed to store vector: {str(e)}")
            raise

    def search_similar(self, vector: List[float], collection_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            collection = Collection(collection_name)
            collection.load()

            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }

            results = collection.search(
                data=[vector],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=[
                    "entry_id", "mood"] if collection_name == "journal_entries" else ["entry_id"]
            )

            similar_entries = []
            for hits in results:
                for hit in hits:
                    entry = {
                        "entry_id": hit.entity.get("entry_id"),
                        "similarity": 1 - hit.distance
                    }
                    if collection_name == "journal_entries":
                        entry["mood"] = hit.entity.get("mood")
                    similar_entries.append(entry)

            return similar_entries
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise
        finally:
            collection.release()

