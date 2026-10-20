# ============================================================
# STEP D: LLM PROCESSING
#
# This file:
# 1. Splits the transcript into smaller chunks.
# 2. Uses Ollama to summarize each chunk.
# 3. Combines the chunk summaries.
# 4. Uses Gemini to create the final meeting knowledge.
# 5. Gemini returns a validated Pydantic structure.
#
# Final output:
#   - Summary
#   - Decisions
#   - Tasks
# ============================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from backend.meeting.i_state import MeetingState, MeetingKnowledge, Task

import os
import re

load_dotenv()


class MeetingLLM:

    def __init__(self):

        # ====================================================
        # 1. TEXT SPLITTER
        # ====================================================
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=150
        )

        # ====================================================
        # 2. OLLAMA (OPTIONAL)
        # ====================================================
        self.ollama = None
        try:
            self.ollama = ChatOllama(model="llama3.1:latest", temperature=0)
        except Exception as exc:
            print(f"Ollama unavailable; continuing without it: {exc}")

        # ====================================================
        # 3. GEMINI
        # ====================================================
        self.gemini = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.gemini = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0.2,
                    google_api_key=api_key,
                )
            except Exception as exc:
                print(f"Gemini client unavailable: {exc}")

        # ====================================================
        # 4. STRUCTURED GEMINI
        # ====================================================
        self.structured_gemini = None
        if self.gemini is not None:
            try:
                self.structured_gemini = self.gemini.with_structured_output(MeetingKnowledge)
            except Exception as exc:
                print(f"Structured Gemini output setup failed: {exc}")

        # ====================================================
        # 5. CHUNK PROMPT
        # ====================================================
        self.chunk_prompt = PromptTemplate(
            template="""
            You are an expert meeting summarizer.

            Read the following meeting transcript chunk.

            Summarize only the useful information.

            Focus on:
            - Important discussion points
            - Decisions mentioned
            - Tasks or action items mentioned
            - Task owners if clearly mentioned
            - Deadlines if clearly mentioned

            Ignore:
            - Greetings
            - Small talk
            - Jokes
            - Repeated information

            Do not invent information.

            Meeting Chunk:
            {chunk}
            """,
            input_variables=["chunk"],
        )

        self.final_prompt = PromptTemplate(
            template="""
            You are an expert meeting assistant.

            Below is information extracted from different parts
            of a meeting transcript.

            Create the final meeting knowledge.

            Rules:

            1. Do not invent information.
            2. Do not create a task unless the meeting indicates
            that an action needs to be performed.
            3. Do not invent task owners.
            4. DO NOT extract, calculate, interpret, or assign
            any deadline.
            5. Always return deadline_date as null.
            6. If the meeting mentions a deadline, ignore the
            deadline because it will be assigned manually later.
            7. If the meeting explicitly mentions a priority,
            use: low, medium, or high.
            8. If priority is not mentioned, return null.
            9. New tasks should normally have status "pending".
            10. A decision means something the team actually decided
                or agreed upon.
            11. Keep the summary concise but informative.

            Meeting Information:

            {chunk_information}
            """,
            input_variables=["chunk_information"],
        )

        # ====================================================
        # 6. CREATE CHAINS
        # ====================================================
        self.chunk_chain = self.chunk_prompt | self.ollama if self.ollama is not None else None
        self.final_chain = self.final_prompt | self.structured_gemini if self.structured_gemini is not None else None

    def _safe_invoke(self, chain, payload, fallback_text):
        if chain is None:
            return fallback_text

        try:
            response = chain.invoke(payload)
            return getattr(response, "content", str(response))
        except Exception as exc:
            print(f"AI call failed, using offline fallback: {exc}")
            return fallback_text

    def _fallback_summary(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return "No transcript content was provided."
        return cleaned[:500] + ("..." if len(cleaned) > 500 else "")

    def _fallback_decisions(self, transcript: str):
        decisions = []
        for sentence in re.split(r"(?<=[.!?])\s+", transcript):
            lower = sentence.lower()
            if any(word in lower for word in ["decided", "agreed", "approved", "will use", "will proceed", "we are moving forward", "we chose"]):
                cleaned = sentence.strip()
                if cleaned and cleaned not in decisions:
                    decisions.append(cleaned)
        return decisions

    def _fallback_tasks(self, transcript: str):
        tasks = []
        for sentence in re.split(r"(?<=[.!?])\s+", transcript):
            lower = sentence.lower()
            if any(word in lower for word in ["will", "need to", "should", "must", "can", "action item", "follow up", "next step", "responsible"]):
                cleaned = sentence.strip()
                if not cleaned:
                    continue
                owner_match = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:will|needs to|should|must|can)\b", sentence)
                owner = owner_match.group(1).strip() if owner_match else None
                tasks.append(Task(description=cleaned, owner=owner, status="pending"))
        return tasks[:10]

    def _fallback_meeting_knowledge(self, transcript: str):
        summary = self._fallback_summary(transcript)
        return MeetingKnowledge(
            summary=summary,
            decisions=self._fallback_decisions(transcript),
            tasks=self._fallback_tasks(transcript),
        )

    # ========================================================
    # PROCESS MEETING
    # ========================================================
    def process_meeting(self, state: MeetingState):

        print("Generating Meeting Knowledge...")

        transcript = state["transcript"]
        if not transcript or not transcript.strip():
            return {
                "summary": "No transcript available.",
                "decisions": [],
                "tasks": [],
            }

        chunks = self.splitter.create_documents([transcript])
        chunk_information = []

        for chunk in chunks:
            chunk_text = chunk.page_content
            fallback_text = self._fallback_summary(chunk_text)
            chunk_information.append(
                self._safe_invoke(
                    self.chunk_chain,
                    {"chunk": chunk_text},
                    fallback_text,
                )
            )

        combined_information = "\n\n".join(chunk_information)

        try:
            if self.final_chain is not None:
                final_result = self.final_chain.invoke({"chunk_information": combined_information})
            else:
                final_result = self._fallback_meeting_knowledge(transcript)
        except Exception as exc:
            print(f"Final structured inference failed, using offline fallback: {exc}")
            final_result = self._fallback_meeting_knowledge(transcript)

        print("Meeting Knowledge Generated")

        return {
            "summary": final_result.summary,
            "decisions": final_result.decisions,
            "tasks": final_result.tasks,
        }
