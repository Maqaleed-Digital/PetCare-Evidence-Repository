import { z } from 'zod'

const schema = z.object({
  NEXT_PUBLIC_APP_NAME: z.string().min(1),
  NEXT_PUBLIC_DOMAIN: z.string().min(1),
  NEXT_PUBLIC_API_BASE_URL: z.string().url(),
  NEXT_PUBLIC_AUTH_MODE: z.enum(['jwt', 'iap']),
  AUTH_ISSUER: z.string().min(1),
  AUTH_AUDIENCE: z.string().min(1),
  SESSION_SECRET: z.string().min(16),
  AUDIT_PROBE_ENDPOINT: z.string().url()
})

export const env = schema.parse({
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  NEXT_PUBLIC_DOMAIN: process.env.NEXT_PUBLIC_DOMAIN,
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  NEXT_PUBLIC_AUTH_MODE: process.env.NEXT_PUBLIC_AUTH_MODE,
  AUTH_ISSUER: process.env.AUTH_ISSUER,
  AUTH_AUDIENCE: process.env.AUTH_AUDIENCE,
  SESSION_SECRET: process.env.SESSION_SECRET,
  AUDIT_PROBE_ENDPOINT: process.env.AUDIT_PROBE_ENDPOINT
})
