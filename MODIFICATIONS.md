# MODIFICATIONS.md - SkillOps v2: DevOps Career Simulator

## 1. Project Objective
**Goal:** Transform the current "Learning Management System" (LMS) into a **"DevOps Career Simulator"**.
**Core Concept:** The user is an employee at a fictitious company (*TechCorp*). Instead of doing abstract "exercises", they solve "tickets" and "incidents" within a simulated Software Development Life Cycle (SDLC).
**Key Pedagogy:** Neuro-learning principles (Active context, Immediate feedback, Scaffolding).

## 2. Architecture Overview

### 2.1. Terminology Shift
| Old Term       | New Term             | Concept                                                                 |
|----------------|----------------------|-------------------------------------------------------------------------|
| Exercise       | **Mission / Ticket** | A task with a business context, acceptance criteria, and validation logic. |
| Reinforce Step | **Mission Control** | The module managing the backlog, board, and execution.                  |
| Share Step     | **Pull Request** | The submission step where AI acts as a Senior Dev reviewer.             |
| Review Step    | **Daily Stand-up** | Reviewing metrics, incidents resolved, and company reputation.          |

### 2.2. File Structure Changes
```text
src/lms/
├── data/
│   ├── companies.yaml         # [NEW] Definition of fictitious employers
│   ├── missions/              # [NEW] Folder replacing exercises_catalog.yaml
│   │   ├── scenario_01_onboarding.yaml
│   │   └── scenario_02_docker_incident.yaml
│   └── exercises_catalog.yaml # [DEPRECATE] To be archived
├── steps/
│   ├── missions.py            # [NEW] Replaces reinforce.py
│   ├── validator.py           # [NEW] Handles local checks (subprocess) & AI reviews
│   └── reinforce.py           # [DEPRECATE]
└── classes/
    └── mission.py             # [NEW] Pydantic models for Missions/Tickets
