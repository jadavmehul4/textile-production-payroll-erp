# Textile Production & Payroll ERP - Deployment & Security Guide

## Deployment Architecture
- **Frontend:** Next.js (Static Export or Node.js server)
- **Backend:** Django with Gunicorn/Uvicorn
- **Database:** PostgreSQL (15+)
- **Cache/Broker:** Redis
- **Worker:** Celery (for salary generation and reports)
- **Proxy:** NGINX with SSL (Let's Encrypt)

## Security Policy
1. **Data Isolation:** Enforced via `UnitIsolationMiddleware` and `UnitIsolatedManager`. Cross-unit data access is prohibited except for Super Admins.
2. **Authentication:** JWT with Rotating Refresh Tokens. Access tokens expire in 60 minutes.
3. **RBAC:** Hierarchical role-based access control with module-level granularity.
4. **Audit:** Every structural/financial change is logged with IP and timestamp. Logs are immutable.
5. **Validation:** Multi-layer validation (Zod on frontend, DRF Serializers on backend).

## Backup Strategy
- **Database:** Nightly automated dumps to secure off-site storage.
- **Retention:** 30 days of daily backups.
- **Verification:** Weekly automated restoration tests.

## Performance Tuning
- **Indexing:** All foreign keys and date-range filter fields are indexed.
- **Caching:** Redis-based caching for frequent master data queries.
- **Scaling:** Horizontal scaling supported for both Frontend and Backend layers.
