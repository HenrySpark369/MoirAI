#   Casos de Uso (Use Cases) del MVP

-   Registro y Perfilado Inteligente del Estudiante
    -   El Estudiante centraliza su perfil académico y proyectos (RF 1.0). La API ingesta el currículum o perfil, y los modelos de NLP (Integración de modelos NLP, Tarea S3) analizan e infieren sus habilidades blandas y técnicas (RF 2.0), almacenando el perfil estructurado.

-   Búsqueda y Matchmaking Automatizado
    -   El Reclutador de la empresa sube o introduce los requisitos de una vacante (o aplica filtros avanzados, RF 4.0). La API ejecuta el Algoritmo de Matchmaking (Modelo de clasificación, Tarea S4) para identificar y rankear a los estudiantes cuyos perfiles (incluyendo habilidades blandas inferidas) son más compatibles con la vacante (RF 3.0).

-   Gestión Segura de la Información
    -   El Administrador gestiona el acceso y los permisos de nuevos usuarios (Empresas o Tutores) (RF 8.0). La API aplica protocolos de autenticación (OAuth 2.0) y asegura que toda la información sensible del alumnado (historiales académicos, perfiles) esté protegida mediante cifrado en tránsito (TLS 1.3) (RNF 3.0).

#   Historias de Usuario Esenciales del MVP

-   Empresa Colaboradora
    -   COMO un líder de equipo, QUIERO que la API utilice modelos de procesamiento de lenguaje natural (NLP) para analizar currículums e inferir competencias blandas, PARA encontrar candidatos con potencial de colaboración y adaptabilidad.
    -   COMO un reclutador, QUIERO filtrar perfiles por habilidades técnicas específicas y proyectos prototípicos completados, PARA identificar rápidamente a los candidatos más alineados.

-   Estudiante UNRC
    -   COMO un estudiante, QUIERO centralizar mi perfil académico, proyectos prototípicos y habilidades blandas en un solo repositorio, PARA presentar una candidatura completa y dinámica.
    -   COMO un estudiante, QUIERO recibir notificaciones de coincidencias entre mi perfil y las oportunidades laborales, PARA agilizar mi proceso de inserción laboral.

-   Administrador UNRC
    -   COMO el administrador, QUIERO gestionar roles y permisos de acceso para empresas y estudiantes, PARA asegurar el cumplimiento de las políticas de seguridad y la protección de los datos.
    -   COMO el administrador, quiero visualizar métricas de KPI's sobre el porcentaje de coincidencias y la tasa de colocación de nuestros egresados, PARA evaluar el impacto de la API en la empleabilidad y alinear nuestros planes curriculares con las demandas del mercado

#   Especificaciones Funcionales para el MVP

-   Gestión de Perfil Centralizado
    -   El sistema deberá exponer un endpoint seguro para la ingesta y actualización de datos estructurados (académicos y extracurriculares) y archivos de currículum del estudiante.

-   Análisis de Currículums (NLP)
    -   La API deberá procesar el texto de los currículums utilizando modelos NLP y redes neuronales para extraer y categorizar habilidades técnicas explícitas e inferir competencias blandas.

-   Algoritmo de Matchmaking
    -   El módulo de clasificación deberá generar un puntaje de compatibilidad (matchmaking) entre un perfil de estudiante y una vacante, basado en las habilidades inferidas y los requisitos empresariales.

-   Filtros Avanzados (API)◊v
    -  La API deberá permitir consultas mediante filtros booleanos y de texto sobre habilidades técnicas, proyectos prototípicos y nivel de experiencia (para alimentar Búsqueda y Matchmaking Automatizado).

-   Notificaciones de Coincidencia
    -   El sistema deberá generar y enviar notificaciones automáticas al estudiante cuando se detecte una coincidencia de alta relevancia (matchmaking).

-   Gestión de Roles y Permisos
    -   El sistema deberá autenticar a los usuarios (Estudiante, Empresa, Administrador) y aplicar control de acceso por roles para proteger la información sensible, implementado mediante protocolos de OAuth 2.0.

#   Especificaciones No Funcionales (RNF) Críticas para el MVP

-   Arquitectura y Tecnología
    -   La API debe construirse sobre FastAPI en Python, utilizando PostgresSQL como base de datos, y librerías clave de IA (sklearn, hugging face) así como de visualización (Streamlit).

-   Rendimiento
    -   Los tiempos de respuesta del algoritmo de matchmaking (RF 3.0) deben ser óptimos, justificando la selección de herramientas de Cómputo de Alto Rendimiento (HPC).

-   Protección de Datos
    -   Implementación obligatoria de cifrado en tránsito (TLS 1.3) para proteger el historial académico y la información sensible del alumnado

-   Cumplimiento Regulatorio (Adherencia)
    -   La arquitectura y los procesos deben adherirse a la LFPDPPP y los estándares ISO/IEC 27001.

#   
