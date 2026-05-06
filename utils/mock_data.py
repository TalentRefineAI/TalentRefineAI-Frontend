"""
Módulo de datos simulados (mocks) para la aplicación RAG de selección de personal.
Estos datos se utilizan hasta que se integre la API real en la Fase 2.
"""

from typing import List, Dict, Any
from datetime import datetime


def get_mock_candidates() -> List[Dict[str, Any]]:
    """
    Retorna una lista de candidatos simulados con sus perfiles.
    
    Returns:
        List[Dict[str, Any]]: Lista de candidatos con sus detalles.
    """
    return [
        {
            "id": 1,
            "name": "María García López",
            "email": "maria.garcia@email.com",
            "phone": "+34 666 123 456",
            "experience_years": 7,
            "location": "Madrid",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "expertise_summary": "Desarrolladora fullstack con experiencia en APIs REST y microservicios",
            "match_score": 95,
            "llm_justification": "María destaca por su sólida experiencia en desarrollo backend con Python y FastAPI, combinada con conocimientos en infraestructura cloud (AWS) y containerización. Su perfil es excepcional para este rol de Ingeniero Senior.",
            "document_name": "Maria_Garcia_CV.pdf"
        },
        {
            "id": 2,
            "name": "Juan Rodríguez Martínez",
            "email": "juan.rodriguez@email.com",
            "phone": "+34 666 234 567",
            "experience_years": 5,
            "location": "Barcelona",
            "skills": ["JavaScript", "React", "Node.js", "MongoDB", "CSS"],
            "expertise_summary": "Ingeniero Frontend con experiencia en aplicaciones web modernas",
            "match_score": 82,
            "llm_justification": "Juan posee una excelente trayectoria en desarrollo frontend con React y manejo avanzado de JavaScript. Su capacidad para crear interfaces responsivas y su experiencia con herramientas modernas de desarrollo lo hacen ideal para nuestro equipo.",
            "document_name": "Juan_Rodriguez_CV.pdf"
        },
        {
            "id": 3,
            "name": "Ana Fernández Pérez",
            "email": "ana.fernandez@email.com",
            "phone": "+34 666 345 678",
            "experience_years": 8,
            "location": "Valencia",
            "skills": ["DevOps", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "AWS"],
            "expertise_summary": "Especialista DevOps con enfoque en automatización e infraestructura",
            "match_score": 88,
            "llm_justification": "Ana es una profesional experimentada en orquestación de contenedores y Infrastructure as Code. Su dominio de Kubernetes y experiencia en pipelines CI/CD la posicionan como candidata óptima para liderar la transformación digital.",
            "document_name": "Ana_Fernandez_CV.pdf"
        },
        {
            "id": 4,
            "name": "Carlos López Jiménez",
            "email": "carlos.lopez@email.com",
            "phone": "+34 666 456 789",
            "experience_years": 6,
            "location": "Madrid",
            "skills": ["Data Science", "Python", "Machine Learning", "TensorFlow", "SQL"],
            "expertise_summary": "Científico de datos especializado en machine learning y análisis predictivo",
            "match_score": 80,
            "llm_justification": "Carlos demuestra una fuerte formación en machine learning con experiencia práctica en proyectos de análisis predictivo. Su dominio de Python y TensorFlow, junto con sus habilidades estadísticas, lo convierten en un candidato prometedor.",
            "document_name": "Carlos_Lopez_CV.pdf"
        },
        {
            "id": 5,
            "name": "Sofia González Ruiz",
            "email": "sofia.gonzalez@email.com",
            "phone": "+34 666 567 890",
            "experience_years": 4,
            "location": "Bilbao",
            "skills": ["QA Testing", "Automation Testing", "Selenium", "Python", "JIRA"],
            "expertise_summary": "Ingeniera QA con experiencia en automatización de pruebas",
            "match_score": 75,
            "llm_justification": "Sofía presenta un perfil sólido en aseguramiento de calidad con especialidad en automatización de pruebas. Su experiencia con Selenium y Python la califica para proyectos de testing de mediana complejidad.",
            "document_name": "Sofia_Gonzalez_CV.pdf"
        },
        {
            "id": 6,
            "name": "Miguel Sánchez Torres",
            "email": "miguel.sanchez@email.com",
            "phone": "+34 666 678 901",
            "experience_years": 9,
            "location": "Madrid",
            "skills": ["System Architecture", "Microservices", "Java", "Spring Boot", "AWS"],
            "expertise_summary": "Arquitecto de sistemas con experiencia en diseño de arquitecturas escalables",
            "match_score": 92,
            "llm_justification": "Miguel es un arquitecto experimentado con profundo conocimiento en diseño de sistemas distribuidos y microservicios. Su trayectoria en grandes proyectos empresariales lo hace ideal para liderar iniciativas tecnológicas estratégicas.",
            "document_name": "Miguel_Sanchez_CV.pdf"
        }
    ]


def get_mock_query_results(query: str, experience_min: int = 0, 
                          experience_max: int = 20, locations: List[str] = None) -> Dict[str, Any]:
    """
    Simula los resultados de una consulta RAG filtrando candidatos.
    
    Args:
        query (str): Consulta semántica del reclutador
        experience_min (int): Años mínimos de experiencia
        experience_max (int): Años máximos de experiencia
        locations (List[str]): Ubicaciones preferidas
        
    Returns:
        Dict[str, Any]: Resultados simulados de la búsqueda
    """
    all_candidates = get_mock_candidates()
    locations = locations or []
    
    # Filtrar por experiencia
    filtered = [c for c in all_candidates 
                if experience_min <= c["experience_years"] <= experience_max]
    
    # Filtrar por ubicación si se especifican
    if locations:
        filtered = [c for c in filtered if c["location"] in locations]
    
    # Simular ordenamiento por relevancia (score descendente)
    filtered.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "query": query,
        "total_results": len(filtered),
        "candidates": filtered,
        "search_timestamp": datetime.now().isoformat(),
        "metadata": {
            "experience_range": f"{experience_min}-{experience_max} años",
            "locations_filtered": locations if locations else "Todas",
            "processing_time_ms": 245  # Simulado
        }
    }


def get_mock_upload_progress() -> Dict[str, Any]:
    """
    Retorna el estado simulado de subida de documentos.
    
    Returns:
        Dict[str, Any]: Estado de los documentos en subida
    """
    return {
        "files": [
            {"name": "CV_Juan_Perez.pdf", "status": "completed", "progress": 100},
            {"name": "CV_Maria_Lopez.pdf", "status": "processing", "progress": 65},
            {"name": "CV_Carlos_Garcia.pdf", "status": "pending", "progress": 0},
        ],
        "total_processed": 1,
        "total_processing": 1,
        "total_pending": 1,
        "error_messages": []
    }


def get_available_locations() -> List[str]:
    """
    Retorna las ubicaciones disponibles para filtrado.
    
    Returns:
        List[str]: Lista de ubicaciones
    """
    return ["Madrid", "Barcelona", "Valencia", "Bilbao", "Sevilla", "Remoto"]


def get_available_skills() -> List[str]:
    """
    Retorna las habilidades disponibles para búsqueda.
    
    Returns:
        List[str]: Lista de habilidades técnicas
    """
    return [
        "Python", "JavaScript", "Java", "C++", "Go",
        "React", "Vue.js", "Angular",
        "FastAPI", "Django", "Flask", "Spring Boot",
        "PostgreSQL", "MongoDB", "MySQL",
        "Docker", "Kubernetes", "Terraform",
        "AWS", "Azure", "GCP",
        "Machine Learning", "Data Science", "DevOps",
        "System Architecture", "Microservices", "CI/CD"
    ]
