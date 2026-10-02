# 📚 BookNest — Backend API

A **FastAPI** backend for **BookNest**, a platform where users can list, discover, and swap books with each other. Features include book management, swap request workflows, wishlists, real-time chat via WebSockets, and user stats.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.128+ |
| ORM | SQLModel + SQLAlchemy |
| Database | PostgreSQL (via Supabase) |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Real-time | WebSockets |
| Server | Uvicorn |
| Containerization | Docker |

---

## 📂 Project Structure

```
booknest_backend_fastapi/
├── main.py                 # App entry point, router registration, CORS config
├── database.py             # DB engine, session, and all SQLModel table models
├── schemas.py              # Pydantic request/response schemas
├── connectionManager.py    # WebSocket connection manager
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
├── .env                    # Environment variables (not committed)
│
├── routers/                # Route definitions (thin controllers)
│   ├── authenticate.py     # Login / token endpoints
│   ├── user.py             # User CRUD
│   ├── book.py             # Book CRUD + search
│   ├── booklog.py          # Book log + swap requests
│   ├── wishlist.py         # Wishlist management
│   ├── websocket.py        # Real-time chat via WebSocket
│   ├── stats.py            # User statistics
│   └── messages.py         # Chat message history
│
├── repository/             # Business logic layer
│   ├── authenticate.py
│   ├── book.py
│   ├── booklog.py
│   ├── user.py
│   └── wishlist.py
│
└── security/               # Auth utilities
    ├── hashing.py          # Password hashing (bcrypt)
    ├── oauth2.py           # JWT dependency (get_current_user)
    └── token.py            # Token creation & verification
```

---

## 🗄️ Database Models

| Model | Description |
|---|---|
| `User` | Registered users with name, email, password, phone, address |
| `Book` | Books listed by users with name, author, genre |
| `BookLog` | Log of a book being associated with a user |
| `Request` | Swap requests between two users (offered ↔ wanted book) |
| `SuccessfulSwapHistory` | Completed swap records |
| `Wishlist` | Books a user wants to find/swap for |
| `ChatMessage` | In-app chat messages tied to a swap request |

---

## 🔌 API Endpoints

### 🔐 Auth — `/`
| Method | Path | Description |
|---|---|---|
| POST | `/login` | Authenticate and receive JWT token |

### 👤 Users — `/user`
| Method | Path | Description |
|---|---|---|
| POST | `/user/` | Register a new user |
| GET | `/user/` | Get current user profile |
| PUT | `/user/` | Update profile (name, phone, address) |

### 📖 Books — `/book`
| Method | Path | Description |
|---|---|---|
| POST | `/book/` | Add a new book listing |
| GET | `/book/` | Get current user's books |
| GET | `/book/all` | Explore all books (supports `?q=` search & `?genre=` filter) |
| GET | `/book/{id}` | Get a specific book by ID |
| DELETE | `/book/{id}` | Delete a book listing |

### 🔁 Book Logs & Swaps — `/booklog`
| Method | Path | Description |
|---|---|---|
| POST | `/booklog/{book_id}` | Create a book log entry |
| GET | `/booklog/` | Browse marketplace (supports `?q=` and `?genre=`) |
| GET | `/booklog/history/all` | Get detailed swap history |
| POST | `/booklog/request` | Send a swap request |
| GET | `/booklog/request` | View pending requests |
| PUT | `/booklog/request/{id}` | Accept or decline a swap request |

### ❤️ Wishlist — `/wishlist`
| Method | Path | Description |
|---|---|---|
| POST | `/wishlist/` | Add a book to wishlist |
| GET | `/wishlist/` | Get user's wishlist |
| DELETE | `/wishlist/{id}` | Remove item from wishlist |

### 💬 Messages — `/messages`
| Method | Path | Description |
|---|---|---|
| GET | `/messages/{request_id}` | Get chat history for a swap request |

### 📊 Stats — `/stats`
| Method | Path | Description |
|---|---|---|
| GET | `/stats/` | Get stats for the current user |

### 🔴 WebSocket — `/ws`
| Type | Path | Description |
|---|---|---|
| WS | `/ws/{user_id}` | Real-time bidirectional chat |

**WebSocket payload format:**
```json
{
  "request_id": 1,
  "receiver_id": 2,
  "content": "Hey, want to swap?"
}
```

---

## ⚙️ Setup & Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL database (or a [Supabase](https://supabase.com) project)

### 1. Clone & create virtual environment
```bash
git clone <repo-url>
cd booknest_backend_fastapi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the root directory:
```env
DATABASE=postgresql://user:password@host:port/dbname
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

The API will be live at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

---

## 🐳 Running with Docker

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d
```

The server will be available at `http://localhost:8000`.

---

## 🔒 Authentication

This API uses **JWT Bearer tokens**.

1. Call `POST /login` with `username` (email) and `password` as form data.
2. Copy the `access_token` from the response.
3. Pass it as a header on all protected routes:
   ```
   Authorization: Bearer <your_token>
   ```

---

## 🌐 CORS

CORS is configured to allow **all origins** (`*`) for development. Update `allow_origins` in `main.py` before going to production.

---

## ☁️ Deployment

This project is designed for deployment on **[Render](https://render.com)**:

- Set the `DATABASE` environment variable in the Render dashboard pointing to your PostgreSQL connection string.
- The `Dockerfile` is ready to use for Render's Docker-based deployment.
- The app auto-creates all database tables on startup via `create_db_and_tables()`.
