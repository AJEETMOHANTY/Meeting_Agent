# ============================================================
# STEP G: VECTOR SEARCH
#
# This file searches stored meeting transcript chunks using
# semantic similarity.
# ============================================================

from langchain_huggingface import HuggingFaceEmbeddings
from pgvector.psycopg import register_vector
from sqlalchemy import sql

from backend.database.a_connection import engine


class MeetingRAG:

    def __init__(self):
        # Use the same embedding model used for transcript chunks.
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def search(self, question: str, limit: int = 5, meeting_id: int = None):
        # Convert the user's question into a 1024-dimensional vector.
        question_vector = self.embeddings.embed_query(question)

        # Build the SQL query.
        sql = """
            SELECT
                meeting_id,
                chunk_index,
                content,
                embedding <=> %s AS distance
            FROM transcript_chunks
        """

        parameters = [question_vector]

        # Optionally restrict the search to one meeting.
        if meeting_id is not None:
            sql += " WHERE meeting_id = %s"
            parameters.append(meeting_id)

        # Smaller cosine distance means greater similarity.
        sql += """
            ORDER BY embedding <=> %s
            LIMIT %s
        """

        parameters.extend([question_vector, limit])

        # Execute the vector search.
        with engine.begin() as connection:
            # Register pgvector support for the underlying psycopg connection.
            raw_connection = connection.connection.driver_connection
            register_vector(raw_connection)

            # Convert the question embedding into a pgvector Vector object.
            from pgvector import Vector

            question_vector = Vector(question_vector)

            # Rebuild the parameters using the properly adapted vector.
            parameters = [question_vector]

            if meeting_id is not None:
                parameters.append(meeting_id)

            parameters.extend([question_vector, limit])

            rows = connection.exec_driver_sql(
                sql,
                tuple(parameters),
            ).fetchall()

        # Return the matching transcript chunks.
        return [
            {
                "meeting_id": row[0],
                "chunk_index": row[1],
                "content": row[2],
                "distance": float(row[3]),
            }
            for row in rows
        ]


# ============================================================
# TEST VECTOR SEARCH
# ============================================================

if __name__ == "__main__":

    rag = MeetingRAG()

    question = input("Ask a question about your meetings: ")

    results = rag.search(question, limit=5)

    print("\nRELEVANT TRANSCRIPT CHUNKS")
    print("=" * 50)

    if not results:
        print("No transcript chunks found.")
    else:
        for result in results:
            print(f"\nMeeting ID: {result['meeting_id']}")
            print(f"Chunk Index: {result['chunk_index']}")
            print(f"Cosine Distance: {result['distance']:.4f}")
            print(f"Content: {result['content']}")
            print("-" * 50)