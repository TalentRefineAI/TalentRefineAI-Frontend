"""
Módulo de cliente API para la aplicación RAG.
Gestiona las llamadas HTTP a los endpoints de FastAPI.
Usa datos simulados (mocks) hasta que se integre la API real en la Fase 2.
"""

import os
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



class RAGAPIClient:
    """Cliente para comunicarse con las APIs de ingesta y procesamiento."""
    
    def __init__(
        self,
        ingest_base_url: str = "http://localhost:8000",
        process_base_url: Optional[str] = None,
        use_mock: bool = True,
        timeout: int = 30
    ):
        """
        Inicializa el cliente API.
        
        Args:
            ingest_base_url (str): URL base del servicio de ingesta.
            process_base_url (Optional[str]): URL base del servicio de procesamiento.
                Si no se proporciona, se utiliza ingest_base_url.
            use_mock (bool): Si True, usa datos simulados; si False, llama a la API real.
            timeout (int): Timeout en segundos para las llamadas HTTP.
        """
        self.ingest_base_url = ingest_base_url.rstrip("/")
        self.process_base_url = (process_base_url or ingest_base_url).rstrip("/")
        self.use_mock = use_mock
        self.timeout = timeout
        self.session = requests.Session()
    
    def upload_cv_documents(self, files: List[bytes], filenames: List[str]) -> Dict[str, Any]:
        """
        Sube documentos CV a la API para procesamiento.
        
        Args:
            files (List[bytes]): Lista de contenidos de archivos
            filenames (List[str]): Lista de nombres de archivos
            
        Returns:
            Dict[str, Any]: Respuesta de la API con IDs de documentos
        """
        if self.use_mock:
            # Retornar datos simulados
            return {
                "status": "success",
                "message": f"Se han procesado {len(files)} documentos exitosamente",
                "document_ids": [f"doc_{i}" for i in range(len(files))],
                "filenames": filenames,
                "processing_time_ms": 1250
            }
        
        # Aquí iría la lógica real de llamada a API
        try:
            url = f"{self.ingest_base_url}/upload"
            files_data = [
                ("files", (filename, file_content))
                for filename, file_content in zip(filenames, files)
            ]
            response = self.session.post(url, files=files_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al conectar con la API: {str(e)}",
                "document_ids": []
            }
    
    def query_rag(self, query: str, experience_min: int = 0, 
                  experience_max: int = 20, locations: List[str] = None,
                  top_k: int = 10) -> Dict[str, Any]:
        """
        Realiza una consulta semántica a través del sistema RAG.
        
        Args:
            query (str): Consulta semántica del reclutador
            experience_min (int): Años mínimos de experiencia requeridos
            experience_max (int): Años máximos de experiencia
            locations (List[str]): Ubicaciones preferidas
            top_k (int): Número de resultados a devolver
            
        Returns:
            Dict[str, Any]: Resultados de la búsqueda RAG
        """
        if self.use_mock:
            # Retornar datos simulados
            return get_mock_query_results(
                query=query,
                experience_min=experience_min,
                experience_max=experience_max,
                locations=locations
            )
        
        # Aquí iría la lógica real de llamada a API
        try:
            url = f"{self.process_base_url}/api/v1/rag/query"
            payload = {
                "query": query,
                "experience_min": experience_min,
                "experience_max": experience_max,
                "locations": locations or [],
                "top_k": top_k
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error en la consulta RAG: {str(e)}",
                "candidates": []
            }
    
    def get_candidate_details(self, candidate_id: str) -> Dict[str, Any]:
        """
        Obtiene los detalles completos de un candidato específico.
        
        Args:
            candidate_id (str): ID del candidato
            
        Returns:
            Dict[str, Any]: Detalles del candidato
        """
        if self.use_mock:
            # Retornar candidato simulado
            candidates = get_mock_candidates()
            for candidate in candidates:
                if str(candidate["id"]) == candidate_id:
                    return {
                        "status": "success",
                        "candidate": candidate
                    }
            return {
                "status": "error",
                "message": "Candidato no encontrado"
            }
        
        # Aquí iría la lógica real de llamada a API
        try:
            url = f"{self.process_base_url}/api/v1/candidates/{candidate_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al obtener detalles: {str(e)}"
            }
    
    def get_upload_status(self, doc_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un documento subido.
        
        Args:
            doc_id (str): ID del documento subido.

        Returns:
            Dict[str, Any]: Estado del documento
        """
        if self.use_mock:
            # Retornar estado simulado
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
                "files": []
            }

    def process_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Inicia el procesamiento de un documento mediante el servicio de procesamiento.
        
        Args:
            doc_id (str): ID del documento a procesar.

        Returns:
            Dict[str, Any]: Respuesta del servicio de procesamiento
        """
        if self.use_mock:
            return {
                "status": "success",
                "message": f"Documento {doc_id} procesado con éxito",
                "document_id": doc_id
            }

        try:
            url = f"{self.process_base_url}/processing/{doc_id}"
            response = self.session.post(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al procesar documento {doc_id}: {str(e)}"
            }

    def get_available_locations(self) -> List[str]:
        """
        Obtiene la lista de ubicaciones disponibles.
        
        Returns:
            List[str]: Lista de ubicaciones
        """
        if self.use_mock:
            return get_available_locations()
        
        try:
            url = f"{self.process_base_url}/api/v1/filters/locations"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("locations", [])
        except requests.exceptions.RequestException:
            return get_available_locations()  # Fallback a datos locales
    
    def get_available_skills(self) -> List[str]:
        """
        Obtiene la lista de habilidades disponibles.
        
        Returns:
            List[str]: Lista de habilidades
        """
        if self.use_mock:
            return get_available_skills()
        
        try:
            url = f"{self.process_base_url}/api/v1/filters/skills"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("skills", [])
        except requests.exceptions.RequestException:
            return get_available_skills()  # Fallback a datos locales


# Instancia global del cliente (puede reutilizarse en toda la app)
def get_api_client(
    use_mock: Optional[bool] = None,
    ingest_base_url: Optional[str] = None,
    process_base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> RAGAPIClient:
    """
    Obtiene una instancia del cliente API.
    
    Args:
        use_mock (Optional[bool]): Si True, usa mocks; si False, usa API real.
            Si no se provee, se lee de USE_MOCK_DATA.
        ingest_base_url (Optional[str]): URL base del servicio de ingesta.
        process_base_url (Optional[str]): URL base del servicio de procesamiento.
        timeout (Optional[int]): Timeout en segundos para las llamadas HTTP.
        
    Returns:
        RAGAPIClient: Instancia del cliente
    """
    if use_mock is None:
        use_mock = _parse_bool_env("USE_MOCK_DATA", True)

    ingest_base_url = ingest_base_url or os.getenv(
        "INGEST_API_URL",
        os.getenv("API_URL", "http://localhost:8000")
    )
    process_base_url = process_base_url or os.getenv(
        "PROCESS_API_URL",
        os.getenv("API_URL", ingest_base_url)
    )
    timeout = timeout if timeout is not None else _parse_int_env("API_TIMEOUT", 30)

    return RAGAPIClient(
        ingest_base_url=ingest_base_url,
        process_base_url=process_base_url,
        use_mock=use_mock,
        timeout=timeout,
    )
