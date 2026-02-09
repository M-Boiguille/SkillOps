"""Pydantic models for Missions/Tickets."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Company(BaseModel):
    """Fictitious employer definition."""

    id: str
    name: str
    industry: str
    culture: str
    stack: List[str] = Field(default_factory=list)


class Mission(BaseModel):
    """Mission/Ticket definition for the DevOps Career Simulator."""

    id: int
    key: str
    title: str
    company_id: str
    scenario: str
    objectives: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    difficulty: str = "Intermédiaire"
    estimated_time: str = "30min"
    prerequisites: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    validators: List[str] = Field(default_factory=list)
