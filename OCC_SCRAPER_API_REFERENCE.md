# 📡 OCC.COM.MX API & DATOS - REFERENCIA TÉCNICA

**Fuente:** Análisis de curl provided  
**Fecha:** 11 Nov 2025  
**Estado:** Completo

---

## 🔗 ENDPOINTS IDENTIFICADOS

### 1. **Homepage + Search Results**

**GET** `https://www.occ.com.mx/empleos/de-{skill}/en-{location}/`

```
Ejemplo: https://www.occ.com.mx/empleos/de-python/en-ciudad-de-mexico/
```

**Response:** HTML con estructura:
```html
<div class="job-grid">
  <div class="job-card" data-job-id="OCC-20834631">
    <h2 class="job-title">Python Developer</h2>
    <div class="company">Tech Corp</div>
    <div class="location">Mexico City</div>
    <div class="salary">$60,000-80,000</div>
    <div class="job-type">Full-time | Hybrid</div>
    <button class="apply">Apply</button>
  </div>
</div>
```

**Headers Requeridos:**
```
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: es-MX,es;q=0.9,en;q=0.8
Cache-Control: no-cache
Pragma: no-cache
User-Agent: Mozilla/5.0 (...)
Cookies: occtrsid, __cf_bm, Responsive
```

---

### 2. **Búsqueda AJAX - Offers List**

**POST** `https://collector.occ.com.mx/offer/search`

**Content-Type:** `application/x-www-form-urlencoded`

**Body (URL-encoded JSON):**
```json
{
  "ut": "",                          // User token
  "isea": "ECA1027B5469...",         // Search ID (hashed)
  "iu": "",                           // User ID
  "ic": "",                           // Cookie ID
  "ip": "2C1710479D129131",          // IP
  "seawor": "python",                 // Search word
  "icare": "7517F155D77BACC7",       // Category ID
  "icate": "7517F155D77BACC7",       // Subcategory ID
  "iloce": "B5ABFFA97F3173A3",       // Location ID
  "icite": "7517F155D77BACC7",       // City ID
  "ipubdat": "0",                     // Publish date
  "isale": "",                        // Salary
  "icontype": "7517F155D77BACC7",     // Contact type
  "iemptype": "7517F155D77BACC7",     // Employment type
  "dise": "",                         // Disabled
  "o": "relevance",                   // Sort (relevance, date)
  "numres": "20",                     // Num results
  "pn": "1",                          // Page number
  "mv": "",                           // Market value
  "oin": [                            // Offer IDs
    {"oi": "E82064C6D3829B3B61373E686DCF3405", "s": 0, "p": 1},
    {"oi": "54C699184212F8AD61373E686DCF3405", "s": 0, "p": 2}
  ]
}
```

**Response:**
```json
{
  "offers": [
    {
      "id": "E82064C6D3829B3B61373E686DCF3405",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Mexico City",
      "salary": "60000-80000",
      "currency": "MXN",
      "type": "full-time",
      "mode": "hybrid",
      "publishedAt": "2025-11-06T10:30:00Z"
    }
  ],
  "total": 342,
  "page": 1,
  "pageSize": 20,
  "hasMore": true
}
```

---

### 3. **Detalle de Oferta**

**POST** `https://collector.occ.com.mx/offer/detail`

**Body:**
```json
{
  "oi": "E82064C6D3829B3B61373E686DCF3405",
  "icare": "7517F155D77BACC7",
  "icate": "EC2456E4BF054B47",
  "iloce": "B5ABFFA97F3173A3",
  "icite": "7517F155D77BACC7",
  "pubdat": "76E3F8DF6D68DFAC00BA58744F6675C6AB5F23BA41BFE4DF",
  "isale": "7517F155D77BACC7",
  "iconttype": "A9A3BEA2DB08F1B2",
  "iemptype": "469814F59E4D6F04",
  "dise": "7517F155D77BACC7",
  "iexpe": "7517F155D77BACC7"
}
```

**Response (HTML):**
```html
<div class="job-detail">
  <h1>Senior Python Developer</h1>
  <div class="company-info">
    <img src="company-logo-url" alt="Tech Corp">
    <h2>Tech Corp</h2>
    <a href="company-page">Visit Company</a>
  </div>
  
  <section class="requirements">
    <h3>Requisitos</h3>
    <ul>
      <li>5+ años experiencia en Python</li>
      <li>FastAPI knowledge</li>
      <li>PostgreSQL</li>
      <li>Docker & Kubernetes</li>
      <li>AWS</li>
    </ul>
  </section>
  
  <section class="responsibilities">
    <h3>Responsabilidades</h3>
    <ul>
      <li>Diseñar y desarrollar backend services</li>
      <li>Code reviews y mentoring</li>
    </ul>
  </section>
  
  <section class="benefits">
    <h3>Beneficios</h3>
    <ul>
      <li>Health insurance</li>
      <li>Home office</li>
      <li>Training budget</li>
    </ul>
  </section>
  
  <section class="contact">
    <p><strong>Email:</strong> careers@techcorp.com</p>
    <p><strong>Phone:</strong> +52 55 1234 5678</p>
  </section>
</div>
```

---

### 4. **Análisis Básico (Kinesis)**

**POST** `https://www.occ.com.mx/ajaxkinesis/basicinfo`

**Headers:**
```
X-Requested-With: XMLHttpRequest
Content-Type: application/json
```

**Body:**
```json
{
  "oi": "20834631",
  "icare": "0",
  "icate": "17",
  "iloce": "21957",
  "icite": "0",
  "pubdat": "2025-11-06T00:00:00Z",
  "isale": "0",
  "iconttype": "-1",
  "iemptype": "1",
  "dise": ""
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "views": 342,
    "clicks": 89,
    "applications": 12,
    "featured": false,
    "promoted": false
  }
}
```

---

## 🔐 PARÁMETROS MAPEADOS

| Parámetro | Significado | Valores Comunes | Mapeo a Nuestro Sistema |
|-----------|------------|-----------------|----------------------|
| `icare` | Category ID | "17" (IT), "20" (Admin) | `category` |
| `icate` | Subcategory ID | "17", "20" | `sub_category` |
| `iloce` | Location ID | "21957" (CDMX) | `location_normalized` |
| `icite` | City ID | "0", "21957" | `city_id` |
| `iemptype` | Employment Type | "1" (FT), "2" (PT) | `job_type` |
| `iconttype` | Contact Type | "-1", "0", "1" | `contact_type` |
| `isale` | Salary Type | "0" (no), "1" (yes) | `has_salary` |
| `o` | Sort Order | "relevance", "date" | `sort_by` |

---

## 🎯 ESTRUCTURA DE DATOS EXTRAÍDA

### **JobOffer Completo (desde nuestro análisis)**

```python
@dataclass
class JobOfferComplete:
    # IDs
    job_id: str                    # "OCC-20834631"
    external_job_id: str           # De OCC
    
    # Básico
    title: str                     # "Senior Python Developer"
    company: str                   # "Tech Corp"
    location: str                  # "Mexico City"
    
    # Detalles
    description: str               # Full description
    requirements: List[str]        # ["5+ años Python", "FastAPI", ...]
    responsibilities: List[str]    # ["Diseñar backend", "Code reviews", ...]
    benefits: List[str]            # ["Health insurance", ...]
    
    # Extración NLP
    skills: List[str]             # ["Python", "FastAPI", "PostgreSQL", ...]
    soft_skills: List[str]        # ["Liderazgo", "Comunicación", ...]
    experience_level: str         # "Senior", "Mid", "Junior"
    education_required: str       # "Bachelor's in CS"
    
    # Trabajo
    work_mode: str                # "hybrid", "remote", "onsite"
    job_type: str                 # "full-time", "part-time"
    contract_type: str            # "permanent", "temporal"
    work_schedule: str            # "9-5", "Flexible"
    
    # Salario
    salary_min: Optional[float]   # 60000
    salary_max: Optional[float]   # 80000
    currency: str                 # "MXN"
    salary_period: str            # "monthly", "yearly"
    
    # Contacto (PII)
    contact_email: str            # careers@techcorp.com
    contact_phone: Optional[str]  # +52 55 1234 5678
    contact_name: Optional[str]   # "John Doe" (si aparece)
    
    # Metadata
    company_verified: bool        # True/False
    is_featured: bool             # True/False
    is_promoted: bool             # True/False
    company_logo: Optional[str]   # URL
    
    # Timestamps
    published_at: datetime        # Fecha publicación
    created_at: datetime          # Cuando scrapeamos
    category: str                 # "IT", "Administración"
    subcategory: str              # "Programación", "Recursos Humanos"
    
    # OCC-específico
    occ_category_id: str          # "17"
    occ_subcategory_id: str       # "17"
    occ_location_id: str          # "21957"
    occ_city_id: str              # "0"
```

---

## 🛡️ SEGURIDAD - DATOS A PROTEGER

**PII (Personally Identifiable Information) en OCC:**

1. **Email:** careers@techcorp.com
   - ✅ Encriptar en BD
   - ✅ Hash para búsqueda
   - ❌ NO exponer en API público

2. **Teléfono:** +52 55 1234 5678
   - ✅ Encriptar en BD
   - ✅ Hash para búsqueda  
   - ❌ NO exponer en API público

3. **Nombre del Recruiter:** (si aparece)
   - ✅ NO almacenar si es posible
   - Si es necesario: Encriptar

4. **Ubicación exacta:**
   - ✅ OK: "Mexico City"
   - ❌ NOT OK: "Avenida Paseo de la Reforma 505, Mexico City"

---

## ⚡ RATE LIMITING OCC

**Observaciones de los curl:**

1. **CloudFlare Protection:**
   - Requiere `User-Agent` válido
   - Requiere `Accept-Encoding`
   - Puede requerir cookies

2. **Recommended Headers:**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-MX,es;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}
```

3. **Delays Recomendados:**
   - Mínimo entre requests: 1-2 segundos
   - Máximo: 5 segundos
   - Con variable aleatorio: 1.5-3 segundos

---

## 🔄 FLUJO DE SCRAPING RECOMENDADO

```
┌─────────────────────────┐
│ 1. Homepage GET         │
│ (Session init)          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 2. POST /offer/search   │
│ (Get IDs de ofertas)    │
│ Retorna: ~20 jobs      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 3. POST /offer/detail   │
│ (Para cada job ID)      │
│ Retorna: HTML detail    │
│ ⏱️ 1-2s delay entre     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 4. HTMLParser           │
│ (Parse + Extracción)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 5. NLPService           │
│ (Extrae skills)         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 6. Encryption           │
│ (Encripta PII)          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 7. DB Store             │
│ (Almacena JobPosting)   │
└─────────────────────────┘
```

---

## 📊 VOLÚMENES ESTIMADOS

```
OCC.com.mx típicamente tiene:
- ~50,000-100,000 ofertas activas
- ~1,000-2,000 nuevas diarias
- ~100-200 por skill popular (Python, JavaScript, etc.)
- ~500-1,000 por ubicación grande (CDMX)

Para scraping eficiente:
- Scrape top 5 skills: Python, JavaScript, Java, C#, .NET
- Top 5 locations: CDMX, Remote, Monterrey, Guadalajara, Querétaro
- 50 ofertas por combinación = 1,250 nuevas/ciclo
- Ciclo recomendado: cada 4-6 horas
```

---

## ✅ VALIDACIÓN DE DATOS

Campos requeridos:
```python
required_fields = [
    "title",           # min 4 chars
    "company",         # min 1 char
    "location",        # min 1 char
    "description",     # min 10 chars
    "job_id",          # unique
]

required_one_of = [
    ["contact_email", "contact_phone"],
]

constraints = {
    "title": (4, 200),
    "description": (10, 5000),
    "salary_min": (0, 999999),
    "salary_max": (0, 999999),
}
```

---

**FIN DE REFERENCIA TÉCNICA** 📡
