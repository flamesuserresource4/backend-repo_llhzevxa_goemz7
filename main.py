import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Ahadu Travel Solutions API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Health ----------
@app.get("/")
def read_root():
    return {"message": "Ahadu Travel Solutions API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or ("✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error listing collections: {str(e)[:100]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:100]}"
    return response


# ---------- Schemas (request models) ----------
class AppointmentIn(BaseModel):
    full_name: str
    email: str
    phone: str
    destination: Optional[str] = None
    service_type: Optional[str] = None
    date: str
    message: Optional[str] = None


# ---------- Content Endpoints ----------
@app.get("/api/hero")
def get_hero():
    # Return the most recent hero_content document
    try:
        doc = db["hero_content"].find_one(sort=[("_id", -1)])
        if not doc:
            # sensible default
            return {
                "title_en": "Discover Ethiopia with Ahadu Travel",
                "title_am": "ኢትዮጵያን ከአሐዱ ትራቨል ጋር ያግኙ",
                "subtitle_en": "Tailored trips, local expertise, unforgettable experiences.",
                "subtitle_am": "የተስተካከለ ጉብኝት፣ የአካባቢ ሙያዊነት፣ የማይረሱ ተሞክሮዎች።",
                "image_url": "https://images.unsplash.com/photo-1585130401303-cf2fba2b99ef?q=80&w=1600&auto=format&fit=crop"
            }
        # convert ObjectId
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/hero")
def upsert_hero(payload: dict):
    try:
        # simple upsert: insert a new version as latest
        _id = create_document("hero_content", payload)
        return {"id": _id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services")
def list_services():
    try:
        items = get_documents("service")
        for it in items:
            it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blog")
def list_blog_posts():
    try:
        posts = db["blog_post"].find().sort("created_at", -1)
        result = []
        for p in posts:
            p_dict = {
                "id": str(p.get("_id")),
                "title": p.get("title"),
                "slug": p.get("slug"),
                "cover_image": p.get("cover_image"),
                "created_at": p.get("created_at")
            }
            result.append(p_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blog/{slug}")
def get_blog_post(slug: str):
    try:
        post = db["blog_post"].find_one({"slug": slug})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        post["id"] = str(post.pop("_id"))
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Appointments ----------
@app.post("/api/appointments")
def create_appointment(data: AppointmentIn):
    try:
        new_id = create_document("appointment", data)
        return {"id": new_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointments")
def list_appointments(limit: int = 50):
    try:
        docs = get_documents("appointment", limit=limit)
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
