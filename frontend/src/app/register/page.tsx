/**
 * Linear-inspired registration page with gradient accents.
 */

import { SparklesIcon } from '@heroicons/react/24/outline';
import { RegisterForm } from '@/components/RegisterForm';

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12 bg-gray-50 dark:bg-[#0d0d0f] relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-linear opacity-50" />

      {/* Floating orbs for visual interest */}
      <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/3 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />

      <div className="w-full max-w-md relative z-10">
        <div className="mb-8 text-center">
          {/* Logo */}
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 shadow-lg shadow-purple-500/30 mb-6">
            <SparklesIcon className="h-7 w-7 text-white" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Create Account
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Join us to manage your tasks with AI
          </p>
        </div>

        <div className="rounded-xl bg-white/80 dark:bg-[#17171c]/80 backdrop-blur-xl p-8 shadow-2xl shadow-black/5 dark:shadow-black/20 border border-gray-200/50 dark:border-gray-800/50">
          <RegisterForm />
        </div>

        <p className="mt-6 text-center text-xs text-gray-400 dark:text-gray-500">
          Powered by AI-driven task management
        </p>
      </div>
    </main>
  );
}
