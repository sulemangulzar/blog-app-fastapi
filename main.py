from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.post import router as post_router

app = FastAPI(title="Blog App API")
app.include_router(auth_router)
app.include_router(post_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title + " - Scalar Docs",
    )
