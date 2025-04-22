# **LLM-Powered Q&A System**

This repository contains the **Source Code** for an interactive Q&A system integrated with **Google Gemini's LLM API**. It provides structured responses to user queries.

---

## 📌 Features

✅ **FastAPI RESTful API** – Clean, documented endpoints  
✅ **Gemini LLM Integration** – Free-tier AI responses  
✅ **Prompt Engineering** – Optimized for structured answers (e.g., visa requirements)  
✅ **Pydantic Validation** – Type-safe request/response handling  
✅ **Async HTTP Requests** – Non-blocking API calls via `httpx`  
✅ **Swagger UI** – Interactive API documentation at `/docs`

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/Okemwag/PawaIt.git
cd PawaIt
```

### 2. Install Dependencies

```bash
uv init
```

### 3. Configure Environment

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run the Backend

```bash
uv run fastapi dev 
```

Access:

- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)  



## 🔮 Future Improvements

- [ ] Add caching (Redis) for frequent queries  
- [ ] Support multiple LLM providers (OpenAI, Gemini)  
- [ ] Rate limiting (e.g., `fastapi-limiter`)  
- [ ] Database integration for query history (PostgreSQL)



Author: Okemwag  


---

### 🙌 Credits

- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework   
