/**
 * Linear-inspired login page with gradient accents.
 */

import { SparklesIcon } from '@heroicons/react/24/outline';
import { LoginForm } from '@/components/LoginForm';

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12 bg-gray-50 dark:bg-[#0d0d0f] relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-linear opacity-50" />

      {/* Floating orbs for visual interest */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />

      <div className="w-full max-w-md relative z-10">
        <div className="mb-8 text-center">
          {/* Logo */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30 mb-6">
            <SparklesIcon className="h-7 w-7 text-white" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome Back
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Sign in to your account
          </p>
        </div>

        <div className="rounded-xl bg-white/80 dark:bg-[#17171c]/80 backdrop-blur-xl p-8 shadow-2xl shadow-black/5 dark:shadow-black/20 border border-gray-200/50 dark:border-gray-800/50">
          <LoginForm />
        </div>

        <p className="mt-6 text-center text-xs text-gray-400 dark:text-gray-500">
          Powered by AI-driven task management
        </p>
      </div>
    </main>
  );
}
