# 📚 Lector Doc Extractor

Dashboard web para extraer conocimiento estructurado de libros y documentos (PDF, EPUB, TXT) usando **Google Gemini AI** + **LangExtract**.

![Tech Stack](https://img.shields.io/badge/Gemini-AI-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![React](https://img.shields.io/badge/React-18-61DAFB) ![Tailwind](https://img.shields.io/badge/TailwindCSS-3-38BDF8)

---

## ✨ ¿Qué hace?

Sube un PDF, EPUB o TXT y la IA genera **5 tipos de extracción en paralelo**:

| Módulo | Descripción |
|--------|-------------|
| 🎯 **Mensaje Central** | Tesis del autor, argumentos clave y evidencia de soporte |
| 💡 **Ideas Principales** | Ideas jerarquizadas, argumentos y conclusiones |
| 📱 **Redes Sociales** | Posts para X/Twitter, captions Instagram y hooks virales |
| 🎓 **Material de Clase** | Conceptos, definiciones, ejemplos y preguntas de discusión |
| 🤖 **Base de Conocimiento** | Hechos, explicaciones y Q&A para chatbot educativo |

---

## 🛠️ Stack Tecnológico

- **Frontend:** React 18 + Vite + TailwindCSS
- **Backend:** FastAPI (Python) + Uvicorn
- **IA:** Google Gemini 2.5 Flash via LangExtract
- **Procesamiento:** Asíncrono con BackgroundTasks (FastAPI)

---

## 🚀 Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/pjvalverde/Lector_Doc_Extractor.git
cd Lector_Doc_Extractor
```

### 2. Configurar API Key de Gemini

```bash
cp .env.example .env
# Edita .env y añade tu GOOGLE_API_KEY
# Obtén la tuya en: https://aistudio.google.com/apikey
```

### 3. Instalar dependencias Python

```bash
pip install -e .                              # instala langextract y sus dependencias
pip install -r api/requirements.txt          # instala FastAPI, uvicorn, etc.
pip install pymupdf ebooklib beautifulsoup4  # lectura de PDF/EPUB
```

### 4. Instalar dependencias Frontend

```bash
cd frontend
npm install
cd ..
```

### 5. Ejecutar la aplicación

**Terminal 1 — Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Abre tu navegador en **http://localhost:5173**

---

## 📁 Estructura del Proyecto

```
Lector_Doc_Extractor/
├── api/
│   ├── main.py              # FastAPI backend con todos los endpoints
│   └── requirements.txt     # Dependencias del API
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ProcessingView.jsx
│   │   │   └── results/
│   │   │       ├── ResultsDashboard.jsx
│   │   │       ├── CentralMessageSection.jsx
│   │   │       ├── MainIdeasSection.jsx
│   │   │       ├── SocialMediaSection.jsx
│   │   │       ├── TeachingSection.jsx
│   │   │       └── KnowledgeBaseSection.jsx
│   │   ├── api/client.js    # Axios API client
│   │   ├── App.jsx          # Root component con state management
│   │   └── index.css        # TailwindCSS + estilos globales
│   ├── package.json
│   └── vite.config.js
├── book_reader.py           # Lector de PDF/EPUB/TXT
├── extraction_tasks.py      # 5 tareas de extracción (prompts + ejemplos)
├── extract_books.py         # Pipeline CLI original
├── generate_report.py       # Generador de reportes Markdown
├── .env.example             # Template de variables de entorno
└── REPORTE_PROYECTO.md      # Reporte técnico del proyecto
```

---

## 🔌 API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/jobs` | Subir archivo e iniciar extracción |
| `GET`  | `/api/jobs/{job_id}` | Consultar estado del job |
| `GET`  | `/api/jobs/{job_id}/download/markdown` | Descargar reporte `.md` |
| `GET`  | `/api/jobs/{job_id}/download/json` | Descargar knowledge base `.json` |
| `GET`  | `/api/health` | Health check |

---

## 📊 Capacidad del Sistema

- **Modelo:** `gemini-2.5-flash` (1M tokens de contexto)
- **Equivale a:** ~700,000 palabras o 3-4 libros estándar simultáneos
- **Formatos soportados:** PDF, EPUB, TXT

---

## 🗺️ Roadmap

- [ ] Autenticación de usuarios
- [ ] Historial de documentos procesados
- [ ] Arquitectura RAG para bibliotecas completas (GB de texto)
- [ ] Soporte multimodal para libros científicos con fórmulas
- [ ] Chat interactivo con el libro (chatbot educativo)
- [ ] Deploy en cloud (Docker + Cloud Run)

---

## 📄 Licencia

MIT © 2026 pjvalverde
