from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import router as api_router
from app.database.session import SessionLocal, engine, Base
from app.database.seed import seed_database
from app.database.models import Customer, Order, Product, Inventory, Return, CustomerIssue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables exist and seed data if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        order_count = db.query(Order).count()
        if customer_count == 0 and order_count == 0:
            print("Database empty. Seeding initial OpsPilot dataset...")
            seed_database(db)
            print("Database seeded successfully!")
        else:
            print(f"Database active: {customer_count} customers, {order_count} orders found.")
    except Exception as e:
        print(f"Startup DB error: {e}")
        raise e
    finally:
        db.close()
    yield

app = FastAPI(
    title="OpsPilot AI Business Operations Agent",
    description="Operational agent platform for UrbanCart e-commerce ops management with tool execution, RAG policy retrieval, and human-in-the-loop approvals.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "OpsPilot AI Operations Agent Backend API",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
