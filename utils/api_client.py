"""
Módulo de cliente API para la aplicación RAG.
Gestiona las llamadas HTTP a los endpoints de FastAPI.
Usa datos simulados (mocks) hasta que se integre la API real en la Fase 2.
"""

import requests
from typing import List, Dict, Any, Optional
from utils.mock_data import (
    get_mock_candidates,
    get_mock_query_results,
    get_mock_upload_progress,
    get_available_locations,
    get_available_skills
)


class RAGAPIClient:
    """Cliente para comunicarse con la API RAG de selección de personal."""
    
    def __init__(self, base_url: str = "http://localhost:8000", use_mock: bool = True):
        """
        Inicializa el cliente API.
        
        Args:
            base_url (str): URL base de la API (por defecto localhost)
            use_mock (bool): Si True, usa datos simulados; si False, llama a la API real
        """
        self.base_url = base_url
        self.use_mock = use_mock
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
            url = f"{self.base_url}/api/v1/documents/upload"
            files_data = [
                ("files", (filename, file_content))
                for filename, file_content in zip(filenames, files)
            ]
            response = self.session.post(url, files=files_data, timeout=30)
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
            url = f"{self.base_url}/api/v1/rag/query"
            payload = {
                "query": query,
                "experience_min": experience_min,
                "experience_max": experience_max,
                "locations": locations or [],
                "top_k": top_k
            }
            response = self.session.post(url, json=payload, timeout=30)
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
            url = f"{self.base_url}/api/v1/candidates/{candidate_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al obtener detalles: {str(e)}"
            }
    
    def get_upload_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual de los documentos en subida.
        
        Returns:
            Dict[str, Any]: Estado de los documentos
        """
        if self.use_mock:
            # Retornar estado simulado
            return get_mock_upload_progress()
        
        # Aquí iría la lógica real de llamada a API
        try:
            url = f"{self.base_url}/api/v1/documents/status"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error al obtener estado: {str(e)}",
                "files": []
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
            url = f"{self.base_url}/api/v1/filters/locations"
            response = self.session.get(url, timeout=10)
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
            url = f"{self.base_url}/api/v1/filters/skills"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get("skills", [])
        except requests.exceptions.RequestException:
            return get_available_skills()  # Fallback a datos locales


# Instancia global del cliente (puede reutilizarse en toda la app)
def get_api_client(use_mock: bool = True) -> RAGAPIClient:
    """
    Obtiene una instancia del cliente API.
    
    Args:
        use_mock (bool): Si True, usa mocks; si False, usa API real
        
    Returns:
        RAGAPIClient: Instancia del cliente
    """
    return RAGAPIClient(use_mock=use_mock)
