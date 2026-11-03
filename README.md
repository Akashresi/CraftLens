# CraftLens 📸🎨

> **AI-Driven Market Linkage and Smart Cataloging Mobile Application for Marginalized Artisans**  
> *Smart India Hackathon (SIH 2026) | Problem Statement: SIH26090*  
> *Theme: Heritage & Culture | Ministry of Social Justice and Empowerment (MoSJE)*

---

## 🌟 Overview

**CraftLens** is an intelligent, accessible platform designed to bridge the digital divide for marginalized artisans, weavers, and traditional craftspeople. By combining computer vision, generative AI, and multilingual voice capabilities, CraftLens empowers artisans to easily digitize, catalog, and sell their creations on global markets without technical friction or intermediaries.

---

## 🏗️ Architecture & Project Structure

The project is organized as a modular monorepo:

```
CraftLens/
├── mobile/         # Mobile application for artisans (Multilingual UI, Camera & Voice interface)
├── ai-service/     # AI service (Computer vision, auto-tagging, background cleanup, description generation)
├── backend/        # Core backend API (Marketplace, user management, order linkage & inventory)
├── admin-web/      # Web dashboard for administrators, onboarding, and buyer marketplace
└── README.md
```

### Modules
- **`mobile/`**: Lightweight, intuitive mobile app tailored for low-literacy users with voice navigation, one-click camera scanning, and local language support.
- **`ai-service/`**: Python FastAPI microservice that extracts product features from images, removes cluttered backgrounds, generates SEO-friendly descriptions, and suggests optimal pricing.
- **`backend/`**: Scalable backend API handling authentication, product catalogs, order lifecycle, and market integration.
- **`admin-web/`**: Administrative portal for verification, analytics, artisan welfare tracking, and marketplace moderation.

---

## 🚀 Getting Started

### AI Service Setup
```bash
cd ai-service
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 📄 License
This project is developed for educational and hackathon purposes under the Smart India Hackathon initiative.
