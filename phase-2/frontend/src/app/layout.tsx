import './globals.css';
import AuthProvider from './AuthProvider';
import Navigation from './Navigation';
import ErrorBoundary from '../components/ErrorBoundary';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50" suppressHydrationWarning={true}>
        <ErrorBoundary>
          <AuthProvider>
            <div className="min-h-screen flex flex-col">
              {/* Header */}
              <header className="bg-slate-900/80 backdrop-blur-md shadow-sm sticky top-0 z-10 border-b border-slate-700/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                  <div className="flex justify-between h-16 items-center">
                    <div className="flex items-center">
                      <h1 className="text-xl font-bold text-white tracking-tight">Todo App</h1>
                    </div>

                    <Navigation />
                  </div>
                </div>
              </header>

              {/* Main content */}
              <main className="flex-grow">
                {children}
              </main>

              {/* Footer */}
              <footer className="bg-slate-900 border-t border-slate-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <p className="text-center text-white text-sm">
                    Developed with ❤️ by <span className="font-medium text-indigo-300">Mahar Ahmad Sarfraz</span>
                  </p>
                </div>
              </footer>
            </div>
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}