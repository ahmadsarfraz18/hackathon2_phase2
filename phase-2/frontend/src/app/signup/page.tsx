'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { motion } from 'framer-motion';
import NoSSRWrapper from '../../components/NoSSRWrapper';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { signup } = useAuth();

  const validatePassword = (password: string) => {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!minLength) return { valid: false, message: "Password must be at least 8 characters long" };
    if (!hasUpperCase) return { valid: false, message: "Password must contain at least one uppercase letter" };
    if (!hasLowerCase) return { valid: false, message: "Password must contain at least one lowercase letter" };
    if (!hasNumbers) return { valid: false, message: "Password must contain at least one digit" };
    if (!hasSpecialChar) return { valid: false, message: "Password must contain at least one special character" };

    return { valid: true, message: "" };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Client-side password validation
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
      setError(passwordValidation.message);
      setLoading(false);
      return;
    }

    try {
      // Create user with Better Auth
      await signup(email, password, firstName, lastName);

      // Redirect to dashboard after successful signup
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred during signup');
      console.error('Signup error:', err);
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
        duration: 0.6,
        ease: "easeOut"
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
        ease: "easeInOut"
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
              Create your account
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
                <label htmlFor="firstName" className="sr-only">
                  First Name
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-3 border border-slate-700 placeholder-slate-400 text-white bg-slate-800/50 backdrop-blur-sm rounded-t-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                  placeholder="First Name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="lastName" className="sr-only">
                  Last Name
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-3 border border-slate-700 placeholder-slate-400 text-white bg-slate-800/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
                  placeholder="Last Name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                />
              </div>
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
                  className="appearance-none rounded-none relative block w-full px-3 py-3 border border-slate-700 placeholder-slate-400 text-white bg-slate-800/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm transition-all duration-200"
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

            <div>
              <motion.button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-all duration-200"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? 'Creating Account...' : 'Sign up'}
              </motion.button>
            </div>
          </motion.form>

          <motion.div
            className="text-center mt-4"
            variants={itemVariants}
          >
            <a
              href="/login"
              className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors duration-200"
            >
              Already have an account? Sign in
            </a>
          </motion.div>
        </motion.div>
      </div>
    </NoSSRWrapper>
  );
};

export default SignupPage;