import { z } from 'zod';

export const employeeSchema = z.object({
  employee_id: z.string().min(1, 'Employee ID is required'),
  full_name: z.string().min(3, 'Full name must be at least 3 characters'),
  gender: z.enum(['M', 'F', 'O']),
  unit: z.number().int(),
  department: z.number().int(),
  designation: z.number().int(),
  salary_type: z.enum(['PRODUCTION_WISE', 'MONTHLY', 'DAILY']),
  rate: z.number().nonnegative().optional(),
  bank_account_number: z.string().optional(),
  ifsc_code: z.string().regex(/^[A-Z]{4}0[A-Z0-9]{6}$/, 'Invalid IFSC code').optional(),
});

export const productionSchema = z.object({
  date: z.string(),
  employee: z.number().int(),
  buyer: z.number().int(),
  item: z.number().int(),
  so_number: z.string().min(1),
  operation: z.number().int(),
  size: z.number().int().optional(),
  quantity: z.number().int().positive('Quantity must be positive'),
});
