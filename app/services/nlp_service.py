"""
Servicios de procesamiento de lenguaje natural (NLP) para análisis de currículums
Extracción de habilidades técnicas, blandas y proyectos
"""
import re
import json
from typing import List, Dict, Tuple
from rapidfuzz import process as rf_process

# Importación opcional de spaCy
try:
    import spacy
    _SPACY_NLP = spacy.load("en_core_web_sm")
except Exception:
    _SPACY_NLP = None

from app.core.config import settings


class NLPService:
    """Servicio principal de procesamiento de lenguaje natural"""
    
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
        self.soft_skills = self._load_soft_skills()
        self.project_patterns = self._load_project_patterns()
        self.stopwords = self._load_stopwords()
    
    def _load_skill_keywords(self) -> set:
        """Cargar palabras clave de habilidades técnicas"""
        return {
            # Lenguajes de programación
            "python", "r", "sql", "java", "javascript", "c++", "c#", "php", "ruby", "go",
            "scala", "kotlin", "swift", "typescript", "matlab", "julia", "rust", "dart",
            
            # Frameworks y librerías
            "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
            "flask", "fastapi", "django", "react", "angular", "vue", "node.js", "express",
            "spring", "hibernate", "laravel", "rails", "bootstrap", "jquery",
            
            # Bases de datos
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
            "oracle", "sqlite", "dynamodb", "neo4j",
            
            # Cloud y DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github",
            "gitlab", "terraform", "ansible", "linux", "unix", "bash", "powershell",
            
            # Data Science y ML
            "machine learning", "deep learning", "nlp", "computer vision", "data mining",
            "data visualization", "statistics", "probability", "regression", "classification",
            "clustering", "neural networks", "random forest", "svm", "naive bayes",
            
            # Herramientas de análisis
            "tableau", "power bi", "excel", "spss", "sas", "qlik", "looker", "grafana",
            "jupyter", "rstudio", "apache spark", "hadoop", "kafka", "airflow",
            
            # Metodologías
            "agile", "scrum", "kanban", "devops", "ci/cd", "tdd", "bdd", "microservices",
            "api rest", "graphql", "soap", "mvc", "mvp", "solid principles"
        }
    
    def _load_soft_skills(self) -> set:
        """Cargar habilidades blandas"""
        return {
            "leadership", "communication", "teamwork", "problem solving", "critical thinking",
            "adaptability", "creativity", "time management", "collaboration", "initiative",
            "analytical thinking", "decision making", "conflict resolution", "negotiation",
            "presentation skills", "public speaking", "project management", "mentoring",
            "customer service", "emotional intelligence", "stress management", "flexibility",
            "innovation", "strategic thinking", "attention to detail", "multitasking",
            "organization", "planning", "research", "writing", "interpersonal skills"
        }
    
    def _load_project_patterns(self) -> List[str]:
        """Cargar patrones regex para identificar proyectos"""
        return [
            r"project[:\- ](.+)",
            r"prototyp(e|o)[:\- ](.+)",
            r"capstone[:\- ](.+)",
            r"thesis[:\- ](.+)",
            r"tesis[:\- ](.+)",
            r"trabajo final[:\- ](.+)",
            r"sistema[:\- ](.+)",
            r"aplicaci[óo]n[:\- ](.+)",
            r"desarrollo[:\- ](.+)",
            r"implementaci[óo]n[:\- ](.+)"
        ]
    
    def _load_stopwords(self) -> set:
        """Cargar palabras de parada"""
        return set("""
            a an the and or for to of in on with from by at as is are was were be been being
            this that these those i me my we our you your he she it they them their his her its
            vs etc about into over under will would could should might may can must have has had
            do does did don't doesn't didn't won't wouldn't couldn't shouldn't might not may not
            cannot mustn't haven't hasn't hadn't doing done
        """.split())
    
    def normalize_text(self, text: str) -> str:
        """Normalizar texto para procesamiento"""
        return re.sub(r"\s+", " ", text.strip().lower())
    
    def extract_skills(self, text: str) -> List[str]:
        """Extraer habilidades técnicas del texto"""
        text_normalized = self.normalize_text(text)
        found_skills = set()
        
        # Búsqueda directa de palabras clave
        for skill in self.skill_keywords:
            if skill in text_normalized:
                found_skills.add(skill)
        
        # Usar spaCy si está disponible para encontrar entidades adicionales
        if _SPACY_NLP:
            doc = _SPACY_NLP(text)
            
            # Extraer entidades tecnológicas
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text) <= 30:
                    ent_lower = ent.text.lower()
                    # Verificar si es una tecnología conocida
                    if any(tech in ent_lower for tech in ["python", "java", "sql", "react", "node"]):
                        found_skills.add(ent_lower)
            
            # Extraer noun chunks relevantes
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if (3 <= len(chunk_text) <= 50 and 
                    not any(stop in chunk_text for stop in self.stopwords) and
                    any(tech in chunk_text for tech in ["machine", "data", "web", "mobile", "cloud"])):
                    found_skills.add(chunk_text)
        
        return self._deduplicate_and_limit(
            sorted(found_skills), 
            settings.MAX_SKILLS_EXTRACTED
        )
    
    def extract_soft_skills(self, text: str) -> List[str]:
        """Extraer habilidades blandas del texto"""
        text_normalized = self.normalize_text(text)
        found_soft_skills = set()
        
        for skill in self.soft_skills:
            if skill in text_normalized:
                found_soft_skills.add(skill)
        
        # Buscar variaciones y sinónimos
        soft_skill_patterns = {
            "leadership": ["lead", "leader", "management", "supervise"],
            "communication": ["communicate", "present", "explain", "articulate"],
            "teamwork": ["team", "collaborate", "cooperation", "group work"],
            "problem solving": ["solve", "solution", "troubleshoot", "resolve"],
            "analytical": ["analyze", "analysis", "analytical", "evaluate"]
        }
        
        for main_skill, variations in soft_skill_patterns.items():
            if any(var in text_normalized for var in variations):
                found_soft_skills.add(main_skill)
        
        return self._deduplicate_and_limit(
            sorted(found_soft_skills),
            settings.MAX_SOFT_SKILLS_EXTRACTED
        )
    
    def extract_projects(self, text: str) -> List[str]:
        """Extraer proyectos del texto"""
        projects = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        for line in lines:
            for pattern in self.project_patterns:
                match = re.search(pattern, line, flags=re.IGNORECASE)
                if match:
                    # Capturar el último grupo que contiene el nombre del proyecto
                    project_name = match.groups()[-1].strip(" -:[]()\t")
                    if 3 <= len(project_name) <= 100:
                        projects.append(project_name)
        
        # Buscar también patrones más generales
        project_indicators = [
            "developed", "built", "created", "designed", "implemented",
            "desarrollé", "construí", "creé", "diseñé", "implementé"
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in project_indicators):
                # Extraer la parte después del indicador
                for indicator in project_indicators:
                    if indicator in line_lower:
                        parts = line.split(indicator, 1)
                        if len(parts) > 1:
                            project_desc = parts[1].strip(" -:.,")
                            if 10 <= len(project_desc) <= 150:
                                projects.append(project_desc)
                        break
        
        return self._deduplicate_and_limit(
            projects,
            settings.MAX_PROJECTS_EXTRACTED
        )
    
    def _deduplicate_and_limit(self, items: List[str], limit: int) -> List[str]:
        """Eliminar duplicados por similitud y limitar cantidad"""
        unique_items = []
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # Verificar similitud con elementos ya añadidos
            if unique_items:
                result = rf_process.extractOne(item, unique_items)
                if result is not None:
                    # RapidFuzz extractOne returns (match, score, index) in v2+
                    match, score, *_ = result
                    if score < 85:  # Threshold para considerar como diferente
                        unique_items.append(item)
                else:
                    unique_items.append(item)
            else:
                unique_items.append(item)
        
        return unique_items[:limit]
    
    def analyze_resume(self, text: str) -> Dict[str, any]:
        """Análisis completo de un currículum"""
        if not text or len(text.strip()) < 50:
            raise ValueError("El texto del currículum es demasiado corto para analizar")
        
        skills = self.extract_skills(text)
        soft_skills = self.extract_soft_skills(text)
        projects = self.extract_projects(text)
        
        # Calcular métricas de confianza
        total_features = len(skills) + len(soft_skills) + len(projects)
        confidence = min(total_features / 10.0, 1.0)  # Máximo 1.0
        
        return {
            "skills": skills,
            "soft_skills": soft_skills,
            "projects": projects,
            "confidence": confidence,
            "total_features_extracted": total_features,
            "text_length": len(text),
            "analysis_metadata": {
                "spacy_available": _SPACY_NLP is not None,
                "skills_found": len(skills),
                "soft_skills_found": len(soft_skills),
                "projects_found": len(projects)
            }
        }
    
    def calculate_match_score(self, student_skills: List[str], student_projects: List[str], 
                            job_requirements: str) -> Tuple[float, Dict[str, List[str]]]:
        """Calcular puntuación de matching entre estudiante y trabajo"""
        job_text = self.normalize_text(job_requirements)
        job_skills = self.extract_skills(job_requirements)
        
        # Calcular intersecciones
        matching_skills = []
        for skill in student_skills:
            if skill.lower() in job_text or any(js in skill.lower() for js in job_skills):
                matching_skills.append(skill)
        
        matching_projects = []
        for project in student_projects:
            project_words = project.lower().split()
            if any(word in job_text for word in project_words if len(word) > 3):
                matching_projects.append(project)
        
        # Calcular puntuación (0-1)
        skill_score = len(matching_skills) / max(len(job_skills), 1) if job_skills else 0
        project_score = len(matching_projects) / max(len(student_projects), 1) if student_projects else 0
        
        # Puntuación ponderada
        final_score = (skill_score * 0.7) + (project_score * 0.3)
        
        return min(final_score, 1.0), {
            "matching_skills": matching_skills,
            "matching_projects": matching_projects
        }


# Instancia global del servicio NLP
nlp_service = NLPService()
