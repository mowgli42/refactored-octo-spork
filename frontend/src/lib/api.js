/** Default API base; override with VITE_API_URL at build/dev time. */
export const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';
