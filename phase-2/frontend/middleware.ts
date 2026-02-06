import { NextRequest, NextResponse } from 'next/server';

// Define public routes that don't require authentication
const publicRoutes = ['/', '/login', '/signup', '/api/auth', '/health'];

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // If it's a public route, allow it to proceed
  if (isPublicRoute) {
    return NextResponse.next();
  }

  // For protected routes, check if user is authenticated
  // We'll check for the presence of auth token in localStorage via client-side code
  // but we'll also handle the case where the user tries to access protected routes directly

  // Check if this is an API call
  if (pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // For protected page routes, allow the request to proceed to the component
  // where authentication will be handled client-side
  // This avoids server-side authentication issues during SSR
  return NextResponse.next();
}

// Specify the paths the middleware should run for
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};