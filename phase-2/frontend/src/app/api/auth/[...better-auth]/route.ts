import { auth } from '@/auth';

// Export the handlers from Better-Auth
// The Better Auth instance should provide the handlers directly
export const { GET, POST } = auth;