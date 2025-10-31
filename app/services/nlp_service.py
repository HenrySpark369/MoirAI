from typing import List, Tuple, Dict
import re
import unicodedata


# Reemplaza o añade al inicio del módulo (funciones y constantes):
MAX_SKILL_LEN = 200
MAX_PROJECT_LEN = 2000
MAX_JOB_DESC_LEN = 50000
MAX_RETURN_ITEM_LEN = 300

def _clean_text(text: str) -> str:
    if not text:
        return ""
    txt = str(text).strip().lower()

    # Mapear tokens técnicos antes de quitar caracteres especiales
    technical_map = {
        "c++": "cpp",
        "c#": "csharp",
        "node.js": "nodejs",
        "nodejs": "nodejs",
        " r ": " r ",  # preservar token r
    }
    for k, v in technical_map.items():
        txt = txt.replace(k, v)

    # Normalizar unicode y eliminar acentos
    import unicodedata
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))

    # Mantener solo letras, números y espacios
    import re
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

# Asegúrate de que tfidf_config usa stop_words = None
self.tfidf_config = {"ngram_range": (1, 2), "stop_words": None}


class NLPService:
    """
    Servicio NLP para matching entre Student y JobItem.
    - Usa TF-IDF + coseno si sklearn está disponible (importación lazy).
    - Por defecto da más peso a 'projects' (experiencia).
    """

    def __init__(self):
        # Por defecto consideramos proyectos como experiencia con más peso
        self.default_weights = {"skills": 0.35, "projects": 0.65}
        # Config TF-IDF
        self.tfidf_config = {
            "ngram_range": (1, 2),
            "stop_words": "spanish"
        }

    def _list_to_text(self, items: List[str]) -> str:
        return " ".join([_clean_text(i) for i in (items or []) if i])

    def _tfidf_cosine(self, a: str, b: str) -> float:
        a = _clean_text(a)
        b = _clean_text(b)
        if not a or not b:
            return 0.0

        # Intentar importación lazy de sklearn para evitar problemas en entornos sin dependencias
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(**self.tfidf_config).fit_transform([a, b])
            sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
            return float(sim)
        except Exception:
            # Fallback: coseno sobre conteos (bag-of-words)
            a_tokens = a.split()
            b_tokens = b.split()
            vocab = list(set(a_tokens + b_tokens))
            def vec_counts(tokens):
                return [tokens.count(t) for t in vocab]
            va = vec_counts(a_tokens)
            vb = vec_counts(b_tokens)
            dot = sum(x * y for x, y in zip(va, vb))
            import math
            denom = math.sqrt(sum(x * x for x in va)) * math.sqrt(sum(y * y for y in vb))
            return float(dot/denom) if denom else 0.0

    def _matching_items(self, items: List[str], text: str) -> List[str]:
        txt = _clean_text(text)
        matches = []
        for it in (items or []):
            if not it:
                continue
            it_clean = _clean_text(it)
            # coincidencia por frase completa o tokens
            if it_clean in txt:
                matches.append(it)
            else:
                for tok in it_clean.split():
                    if tok and tok in txt:
                        matches.append(it)
                        break
        return matches

    def calculate_match_score(
        self,
        student_skills: List[str],
        student_projects: List[str],
        job_description: str,
        weights: Dict[str, float] = None
    ) -> Tuple[float, Dict]:
        """
        Devuelve (base_score [0..1], details).
        - student_skills: lista de skills (strings)
        - student_projects: lista de descripciones de proyectos (strings)
        - job_description: texto del job (title + description)
        - weights: opcional para ajustar importancias {"skills":0.6, "projects":0.4}
        """
        w = self.default_weights.copy()
        if weights:
            w.update(weights)
        # normalizar
        total = max(1e-9, w.get("skills", 0) + w.get("projects", 0))
        w["skills"] = w.get("skills", 0) / total
        w["projects"] = w.get("projects", 0) / total

        skills_text = self._list_to_text(student_skills)
        projects_text = self._list_to_text(student_projects)
        job_text = _clean_text(job_description or "")

        skill_sim = self._tfidf_cosine(skills_text, job_text) if skills_text else 0.0
        project_sim = self._tfidf_cosine(projects_text, job_text) if projects_text else 0.0

        base_score = (skill_sim * w["skills"]) + (project_sim * w["projects"])
        base_score = max(0.0, min(base_score, 1.0))

        matching_skills = self._matching_items(student_skills, job_text)
        matching_projects = self._matching_items(student_projects, job_text)

        details = {
            "skill_similarity": round(skill_sim, 4),
            "project_similarity": round(project_sim, 4),
            "weights_used": w,
            "matching_skills": matching_skills,
            "matching_projects": matching_projects
        }

        return base_score, details


# instancia compartida
nlp_service = NLPService()

