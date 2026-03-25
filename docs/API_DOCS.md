# Textile Production & Payroll ERP - API Documentation

## Authentication
- `POST /api/token/`: Obtain JWT access and refresh tokens.
- `POST /api/token/refresh/`: Refresh access token.

## Master Data
- `GET /api/master-data/units/`: List units.
- `GET /api/master-data/buyers/`: List buyers.
- `GET /api/master-data/items/`: List items.
- `GET /api/master-data/operations/`: List operations.
- `GET /api/master-data/operation-rates/`: List/Create operation rates.

## ERP Core
- `GET /api/erp/employees/`: List/Create employees. Includes auto-user provisioning.

## Production
- `POST /api/production/entries/`: Create production entry. Auto-resolves rates.
- `GET /api/production/cutting-logs/`: List/Create cutting logs.

## Attendance & Payroll
- `GET /api/attendance/`: List/Mark attendance.
- `GET /api/payroll/advances/`: List/Create advances.

## Reports
- `GET /api/reports/dashboard/`: Dashboard statistics.
- `GET /api/reports/production/`: Detailed production reports with filters.

## Unit Isolation
All endpoints automatically filter data by the authenticated user's `unit_id`, except for Super Admin.
