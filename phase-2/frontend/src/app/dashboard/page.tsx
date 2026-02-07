'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../hooks/useAuth';
import { taskApi } from '../../lib/api';

// Define the Task interface
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

import ProtectedRoute from '../../components/ProtectedRoute';

export default function DashboardPage() {
  const { user, loading, isInitialized, isAuthenticated, safeLogout, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [editTaskTitle, setEditTaskTitle] = useState('');
  const [editTaskDescription, setEditTaskDescription] = useState('');

  // Fetch tasks when component mounts and user is authenticated
  useEffect(() => {
    let isCancelled = false; // Prevent state updates after component unmounts

    const fetchTasks = async () => {
      try {
        if (isCancelled) return; // Early exit if component unmounted

        setLoadingTasks(true);
        setError(null); // Clear any previous errors

        const tasksData = await taskApi.getTasks();

        if (isCancelled) return; // Early exit if component unmounted
        setTasks(tasksData);
      } catch (err: any) {
        // Check if the error is related to authentication
        if (err?.message?.includes('Unauthorized') || err?.message?.includes('Please log in again') || err?.message?.includes('Not authenticated')) {
          // Use setTimeout to safely call logout after the current call stack
          setTimeout(() => {
            logout();
          }, 0);
          return;
        }

        if (isCancelled) return; // Early exit if component unmounted
        setError(err?.message || 'Failed to fetch tasks');
        console.error('Error fetching tasks:', err);
      } finally {
        if (!isCancelled) {
          setLoadingTasks(false);
        }
      }
    };

    // Only fetch tasks if auth is initialized and user is authenticated
    if (isInitialized && isAuthenticated && user) {
      fetchTasks();
    } else if (isInitialized && !isAuthenticated) {
      // If auth is initialized but user is not authenticated, ensure tasks are cleared
      setTasks([]);
      setLoadingTasks(false);
    }

    // Cleanup function to set isCancelled to true when component unmounts
    return () => {
      isCancelled = true;
    };
  }, [isInitialized, isAuthenticated, user]); // Removed logout and safeLogout from dependencies to prevent infinite re-renders

  // Show loading state while authentication is being resolved
  // Wait for component to be fully initialized to ensure client-side auth state is ready
  if (loading || !isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="relative inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto"></div>
            <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-indigo-200"></div>
          </div>
          <p className="mt-4 text-lg text-gray-600 animate-fade-in">Checking authentication status...</p>
        </div>
      </div>
    );
  }

  // Only show Access Denied after auth state has been fully resolved and user is not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 animate-fade-in-up">
          <div className="text-center">
            <div className="mx-auto bg-gradient-to-r from-indigo-500 to-purple-600 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="mt-4 text-3xl font-bold bg-gradient-to-r from-gray-900 to-indigo-700 bg-clip-text text-transparent">
              Access Denied
            </h2>
            <p className="mt-2 text-gray-600">
              Please log in to access the dashboard
            </p>
            <div className="mt-8">
              <Link
                href="/login"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                Go to Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleAddTask = async () => {
    if (!newTaskTitle.trim()) {
      setError('Task title is required');
      return;
    }

    try {
      setError(null);
      const newTask = await taskApi.createTask({
        title: newTaskTitle,
        description: newTaskDescription,
        completed: false
      });

      setTasks([newTask, ...tasks]); // Add new task to the top of the list
      setNewTaskTitle('');
      setNewTaskDescription('');
      setShowAddTaskModal(false);
    } catch (err: any) {
      // Check if the error is related to authentication
      if (err?.message?.includes('Unauthorized') || err?.message?.includes('Please log in again') || err?.message?.includes('Not authenticated')) {
        // Use setTimeout to safely call safeLogout after the current call stack
        setTimeout(() => {
          safeLogout();
        }, 0);
        // We can't redirect here directly, but the component will re-render and show Access Denied
        return;
      }

      setError(err?.message || 'Failed to add task');
      console.error('Error adding task:', err);
    }
  };

  const handleToggleTask = async (taskId: string, completed: boolean) => {
    try {
      const updatedTask = await taskApi.updateTask(taskId, { completed: !completed });

      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, completed: !completed } : task
      ));
    } catch (err: any) {
      // Check if the error is related to authentication
      if (err?.message?.includes('Unauthorized') || err?.message?.includes('Please log in again') || err?.message?.includes('Not authenticated')) {
        // Use setTimeout to safely call safeLogout after the current call stack
        setTimeout(() => {
          safeLogout();
        }, 0);
        // We can't redirect here directly, but the component will re-render and show Access Denied
        return;
      }

      setError(err?.message || 'Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await taskApi.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err: any) {
      // Check if the error is related to authentication
      if (err?.message?.includes('Unauthorized') || err?.message?.includes('Please log in again') || err?.message?.includes('Not authenticated')) {
        // Use setTimeout to safely call safeLogout after the current call stack
        setTimeout(() => {
          safeLogout();
        }, 0);
        // We can't redirect here directly, but the component will re-render and show Access Denied
        return;
      }

      setError(err?.message || 'Failed to delete task');
      console.error('Error deleting task:', err);
    }
  };

  const handleEditTask = async (task: Task) => {
    setEditingTask(task);
    setEditTaskTitle(task.title);
    setEditTaskDescription(task.description || '');
  };

  const handleSaveEditTask = async () => {
    if (!editingTask) return;

    try {
      const updatedTask = await taskApi.updateTask(editingTask.id, {
        title: editTaskTitle.trim(),
        description: editTaskDescription.trim() || null
      });

      setTasks(tasks.map(t =>
        t.id === editingTask.id ? { ...updatedTask } : t
      ));

      setEditingTask(null);
      setEditTaskTitle('');
      setEditTaskDescription('');
    } catch (err: any) {
      // Check if the error is related to authentication
      if (err?.message?.includes('Unauthorized') || err?.message?.includes('Please log in again') || err?.message?.includes('Not authenticated')) {
        // Use setTimeout to safely call safeLogout after the current call stack
        setTimeout(() => {
          safeLogout();
        }, 0);
        // We can't redirect here directly, but the component will re-render and show Access Denied
        return;
      }

      setError(err?.message || 'Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const cancelEditTask = () => {
    setEditingTask(null);
    setEditTaskTitle('');
    setEditTaskDescription('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50">
      {/* Animated Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center animate-fade-in">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-2.5 rounded-xl shadow-lg transform transition-transform duration-300 hover:scale-105">
                  <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <h1 className="ml-3 text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent animate-slide-in-left">
                  TaskFlow
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4 animate-slide-in-right">
              <div className="text-gray-600 text-sm">
                Welcome back, <span className="font-semibold text-indigo-600">{user.name || user.email.split('@')[0]}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-10 space-y-6 sm:space-y-0">
          <div className="animate-fade-in-up">
            <h2 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-indigo-700 bg-clip-text text-transparent">
              Your Tasks
            </h2>
            <p className="mt-3 text-lg text-gray-600 animate-fade-in-up delay-100">
              {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} in your list
            </p>
          </div>
          <button
            onClick={() => setShowAddTaskModal(true)}
            className="inline-flex items-center px-7 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 animate-fade-in-up delay-200 group"
          >
            <svg className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add New Task
          </button>
        </div>

        {error && (
          <div className="rounded-xl bg-red-50 p-4 mb-6 border border-red-200 animate-fade-in-up shadow-sm">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400 animate-pulse" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-1 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {loadingTasks ? (
          <div className="flex justify-center items-center py-20 animate-pulse">
            <div className="relative">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
              <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-indigo-200"></div>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-20 animate-fade-in-up">
            <div className="mx-auto h-32 w-32 text-indigo-200 flex items-center justify-center mb-6 animate-bounce">
              <svg className="h-32 w-32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">No tasks yet</h3>
            <p className="text-gray-600 mb-8">Get started by creating your first task.</p>
            <button
              onClick={() => setShowAddTaskModal(true)}
              className="inline-flex items-center px-7 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 animate-fade-in-up delay-300 group"
            >
              <svg className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Create Your First Task
            </button>
          </div>
        ) : (
          <div className="space-y-5">
            {tasks.map((task, index) => (
              <div
                key={task.id}
                className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start space-x-4">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggleTask(task.id, task.completed)}
                    className="mt-1 h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer transition-transform duration-200 hover:scale-110"
                  />
                  <div className="flex-1 min-w-0">
                    <p className={`text-lg font-medium transition-all duration-300 ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                      {task.title}
                    </p>
                    {task.description && (
                      <p className="text-sm text-gray-600 mt-2 transition-opacity duration-300">{task.description}</p>
                    )}
                    <div className="mt-4 flex items-center text-xs text-gray-500 transition-colors duration-300">
                      <svg className="flex-shrink-0 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditTask(task)}
                      className="inline-flex items-center px-4 py-2 text-xs font-medium text-indigo-700 bg-indigo-50/80 hover:bg-indigo-100 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 backdrop-blur-sm"
                    >
                      <svg className="h-4 w-4 mr-1 transition-transform duration-200 hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      className="inline-flex items-center px-4 py-2 text-xs font-medium text-red-700 bg-red-50/80 hover:bg-red-100 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 backdrop-blur-sm"
                    >
                      <svg className="h-4 w-4 mr-1 transition-transform duration-200 hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer with Logout */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-6 sm:space-y-0">
            <div className="text-sm text-gray-600 animate-fade-in-up">
              Signed in as: <span className="font-medium text-gray-900">{user.email}</span>
            </div>
            <button
              onClick={safeLogout}
              className="inline-flex items-center px-5 py-2.5 border border-gray-300 text-sm font-medium rounded-lg text-red-700 bg-red-50/80 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 backdrop-blur-sm animate-fade-in-up"
            >
              <svg className="mr-2 h-4 w-4 transition-transform duration-300 group-hover:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>
      </footer>

      {/* Add Task Modal */}
      {showAddTaskModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl p-7 max-w-lg w-full transform transition-all duration-300 scale-100 animate-slide-up">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Add New Task</h3>
              <button
                onClick={() => {
                  setShowAddTaskModal(false);
                  setNewTaskTitle('');
                  setNewTaskDescription('');
                  setError(null);
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200 hover:rotate-90"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div className="animate-fade-in-up">
                <label htmlFor="task-title" className="block text-sm font-medium text-gray-700 mb-3">
                  Task Title *
                </label>
                <input
                  type="text"
                  id="task-title"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white/80 backdrop-blur-sm transition-all duration-200"
                  placeholder="Enter task title"
                  autoFocus
                />
              </div>

              <div className="animate-fade-in-up delay-100">
                <label htmlFor="task-description" className="block text-sm font-medium text-gray-700 mb-3">
                  Description (Optional)
                </label>
                <textarea
                  id="task-description"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white/80 backdrop-blur-sm transition-all duration-200 resize-none"
                  placeholder="Enter task description..."
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 p-4 border border-red-200 animate-fade-in-up delay-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-3 animate-fade-in-up delay-300">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddTaskModal(false);
                    setNewTaskTitle('');
                    setNewTaskDescription('');
                    setError(null);
                  }}
                  className="inline-flex items-center px-5 py-2.5 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white/80 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 backdrop-blur-sm"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAddTask}
                  className="inline-flex items-center px-5 py-2.5 text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 group"
                >
                  <svg className="mr-2 h-4 w-4 transition-transform duration-300 group-hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Task
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl p-7 max-w-lg w-full transform transition-all duration-300 scale-100 animate-slide-up">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Edit Task</h3>
              <button
                onClick={cancelEditTask}
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200 hover:rotate-90"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div className="animate-fade-in-up">
                <label htmlFor="edit-task-title" className="block text-sm font-medium text-gray-700 mb-3">
                  Task Title *
                </label>
                <input
                  type="text"
                  id="edit-task-title"
                  value={editTaskTitle}
                  onChange={(e) => setEditTaskTitle(e.target.value)}
                  className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white/80 backdrop-blur-sm transition-all duration-200"
                  placeholder="Enter task title"
                />
              </div>

              <div className="animate-fade-in-up delay-100">
                <label htmlFor="edit-task-description" className="block text-sm font-medium text-gray-700 mb-3">
                  Description (Optional)
                </label>
                <textarea
                  id="edit-task-description"
                  value={editTaskDescription}
                  onChange={(e) => setEditTaskDescription(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white/80 backdrop-blur-sm transition-all duration-200 resize-none"
                  placeholder="Enter task description..."
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 p-4 border border-red-200 animate-fade-in-up delay-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-3 animate-fade-in-up delay-300">
                <button
                  type="button"
                  onClick={cancelEditTask}
                  className="inline-flex items-center px-5 py-2.5 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white/80 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 backdrop-blur-sm"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveEditTask}
                  className="inline-flex items-center px-5 py-2.5 text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 group"
                >
                  <svg className="mr-2 h-4 w-4 transition-transform duration-300 group-hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}