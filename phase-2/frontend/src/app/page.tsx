'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { CheckCircle, Zap, Shield, Users } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const HomePage = () => {
  const { user, loading } = useAuth();

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

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const floatVariants = {
    animate: {
      y: [0, -15, 0],
      x: [0, 5, 0],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  const pulseVariants = {
    animate: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* Animated floating elements */}
      <motion.div
        className="absolute top-20 left-10 w-2 h-2 bg-indigo-400 rounded-full"
        variants={floatVariants}
        animate="animate"
      />
      <motion.div
        className="absolute top-40 right-20 w-3 h-3 bg-purple-400 rounded-full"
        variants={floatVariants}
        animate="animate"
        transition={{ delay: 0.5 }}
      />
      <motion.div
        className="absolute bottom-40 left-1/4 w-1 h-1 bg-blue-400 rounded-full"
        variants={floatVariants}
        animate="animate"
        transition={{ delay: 1 }}
      />

      <motion.div
        className="container mx-auto px-4 py-16 flex flex-col items-center text-center max-w-4xl relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Logo/Brand Area */}
        <motion.div
          className="mb-8"
          variants={itemVariants}
        >
          <motion.div
            className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center"
            variants={pulseVariants}
            animate="animate"
          >
            <CheckCircle className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            <span className="gradient-text">TaskFlow</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            The ultimate productivity platform for individuals and teams
          </p>
        </motion.div>

        {/* Hero Section */}
        <motion.div
          className="glass-card rounded-3xl p-8 md:p-12 mb-12 max-w-3xl"
          variants={itemVariants}
        >
          <motion.h2
            className="text-3xl md:text-5xl font-bold mb-6 leading-tight"
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6, ease: "easeOut" }}
          >
            Transform Your <span className="gradient-text">Productivity</span> with Smart Task Management
          </motion.h2>

          <motion.p
            className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto"
            variants={itemVariants}
          >
            Streamline your workflow, collaborate seamlessly, and achieve more with our intuitive task management platform designed for modern professionals.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center"
            variants={itemVariants}
          >
            {!user ? (
              <>
                <Link href="/signup">
                  <motion.button
                    className="btn-primary text-white font-semibold py-3 px-8 rounded-xl text-lg relative overflow-hidden"
                    whileHover={{ scale: 1.05, boxShadow: "0 20px 25px -5px rgba(99, 102, 241, 0.3)" }}
                    whileTap={{ scale: 0.95 }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5, duration: 0.4 }}
                  >
                    <span className="relative z-10">Get Started</span>
                    <motion.span
                      className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-700 opacity-0"
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                  </motion.button>
                </Link>
                <Link href="/login">
                  <motion.button
                    className="btn-secondary text-white font-semibold py-3 px-8 rounded-xl text-lg relative overflow-hidden"
                    whileHover={{ scale: 1.05, boxShadow: "0 20px 25px -5px rgba(99, 102, 241, 0.15)" }}
                    whileTap={{ scale: 0.95 }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6, duration: 0.4 }}
                  >
                    <span className="relative z-10">Sign In</span>
                    <motion.span
                      className="absolute inset-0 bg-gray-700 opacity-0"
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                  </motion.button>
                </Link>
              </>
            ) : (
              <Link href="/dashboard">
                <motion.button
                  className="btn-primary text-white font-semibold py-3 px-8 rounded-xl text-lg"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Go to Dashboard
                </motion.button>
              </Link>
            )}
          </motion.div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl"
          variants={containerVariants}
        >
          {[{icon: Zap, title: "Lightning Fast", desc: "Quick task creation and updates"},
            {icon: Shield, title: "Secure", desc: "Enterprise-grade security for your data"},
            {icon: Users, title: "Collaborative", desc: "Work together in real-time"}].map((feature, index) => (
            <motion.div
              key={index}
              className="glass-card rounded-2xl p-6 text-left"
              variants={itemVariants}
              whileHover={{ y: -8, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <motion.div
                className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mb-4"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
              >
                <feature.icon className="w-6 h-6 text-white" />
              </motion.div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-300">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* User Status */}
        {loading ? (
          <motion.div
            className="mt-8 text-gray-400"
            variants={itemVariants}
          >
            Loading...
          </motion.div>
        ) : user ? (
          <motion.div
            className="mt-8 text-gray-300 text-center"
            variants={itemVariants}
          >
            <p>Hello, {user.name || user.email}!</p>
            <p className="text-sm mt-2">Ready to boost your productivity?</p>
          </motion.div>
        ) : null}
      </motion.div>
    </div>
  );
};

export default HomePage;