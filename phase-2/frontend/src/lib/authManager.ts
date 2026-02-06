import { getSession, signIn, signOut } from 'next-auth/react';

class AuthManager {
  private onAuthChangeCallbacks: Array<(isAuthenticated: boolean) => void> = [];

  constructor() {
    // Check authentication status on initialization
    this.checkAuthStatus();
  }

  // Subscribe to authentication status changes
  subscribe(callback: (isAuthenticated: boolean) => void) {
    this.onAuthChangeCallbacks.push(callback);
    return () => {
      this.onAuthChangeCallbacks = this.onAuthChangeCallbacks.filter(cb => cb !== callback);
    };
  }

  // Notify all subscribers of authentication status change
  private notifyAuthChange(isAuthenticated: boolean) {
    this.onAuthChangeCallbacks.forEach(callback => callback(isAuthenticated));
  }

  // Check authentication status
  async checkAuthStatus() {
    const session = await getSession();
    const authenticated = !!session?.user;
    this.notifyAuthChange(authenticated);
  }

  // Get time until token expiration in milliseconds (NextAuth handles this automatically)
  async getTimeUntilExpiration(): Promise<number | null> {
    // NextAuth handles token expiration automatically, but we can provide a mock implementation
    // In a real app, this would be handled by NextAuth's built-in session management
    const session = await getSession();
    if (!session) {
      return null;
    }

    // NextAuth session includes an expires field (ISO string)
    if (session.expires) {
      const expirationTime = new Date(session.expires).getTime();
      const currentTime = Date.now();
      return Math.max(0, expirationTime - currentTime);
    }

    return null;
  }

  // Check if token is expired (NextAuth handles this automatically)
  async isTokenExpired(): Promise<boolean> {
    const timeUntilExpiration = await this.getTimeUntilExpiration();
    return timeUntilExpiration === null || timeUntilExpiration <= 0;
  }

  // Check if token will expire soon (within 5 minutes)
  async willTokenExpireSoon(): Promise<boolean> {
    const timeUntilExpiration = await this.getTimeUntilExpiration();
    const FIVE_MINUTES = 5 * 60 * 1000; // 5 minutes in milliseconds
    return timeUntilExpiration !== null && timeUntilExpiration <= FIVE_MINUTES;
  }

  // Force logout and cleanup
  async logout() {
    await signOut({ redirect: false });
    this.notifyAuthChange(false);
  }

  // Get token expiration info
  async getTokenExpirationInfo() {
    const session = await getSession();
    if (!session || !session.expires) {
      return null;
    }

    const expirationTime = new Date(session.expires);
    const currentTime = new Date();
    const timeUntilExpiration = Math.max(0, expirationTime.getTime() - currentTime.getTime());

    return {
      expirationTime,
      currentTime,
      timeUntilExpiration,
      isExpired: timeUntilExpiration <= 0,
      willExpireSoon: timeUntilExpiration <= 5 * 60 * 1000, // 5 minutes
    };
  }
}

// Create a singleton instance
export const authManager = new AuthManager();

// Export for use in components
export default authManager;