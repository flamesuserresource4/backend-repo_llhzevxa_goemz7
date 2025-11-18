"""
Database Schemas for Ahadu Travel Solutions

Each Pydantic model represents a collection in your MongoDB database.
Collection name is the lowercase of the class name.

These schemas mirror the intended Supabase/Postgres tables so we can
prototype quickly in this environment.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Hero_content(BaseModel):
    """
    Collection: "hero_content"
    Stores localized hero copy and image for the homepage
    """
    title_en: str = Field(...)
    title_am: str = Field(...)
    subtitle_en: str = Field(...)
    subtitle_am: str = Field(...)
    image_url: Optional[str] = Field(None)


class Service(BaseModel):
    """
    Collection: "service"
    """
    title: str
    description: str
    image_url: Optional[str] = None


class Blog_post(BaseModel):
    """
    Collection: "blog_post"
    """
    title: str
    slug: str
    cover_image: Optional[str] = None
    content: str
    author_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Appointment(BaseModel):
    """
    Collection: "appointment"
    """
    full_name: str
    email: str
    phone: str
    destination: Optional[str] = None
    service_type: Optional[str] = None
    date: str
    message: Optional[str] = None


class User(BaseModel):
    """
    Collection: "user"
    Minimal user model to allow role assignment later if needed
    """
    email: str
    role: Optional[str] = Field(default="editor", description="admin|editor")
