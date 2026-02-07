'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { signIn } from '../../auth';
import { motion, easeInOut } from 'framer-motion';
import NoSSRWrapper from '../../components/NoSSRWrapper';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Sign in with our custom auth
      const response = await signIn({
        email,
        password,
        callbackURL: '/dashboard'  // Redirect after successful login
      });

      if (response?.error) {
        setError(response.error.message || 'Login failed');
        console.error('Login error response:', response.error);
      } else {
        // Successful login - redirect to dashboard
        // Add a small delay to ensure auth state is updated before navigation
        setTimeout(() => {
          // Force a refresh to ensure auth state is properly synced
          window.location.href = '/dashboard';
        }, 100);
      }
    } catch (err: unknown) {
      // Handle the "Object" error issue by providing better error handling
      let errorMessage = 'An error occurred during login';

      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        try {
          const errObj = err as Record<string, unknown>;
          if (typeof errObj.message === 'string') {
            errorMessage = errObj.message;
          } else {
            errorMessage = String(err);
          }
        } catch {
          errorMessage = 'Unknown error occurred during login';
        }
      }

      setError(errorMessage);
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: easeInOut
      }
    }
  };

  const floatVariants = {
    animate: {
      y: [0, -10, 0],
      x: [0, 3, 0],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: easeInOut
      }
    }
  };

  return (
    <NoSSRWrapper>
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
        {/* Animated background elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-indigo-900/20 to-purple-900/20"></div>
        <div className="absolute top-20 left-10 w-2 h-2 bg-indigo-400 rounded-full opacity-60"></div>
        <div className="absolute top-40 right-20 w-3 h-3 bg-purple-400 rounded-full opacity-40"></div>
        <div className="absolute bottom-40 left-1/4 w-1 h-1 bg-blue-400 rounded-full opacity-50"></div>

        <motion.div
          className="max-w-md w-full space-y-8 relative z-10"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div>
            <motion.h2
              className="mt-6 text-center text-3xl font-extrabold text-white"
              variants={itemVariants}
            >
              Sign in to your account
            </motion.h2>
          </div>

          <motion.form
            className="mt-8 space-y-6"
            onSubmit={handleSubmit}
            variants={itemVariants}
          >
            {error && (
              <motion.div
                className="rounded-md bg-red-500/20 p-4 border border-red-500/30"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="text-sm text-red-300">{error}</div>
              </motion.div>
            )}

            <input type="hidden" name="remember" defaultValue="true" />
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <label htmlFor="email-address" className="sr-only">
                  Email address
                </label>
                <input
                  id="email-address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-3 border border-slate-700 placeholder-slate-400 text-white bg-slate-800/50 backdrop-blur-sm rounded-t-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-3 border border-slate-700 placeholder-slate-400 text-white bg-slate-800/50 backdrop-blur-sm rounded-b-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <Link href="/forgot-password" className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors duration-200">
                  Forgot your password?
                </Link>
              </div>
            </div>

            <div>
              <motion.button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-all duration-200"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </motion.button>
            </div>
          </motion.form>

          <motion.div
            className="text-center mt-4"
            variants={itemVariants}
          >
            <Link
              href="/signup"
              className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors duration-200"
            >
              Don't have an account? Sign up
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </NoSSRWrapper>
  );
};

export default LoginPage;