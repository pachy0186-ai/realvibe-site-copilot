"""
Vector search service for RealVibe Site Copilot.
Handles document embeddings, chunking, and similarity search.
"""

import os
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import re

import openai
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class VectorService:
    """Service for vector embeddings and similarity search."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        if hasattr(settings, 'OPENAI_API_BASE'):
            openai.api_base = settings.OPENAI_API_BASE
        
        # Initialize local embedding model as fallback
        try:
            self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.local_model = None
        
        # Chunk settings
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process_document(self, file_id: str, text_content: str) -> Dict[str, Any]:
        """
        Process a document by creating embeddings for text chunks.
        
        Args:
            file_id: Unique file identifier
            text_content: Full text content of the document
            
        Returns:
            Dict containing processing results
        """
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text_content)
            
            if not chunks:
                return {"chunks_created": 0, "embeddings_created": 0}
            
            # Create embeddings for each chunk
            embeddings_created = 0
            
            for i, chunk in enumerate(chunks):
                try:
                    # Generate embedding
                    embedding = await self._generate_embedding(chunk)
                    
                    if embedding is not None:
                        # Store chunk and embedding
                        chunk_data = {
                            "id": str(uuid.uuid4()),
                            "file_id": file_id,
                            "chunk_index": i,
                            "text_content": chunk,
                            "embedding": embedding,
                            "created_at": datetime.utcnow().isoformat()
                        }
                        
                        result = self.supabase.table("document_chunks").insert(chunk_data).execute()
                        
                        if result.data:
                            embeddings_created += 1
                        
                except Exception as e:
                    print(f"Failed to process chunk {i} for file {file_id}: {e}")
                    continue
            
            return {
                "chunks_created": len(chunks),
                "embeddings_created": embeddings_created
            }
            
        except Exception as e:
            print(f"Document processing failed for file {file_id}: {e}")
            return {"chunks_created": 0, "embeddings_created": 0}
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text or len(text.strip()) == 0:
            return []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end position
            end = start + self.chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
            
            # Try to break at sentence boundary
            chunk_text = text[start:end]
            
            # Look for sentence endings near the end of the chunk
            sentence_endings = ['. ', '! ', '? ', '\n\n']
            best_break = -1
            
            for ending in sentence_endings:
                last_occurrence = chunk_text.rfind(ending)
                if last_occurrence > self.chunk_size * 0.7:  # At least 70% of chunk size
                    best_break = max(best_break, last_occurrence + len(ending))
            
            if best_break > 0:
                chunk = text[start:start + best_break].strip()
                start = start + best_break - self.chunk_overlap
            else:
                # No good break point, use word boundary
                words = chunk_text.split()
                if len(words) > 1:
                    chunk = ' '.join(words[:-1])
                    start = start + len(chunk) - self.chunk_overlap
                else:
                    chunk = chunk_text
                    start = end - self.chunk_overlap
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            # Ensure we make progress
            if start <= len(chunks) * 10:  # Prevent infinite loops
                start = max(start, len(chunks) * 10 + 1)
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI or local model."""
        try:
            # Try OpenAI first
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                response = await openai.Embedding.acreate(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response['data'][0]['embedding']
        except Exception as e:
            print(f"OpenAI embedding failed: {e}")
        
        # Fallback to local model
        try:
            if self.local_model:
                embedding = self.local_model.encode(text)
                return embedding.tolist()
        except Exception as e:
            print(f"Local embedding failed: {e}")
        
        return None
    
    async def search_similar_chunks(
        self, 
        query: str, 
        site_id: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks based on query.
        
        Args:
            query: Search query text
            site_id: Site identifier to limit search scope
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            if query_embedding is None:
                return []
            
            # Get all chunks for the site
            # Note: In production, this should use vector similarity search
            # For now, we'll use a simplified approach
            
            chunks_result = self.supabase.table("document_chunks").select(
                "*, files!inner(site_id, filename)"
            ).eq("files.site_id", site_id).execute()
            
            if not chunks_result.data:
                return []
            
            # Calculate similarities
            similarities = []
            
            for chunk in chunks_result.data:
                try:
                    chunk_embedding = chunk.get('embedding')
                    if chunk_embedding:
                        similarity = self._calculate_cosine_similarity(
                            query_embedding, chunk_embedding
                        )
                        
                        if similarity >= similarity_threshold:
                            similarities.append({
                                "chunk_id": chunk["id"],
                                "file_id": chunk["file_id"],
                                "filename": chunk["files"]["filename"],
                                "text_content": chunk["text_content"],
                                "chunk_index": chunk["chunk_index"],
                                "similarity": similarity
                            })
                except Exception as e:
                    print(f"Error calculating similarity for chunk {chunk.get('id')}: {e}")
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Similar chunks search failed: {e}")
            return []
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
        except Exception:
            return 0.0
    
    async def get_evidence_for_field(
        self, 
        field_label: str, 
        field_context: str, 
        site_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get evidence chunks relevant to a specific questionnaire field.
        
        Args:
            field_label: Label of the questionnaire field
            field_context: Additional context about what the field is asking
            site_id: Site identifier
            
        Returns:
            List of relevant evidence chunks
        """
        # Combine field label and context for better search
        search_query = f"{field_label} {field_context}".strip()
        
        # Search for similar chunks
        evidence_chunks = await self.search_similar_chunks(
            query=search_query,
            site_id=site_id,
            limit=3,
            similarity_threshold=0.6
        )
        
        # Format evidence for response
        evidence = []
        for chunk in evidence_chunks:
            evidence.append({
                "file_id": chunk["file_id"],
                "file_name": chunk["filename"],
                "page": chunk["chunk_index"] + 1,  # Approximate page number
                "text": chunk["text_content"][:200] + "..." if len(chunk["text_content"]) > 200 else chunk["text_content"],
                "similarity": round(chunk["similarity"], 3)
            })
        
        return evidence
    
    async def delete_document_embeddings(self, file_id: str) -> bool:
        """Delete all embeddings for a document."""
        try:
            result = self.supabase.table("document_chunks").delete().eq(
                "file_id", file_id
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to delete embeddings for file {file_id}: {e}")
            return False
    
    async def get_embedding_stats(self, site_id: str) -> Dict[str, Any]:
        """Get statistics about embeddings for a site."""
        try:
            # Get total chunks count
            chunks_result = self.supabase.table("document_chunks").select(
                "id", count="exact"
            ).eq("files.site_id", site_id).execute()
            
            # Get files with embeddings
            files_result = self.supabase.table("files").select(
                "id, filename"
            ).eq("site_id", site_id).execute()
            
            files_with_embeddings = 0
            if files_result.data:
                for file_data in files_result.data:
                    file_chunks = self.supabase.table("document_chunks").select(
                        "id", count="exact"
                    ).eq("file_id", file_data["id"]).execute()
                    
                    if file_chunks.count and file_chunks.count > 0:
                        files_with_embeddings += 1
            
            return {
                "total_chunks": chunks_result.count or 0,
                "total_files": len(files_result.data) if files_result.data else 0,
                "files_with_embeddings": files_with_embeddings,
                "embedding_model": "text-embedding-ada-002" if hasattr(settings, 'OPENAI_API_KEY') else "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            print(f"Failed to get embedding stats: {e}")
            return {
                "total_chunks": 0,
                "total_files": 0,
                "files_with_embeddings": 0,
                "embedding_model": "unknown"
            }

