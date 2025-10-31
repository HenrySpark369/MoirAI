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
    
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(**self.tfidf_config).fit_transform([a, b])
            sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
            return max(0.0, min(float(sim), 1.0))
        except Exception:
            # Fallback bag-of-words + coseno
            import math
            a_tokens = a.split()
            b_tokens = b.split()
            vocab = list(set(a_tokens + b_tokens))
            if not vocab:
                return 0.0
            def vec_counts(tokens):
                return [tokens.count(t) for t in vocab]
            va = vec_counts(a_tokens)
            vb = vec_counts(b_tokens)
            dot = sum(x*y for x,y in zip(va, vb))
            denom = math.sqrt(sum(x*x for x in va)) * math.sqrt(sum(y*y for y in vb))
            return float(dot/denom) if denom else 0.0

    def _matching_items(self, items: List[str], text: str) -> List[str]:
        txt = _clean_text(text)
        matches = []
        for it in (items or []):
            if not it:
                continue
            it_clean = _clean_text(it)
            if not it_clean:
                continue
            # coincidencia por frase completa
            if it_clean in txt:
                matches.append(it)
                continue
            # coincidencia por token (primer token que aparezca)
            for tok in it_clean.split():
                if tok and tok in txt:
                    matches.append(it)
                    break
        # deduplicar preservando orden
        seen = set()
        unique = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                unique.append(m)
        return unique
                continue
            else:

    def calculate_match_score(
        self,
        student_skills: List[str],
        student_projects: List[str],
        job_description: str,
        weights: Dict[str, float] = None
    ) -> Tuple[float, Dict]:
        """
        Devuelve (base_score [0..1], details).
        - Valida y trunca inputs para proteger contra entradas maliciosas/excesivas.
        - Weights opcional para ajustar importancias {"skills":0.6, "projects":0.4}
        """
        # -------- Validación y truncado de inputs ----------
        if student_skills is None:
            student_skills = []
        if student_projects is None:
            student_projects = []

        # Forzar listas de strings y truncar cada elemento para evitar DoS/entradas gigantes
        student_skills = [str(s)[:MAX_SKILL_LEN].strip() for s in student_skills if s]
        student_projects = [str(p)[:MAX_PROJECT_LEN].strip() for p in student_projects if p]
        job_text_raw = str(job_description or "")[:MAX_JOB_DESC_LEN]

        # Si no hay datos para comparar, devolver resultado vacío rápido
        if not job_text_raw and not student_skills and not student_projects:
            details_empty = {
                "skill_similarity": 0.0,
                "project_similarity": 0.0,
                "weights_used": {"skills": 0.0, "projects": 0.0},
                "matching_skills": [],
                "matching_projects": []
            }
            return 0.0, details_empty

        # -------- Pesos (validate/normalize) ----------
        w = self.default_weights.copy()
        if weights:
            # proteger contra valores no numéricos y sólo aceptar claves esperadas
            for k in ("skills", "projects"):
                if k in weights:
                    try:
                        w[k] = float(weights[k])
                    except Exception:
                        # ignorar valores inválidos y conservar default
                        pass
        # Normalizar para sumar 1.0 (proteger contra división por 0)
        total = max(1e-9, w.get("skills", 0) + w.get("projects", 0))
        w["skills"] = w.get("skills", 0) / total
        w["projects"] = w.get("projects", 0) / total

        # -------- Preparar textos para similitud ----------
        skills_text = self._list_to_text(student_skills)
        projects_text = self._list_to_text(student_projects)
        job_clean = _clean_text(job_text_raw)

        # -------- Calcular similitudes (TF-IDF o fallback) ----------
        skill_sim = self._tfidf_cosine(skills_text, job_clean) if skills_text else 0.0
        project_sim = self._tfidf_cosine(projects_text, job_clean) if projects_text else 0.0

        base_score = (skill_sim * w["skills"]) + (project_sim * w["projects"])
        base_score = max(0.0, min(base_score, 1.0))

        # -------- Matching por items (deduplicado dentro de la función) ----------
        matching_skills = self._matching_items(student_skills, job_clean)
        matching_projects = self._matching_items(student_projects, job_clean)

        # -------- Truncar elementos devueltos para evitar fuga de texto largo ----------
        def _truncate_return_list(lst):
            out = []
            for it in (lst or []):
                s = str(it) or ""
                if len(s) > MAX_RETURN_ITEM_LEN:
                    s = s[:MAX_RETURN_ITEM_LEN] + "..."
                out.append(s)
            return out

        details = {
            "skill_similarity": round(float(skill_sim), 6),
            "project_similarity": round(float(project_sim), 6),
            "weights_used": w,
            "matching_skills": _truncate_return_list(matching_skills),
            "matching_projects": _truncate_return_list(matching_projects),
        }

        return base_score, details


# instancia compartida
nlp_service = NLPService()

