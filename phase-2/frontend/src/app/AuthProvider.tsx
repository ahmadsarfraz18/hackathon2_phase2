'use client';

import { AuthProvider as AuthProviderImpl } from '../hooks/useAuth';

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  return <AuthProviderImpl>{children}</AuthProviderImpl>;
}