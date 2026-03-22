# Textile Production & Payroll ERP - Ultra Pro Max

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

## 📊 Database Schema (Core)
- **master_data:** Units, Buyers, Items, Operations, Rates, Sizes.
- **erp_core:** Employees, Departments, Designations.
- **production:** ProductionEntries, CuttingLogs, DailyProductionSummaries.
- **payroll:** Advances, SalaryRecords.
- **audit_log:** AuditLogs.

## 🚀 Deployment Guide
1. **Backend:** Django 6.0, Gunicorn, PostgreSQL.
2. **Frontend:** Next.js 16 (App Router), Tailwind CSS v4.
3. **Environment:** 
   - `DEBUG=False`
   - `SECURE_SSL_REDIRECT=True`
   - `DATABASE_URL` (PostgreSQL)

## 🛠 Maintenance & Backups
- **Daily Backups:** `pg_dump` every 24 hours.
- **Audit Reviews:** Super Admin can review immutable logs via the Audit Module.
- **Reconciliation:** Monthly payroll reconciliation tests are built-in.
