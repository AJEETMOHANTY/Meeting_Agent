# Generate embeddings for meeting transcript chunks and store them in PostgreSQL.

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pgvector.psycopg import register_vector

from backend.database.a_connection import engine


class MeetingEmbeddings:

    def __init__(self):
        # Split long transcripts into smaller chunks.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
        )

        # Load the embedding model used in the older Allen project.
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def generate_embeddings(self, transcript: str):
        # Split the transcript into chunks.
        chunks = self.splitter.create_documents([transcript])

        # Extract the text from each chunk.
        chunk_texts = [chunk.page_content for chunk in chunks]

        # Convert each chunk into a numerical vector.
        vectors = self.embeddings.embed_documents(chunk_texts)

        print(f"Number of chunks: {len(chunk_texts)}")
        print(f"Embedding dimensions: {len(vectors[0]) if vectors else 0}")

        return chunk_texts, vectors

    def store_embeddings(
        self,
        meeting_id: int,
        chunk_texts: list[str],
        vectors: list[list[float]],
    ):
        # Make sure each chunk has a corresponding embedding.
        if len(chunk_texts) != len(vectors):
            raise ValueError("The number of chunks and embeddings must match.")

        if not chunk_texts:
            print("No transcript chunks to store.")
            return 0

        # Open a transaction with the existing PostgreSQL database.
        with engine.begin() as conn:

            # Register pgvector support for the Psycopg 3 connection.
            register_vector(conn.connection.driver_connection)

            # Store each chunk and its embedding.
            for chunk_index, (content, vector) in enumerate(
                zip(chunk_texts, vectors)
            ):
                conn.exec_driver_sql(
                    """
                    INSERT INTO transcript_chunks
                        (meeting_id, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (meeting_id, chunk_index, content, vector),
                )

        print(
            f"Successfully stored {len(chunk_texts)} chunks "
            f"for meeting ID {meeting_id}."
        )

        return len(chunk_texts)
