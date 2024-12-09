# services/vector_service.py
from typing import List
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from models.chat import ChatMessage
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
            # Chat messages collection with message text field
            if "chat_messages" not in utility.list_collections():
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64,
                                is_primary=True, auto_id=True),
                    FieldSchema(name="message",
                                dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="is_ai", dtype=DataType.BOOL),
                    FieldSchema(name="embedding",
                                dtype=DataType.FLOAT_VECTOR, dim=1536),
                    FieldSchema(name="timestamp", dtype=DataType.INT64)
                ]
                schema = CollectionSchema(
                    fields=fields, description="Chat messages with embeddings")
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

    def store_message(self, message: str, is_ai: bool, vector: List[float]) -> int:
        try:
            collection = Collection("chat_messages")
            import time
            data = [
                [message],          # message
                [is_ai],           # is_ai
                [vector],          # embedding
                [int(time.time())]  # timestamp
            ]
            mr = collection.insert(data)
            collection.flush()
            return mr.primary_keys[0]
        except Exception as e:
            print(f"Failed to store message: {str(e)}")
            raise

    def search_similar(self, vector: List[float], limit: int = 5) -> List[ChatMessage]:
        try:
            collection = Collection("chat_messages")
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
                output_fields=["message", "is_ai"]
            )

            similar_messages = []
            for hits in results:
                for hit in hits:
                    similar_messages.append(ChatMessage(
                        message=hit.entity.get("message"),
                        is_ai=hit.entity.get("is_ai"),
                        similarity=1 - hit.distance
                    ))

            return similar_messages
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise
        finally:
            collection.release()
