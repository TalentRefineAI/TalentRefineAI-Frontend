"""
Módulo de cliente API para la aplicación RAG.
Gestiona las llamadas HTTP a los endpoints de FastAPI.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv
from utils.mock_data import (
    get_mock_candidates,
    get_mock_query_results,
    get_mock_upload_progress,
    get_available_locations,
    get_available_skills
)

load_dotenv()


def _parse_bool_env(env_key: str, default: bool) -> bool:
    value = os.getenv(env_key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int_env(env_key: str, default: int) -> int:
    value = os.getenv(env_key)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _map_candidate_result(r: Dict[str, Any]) -> Dict[str, Any]:
    """Mapea un CandidateResult del backend al formato esperado por el frontend."""
    contact = r.get("contact_info") or {}
    return {
        "id": r.get("candidate_id", ""),
        "name": contact.get("name") or r.get("file_name", "Candidato"),
        "email": contact.get("email", "N/A"),
        "phone": contact.get("phone", "N/A"),
        "experience_years": r.get("exp_years", 0),
        "location": r.get("location") or "N/A",
        "skills": contact.get("skills", []),
        "expertise_summary": r.get("summary", ""),
        "match_score": round(r.get("score", 0) * 100),
        "llm_justification": r.get("justification", ""),
        "document_name": r.get("file_name", ""),
    }


class RAGAPIClient:
    """Cliente para comunicarse con las APIs de ingesta, procesamiento y RAG."""

    def __init__(
        self,
        ingest_base_url: str = "http://localhost:8000",
        process_base_url: Optional[str] = None,
        rag_base_url: Optional[str] = None,
        use_mock: bool = True,
        timeout: int = 120
    ):
        self.ingest_base_url = ingest_base_url.rstrip("/")
        self.process_base_url = (process_base_url or ingest_base_url).rstrip("/")
        self.rag_base_url = (rag_base_url or ingest_base_url).rstrip("/")
        self.use_mock = use_mock
        self.timeout = timeout
        self.session = requests.Session()

    def upload_cv_documents(self, files: List[bytes], filenames: List[str]) -> Dict[str, Any]:
        """
        Sube documentos CV al servicio de ingesta.

        Returns:
            Dict con document_ids (list[str]), message, status.
        """
        if self.use_mock:
            return {
                "status": "success",
                "message": f"Se han procesado {len(files)} documentos exitosamente",
                "document_ids": [f"doc_{i}" for i in range(len(files))],
                "filenames": filenames,
                "processing_time_ms": 1250,
            }

        try:
            url = f"{self.ingest_base_url}/upload"
            files_data = [
                ("files", (filename, file_content, "application/pdf"))
                for filename, file_content in zip(filenames, files)
            ]
            response = self.session.post(url, files=files_data, timeout=self.timeout)
            response.raise_for_status()
            body = response.json()
            # Backend returns ApiResponse { data: [{id, file_name, status}, ...] }
            items = body.get("data") or []
            document_ids = [item["id"] for item in items if item.get("id")]
            return {
                "status": "success",
                "message": f"Se han encolado {len(document_ids)} documentos",
                "document_ids": document_ids,
                "filenames": filenames,
                "processing_time_ms": 0,
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al conectar con la API: {str(e)}",
                "document_ids": [],
            }

    def query_rag(
        self,
        query: str,
        experience_min: int = 0,
        experience_max: int = 20,
        locations: List[str] = None,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Realiza una consulta semantica al servicio RAG.

        Returns:
            Dict con candidates (lista en formato frontend), total_results, query, metadata.
        """
        if self.use_mock:
            return get_mock_query_results(
                query=query,
                experience_min=experience_min,
                experience_max=experience_max,
                locations=locations,
            )

        try:
            url = f"{self.rag_base_url}/search"
            # Backend SearchRequest fields: job_description, min_exp_years, required_location, top_k
            required_location = locations[0] if locations else None
            payload = {
                "job_description": query,
                "min_exp_years": float(experience_min) if experience_min else None,
                "required_location": required_location,
                "top_k": min(top_k, 20),
            }
            _t0 = time.perf_counter()
            response = self.session.post(url, json=payload, timeout=self.timeout)
            _elapsed_ms = round((time.perf_counter() - _t0) * 1000)
            response.raise_for_status()
            body = response.json()
            # Backend returns SearchResponse { results: [CandidateResult, ...] }
            candidates = [_map_candidate_result(r) for r in body.get("results", [])]
            # Use backend-measured time if available, fall back to client-side RTT
            _backend_ms = body.get("processing_time_ms") or 0
            return {
                "query": query,
                "total_results": len(candidates),
                "candidates": candidates,
                "search_timestamp": datetime.now().isoformat(),
                "metadata": {
                    "experience_range": f"{experience_min}-{experience_max} anos",
                    "locations_filtered": locations if locations else "Todas",
                    "processing_time_ms": _backend_ms or _elapsed_ms,
                },
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error en la consulta RAG: {str(e)}",
                "candidates": [],
            }

    def download_cv(self, doc_id: str, filename: str) -> bytes | None:
        """Descarga los bytes del PDF de un candidato via ingest-service."""
        if self.use_mock or not doc_id or not filename:
            return None
        try:
            url = f"{self.ingest_base_url}/upload/{doc_id}/download"
            response = self.session.get(url, params={"filename": filename}, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException:
            return None

    def list_candidates(self) -> list[dict]:
        """Obtiene todos los candidatos indexados (nombre + email) desde el RAG service."""
        if self.use_mock:
            return [
                {"candidate_id": "mock-1", "name": "Ana García", "email": "ana@example.com", "file_name": "Ana_Garcia_CV.pdf"},
                {"candidate_id": "mock-2", "name": "Carlos López", "email": "carlos@example.com", "file_name": "Carlos_Lopez_CV.pdf"},
            ]
        try:
            url = f"{self.rag_base_url}/search/candidates"
            _t0 = time.perf_counter()
            response = self.session.get(url, timeout=self.timeout)
            _elapsed_ms = round((time.perf_counter() - _t0) * 1000)
            response.raise_for_status()
            body = response.json()
            # Store timing so callers can display it
            self._last_list_candidates_ms = body.get("processing_time_ms") or _elapsed_ms
            return body.get("candidates", [])
        except requests.exceptions.RequestException:
            self._last_list_candidates_ms = 0
            return []

    def get_candidate_details(self, candidate_id: str) -> Dict[str, Any]:
        """Detalle de candidato. Backend no expone este endpoint; usa mock."""
        candidates = get_mock_candidates()
        for candidate in candidates:
            if str(candidate["id"]) == candidate_id:
                return {"status": "success", "candidate": candidate}
        return {"status": "error", "message": "Candidato no encontrado"}

    def get_upload_status(self, doc_id: str) -> Dict[str, Any]:
        """Obtiene el estado de procesamiento de un documento subido."""
        if self.use_mock:
            return get_mock_upload_progress()

        try:
            url = f"{self.ingest_base_url}/upload/{doc_id}/status"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al obtener estado: {str(e)}",
                "files": [],
            }

    def process_document(self, doc_id: str) -> Dict[str, Any]:
        """
        El ingest-service dispara el procesamiento como background task automaticamente.
        En modo real se retorna exito inmediato para no bloquear el flujo.
        Processing is already triggered by ingest-service as a background task.
        """
        if self.use_mock:
            return {
                "status": "success",
                "message": f"Documento {doc_id} procesado con exito",
                "document_id": doc_id,
            }
        return {
            "status": "success",
            "message": f"Documento {doc_id} en cola de procesamiento",
            "document_id": doc_id,
        }

    def delete_all_index(self) -> dict:
        """Elimina toda la colección de candidatos de Qdrant via rag-service."""
        if self.use_mock:
            return {"deleted": True}
        try:
            url = f"{self.rag_base_url}/search/candidates"
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"deleted": False, "error": str(e)}

    def delete_all_uploads(self) -> dict:
        """Elimina todos los blobs de Blob Storage via ingest-service."""
        if self.use_mock:
            return {"deleted": True}
        try:
            url = f"{self.ingest_base_url}/upload/all"
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"deleted": False, "error": str(e)}

    def get_available_locations(self) -> List[str]:
        """Backend no expone este endpoint; retorna datos estaticos."""
        return get_available_locations()

    def get_available_skills(self) -> List[str]:
        """Backend no expone este endpoint; retorna datos estaticos."""
        return get_available_skills()


import streamlit as st

@st.cache_resource
def get_api_client(
    use_mock: Optional[bool] = None,
    ingest_base_url: Optional[str] = None,
    process_base_url: Optional[str] = None,
    rag_base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> RAGAPIClient:
    """
    Obtiene una instancia del cliente API configurada desde variables de entorno.

    Variables de entorno relevantes:
      USE_MOCK_DATA   -- "true"/"false"
      INGEST_API_URL  -- URL del servicio de ingesta
      PROCESS_API_URL -- URL del servicio de procesamiento
      RAG_API_URL     -- URL del servicio RAG (rag-service)
      API_URL         -- URL fallback generica
      API_TIMEOUT     -- timeout en segundos
    """
    if use_mock is None:
        use_mock = _parse_bool_env("USE_MOCK_DATA", True)

    default_url = os.getenv("API_URL", "http://localhost:8000")

    ingest_base_url = ingest_base_url or os.getenv("INGEST_API_URL", default_url)
    process_base_url = process_base_url or os.getenv("PROCESS_API_URL", default_url)
    rag_base_url = rag_base_url or os.getenv("RAG_API_URL", default_url)
    timeout = timeout if timeout is not None else _parse_int_env("API_TIMEOUT", 120)

    return RAGAPIClient(
        ingest_base_url=ingest_base_url,
        process_base_url=process_base_url,
        rag_base_url=rag_base_url,
        use_mock=use_mock,
        timeout=timeout,
    )
