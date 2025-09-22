"""
RAG (Retrieval-Augmented Generation) pipeline implementation
"""

import os
from openai import OpenAI

from typing import List, Dict, Any, Tuple
from config import Config
from vector_store import VectorStore


class RAGPipeline:
    """Implements the complete RAG pipeline for financial document Q&A"""

    def __init__(self, vector_store: VectorStore):
        self.config = Config()
        self.vector_store = vector_store
        self.config.validate_config()

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)

    def query(self, question: str, context_limit: int = None) -> Dict[str, Any]:
        """
        Process a question through the RAG pipeline

        Args:
            question: User's question
            context_limit: Maximum number of context chunks to use

        Returns:
            Dictionary containing answer, sources, and metadata
        """
        if context_limit is None:
            context_limit = self.config.TOP_K_RESULTS

        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question, top_k=context_limit)

        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the documents to answer your question.",
                "sources": [],
                "confidence": 0.0,
                "context_used": 0,
            }

        # Step 2: Prepare context for generation
        context_text = self._prepare_context(retrieved_docs)

        # Step 3: Generate answer using LLM
        answer = self._generate_answer(question, context_text)

        # Step 4: Extract sources and metadata
        sources = self._extract_sources(retrieved_docs)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": self._calculate_confidence(retrieved_docs),
            "context_used": len(retrieved_docs),
        }

    def _prepare_context(
        self, retrieved_docs: List[Tuple[str, Dict[str, Any], float]]
    ) -> str:
        """Prepare context text from retrieved documents"""
        context_parts = []

        for i, (text, metadata, score) in enumerate(retrieved_docs, 1):
            # Add source information
            source_info = self._format_source_info(metadata)
            context_parts.append(f"[Context {i}] {source_info}\n{text}\n")

        return "\n".join(context_parts)

    def _format_source_info(self, metadata: Dict[str, Any]) -> str:
        """Format source information for context"""
        source_parts = []

        if "source" in metadata:
            source_file = os.path.basename(metadata["source"])
            source_parts.append(f"Source: {source_file}")

        if "page" in metadata:
            source_parts.append(f"Page: {metadata['page']}")

        if "category" in metadata:
            source_parts.append(f"Category: {metadata['category']}")

        if "document_type" in metadata:
            source_parts.append(f"Type: {metadata['document_type'].upper()}")

        return " | ".join(source_parts)

    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using OpenAI GPT model"""

        system_prompt = """You are a financial analyst assistant. Your job is to answer questions about financial documents (10-K reports, XBRL filings) based only on the provided context.

Guidelines:
1. Answer based ONLY on the information provided in the context
2. If the context doesn't contain enough information to answer the question, say so
3. Be precise and cite specific numbers, dates, or facts when available
4. For financial questions, include relevant metrics and context
5. If you're unsure about something, express that uncertainty
6. Keep answers concise but comprehensive

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt.format(
                            context=context, question=question
                        ),
                    }
                ],
                max_tokens=self.config.MAX_TOKENS,
                temperature=0.1,  # Low temperature for more consistent, factual responses
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def _extract_sources(
        self, retrieved_docs: List[Tuple[str, Dict[str, Any], float]]
    ) -> List[Dict[str, Any]]:
        """Extract and format source information"""
        sources = []

        for text, metadata, score in retrieved_docs:
            source_info = {
                "text_preview": text[:200] + "..." if len(text) > 200 else text,
                "similarity_score": score,
                "metadata": metadata,
            }
            sources.append(source_info)

        return sources

    def _calculate_confidence(
        self, retrieved_docs: List[Tuple[str, Dict[str, Any], float]]
    ) -> float:
        """Calculate confidence score based on retrieved documents"""
        if not retrieved_docs:
            return 0.0

        # Average similarity score
        avg_score = sum(score for _, _, score in retrieved_docs) / len(retrieved_docs)

        # Normalize to 0-1 range (assuming scores are typically 0-1)
        confidence = min(avg_score, 1.0)

        return confidence

    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple questions in batch"""
        results = []

        for question in questions:
            result = self.query(question)
            results.append({"question": question, **result})

        return results
