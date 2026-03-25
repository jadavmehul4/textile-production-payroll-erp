# Textile Production & Payroll ERP (Ultra Pro Max)

Industrial-grade Enterprise Resource Planning (ERP) system designed for multi-unit textile manufacturing operations.

## 🚀 Production Deployment Guide

### 🧱 Backend Deployment (Render)
1. **Create a New Web Service** on Render and connect this repository.
2. **Root Directory:** `backend`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn core.wsgi:application`
5. **Environment Variables:**
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<Your production secret key>`
   - `ALLOWED_HOSTS`: `your-backend.onrender.com,localhost,127.0.0.1`
   - `DATABASE_URL`: `<Your Render PostgreSQL URL>`
   - `REDIS_URL`: `<Your Redis URL (optional)>`
   - `CORS_ALLOWED_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:3000`
   - `CSRF_TRUSTED_ORIGINS`: `https://your-backend.onrender.com,https://your-frontend.vercel.app`

### 🎨 Frontend Deployment (Vercel)
1. **Create a New Project** on Vercel and connect this repository.
2. **Root Directory:** `frontend`
3. **Framework Preset:** `Next.js`
4. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL`: `https://your-backend.onrender.com`

---

## 🏗 Enterprise Architecture
The system is designed as a Multi-Tenant ERP with a shared database model, enforcing data isolation at both the Middleware and Model Manager layers.

### 🔐 Security Framework
- **Unit Isolation:** Every transactional record is linked to a `unit_id`. Middleware automatically filters data based on the authenticated user's unit.
- **RBAC:** 8 Hierarchical roles from Super Admin to Employee.
- **Audit Trail:** Immutable logs for all financial and structural changes.
- **Production Hardening:** HSTS, Secure Cookies, and JWT Rotation.

### 🧮 Business Logic Engines
- **Rate Engine:** 3-tier priority (Buyer+Item+Op+Size > Buyer+Op > Employee).
- **Payroll Engine:** Transaction-safe calculations for Production, Monthly, and Daily wage types.
- **Attendance:** OT calculation and automated salary impact.

## 🛠 Maintenance & Backups
- **Daily Backups:** `pg_dump` every 24 hours.
- **Audit Reviews:** Super Admin can review immutable logs via the Audit Module.
- **Reconciliation:** Monthly payroll reconciliation tests are built-in.

## 📊 Quick Start (Local Docker)
1. `cp .env.example .env`
2. `docker-compose up --build`
