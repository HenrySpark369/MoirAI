import pytest

from app.services.nlp_service import NLPService


def test_calculate_match_score_basic():
    svc = NLPService()
    skills = ["python", "sql", "machine learning"]
    projects = [
        "Sistema de recomendación con python y sklearn",
        "API REST con FastAPI y PostgreSQL"
    ]
    job_desc = "Buscamos un desarrollador Python para API REST, experiencia con bases de datos y ML es valorada."

    score, details = svc.calculate_match_score(skills, projects, job_desc)
    assert 0.0 <= score <= 1.0
    assert isinstance(details.get("matching_projects"), list)
    # Esperamos al menos una coincidencia de proyecto en detalle
    assert len(details["matching_projects"]) >= 1


def test_no_projects_returns_skill_based_score():
    svc = NLPService()
    skills = ["python", "fastapi"]
    projects = []
    job_desc = "Se busca desarrollador Python con experiencia en FastAPI y APIs REST."

    score, details = svc.calculate_match_score(skills, projects, job_desc)
    # Sin proyectos, project_similarity debe ser 0
    assert details["project_similarity"] == 0.0
    assert len(details["matching_projects"]) == 0
    assert 0.0 <= score <= 1.0


def test_no_skills_uses_projects_only():
    svc = NLPService()
    skills = []
    projects = ["API REST con FastAPI y PostgreSQL", "Microservicios en Python"]
    job_desc = "Desarrollador backend, APIs REST, PostgreSQL y experiencia en microservicios."

    score, details = svc.calculate_match_score(skills, projects, job_desc)
    assert details["skill_similarity"] == 0.0
    assert len(details["matching_projects"]) >= 1
    assert 0.0 <= score <= 1.0


def test_weights_override_and_normalization():
    svc = NLPService()
    skills = ["python"]
    projects = ["Proyecto de Machine Learning con python"]
    job_desc = "ML engineer con experiencia en python y modelos de recomendación."

    # Forzar pesos donde skills tengan mayor importancia
    score_default, details_default = svc.calculate_match_score(skills, projects, job_desc)
    score_custom, details_custom = svc.calculate_match_score(
        skills, projects, job_desc, weights={"skills": 0.9, "projects": 0.1}
    )

    # Verificar que los weights usados están normalizados
    w = details_custom["weights_used"]
    assert abs(w["skills"] + w["projects"] - 1.0) < 1e-6

    # Si damos más peso a skills, la puntuación debería reaccionar (no necesariamente menor/greater determinista,
    # pero debe ser un float válido entre 0 y 1)
    assert 0.0 <= score_custom <= 1.0

