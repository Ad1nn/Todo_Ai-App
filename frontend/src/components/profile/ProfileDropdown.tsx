'use client';

/**
 * Linear-inspired profile dropdown with visual accents.
 */

import { Fragment, useState, useEffect, useCallback } from 'react';
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react';
import {
  UserCircleIcon,
  ArrowRightStartOnRectangleIcon,
  PencilIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/useAuth';
import { getUserStats } from '@/lib/auth';
import type { UserStats } from '@/lib/types';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export function ProfileDropdown() {
  const { user, logout, updateProfile } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const userStats = await getUserStats();
        setStats(userStats);
      } catch {
        // Stats are optional
      }
    };
    fetchStats();
  }, []);

  useEffect(() => {
    if (isEditModalOpen && user) {
      setDisplayName(user.display_name || '');
      setError(null);
    }
  }, [isEditModalOpen, user]);

  const handleUpdateProfile = useCallback(async () => {
    setIsUpdating(true);
    setError(null);
    try {
      await updateProfile({ display_name: displayName || null });
      setIsEditModalOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setIsUpdating(false);
    }
  }, [displayName, updateProfile]);

  const handleLogout = useCallback(async () => {
    try {
      await logout();
    } catch {
      // Ignore
    }
  }, [logout]);

  if (!user) return null;

  const displayNameOrEmail = user.display_name || user.email.split('@')[0];
  const memberSince = new Date(user.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
  });

  return (
    <>
      <Menu as="div" className="relative">
        <MenuButton
          className={cn(
            'inline-flex items-center gap-2 rounded-lg px-2 py-1.5',
            'text-gray-600 dark:text-gray-400',
            'hover:bg-indigo-500/10 dark:hover:bg-indigo-500/10',
            'hover:text-indigo-600 dark:hover:text-indigo-400',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
            'transition-all duration-200'
          )}
        >
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-sm shadow-indigo-500/25">
            <span className="text-xs font-medium text-white">
              {displayNameOrEmail.charAt(0).toUpperCase()}
            </span>
          </div>
        </MenuButton>

        <Transition
          as={Fragment}
          enter="transition ease-out duration-200"
          enterFrom="transform opacity-0 scale-95 -translate-y-2"
          enterTo="transform opacity-100 scale-100 translate-y-0"
          leave="transition ease-in duration-150"
          leaveFrom="transform opacity-100 scale-100 translate-y-0"
          leaveTo="transform opacity-0 scale-95 -translate-y-2"
        >
          <MenuItems
            className={cn(
              'absolute right-0 mt-2 w-72 origin-top-right rounded-xl',
              'bg-white/95 dark:bg-[#17171c]/95',
              'backdrop-blur-xl',
              'shadow-2xl shadow-black/10 dark:shadow-black/30',
              'border border-gray-200/50 dark:border-gray-800/50',
              'focus:outline-none z-50',
              'divide-y divide-gray-100 dark:divide-gray-800/50'
            )}
          >
            {/* User Info with gradient accent */}
            <div className="px-4 py-4">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                  <span className="text-sm font-semibold text-white">
                    {displayNameOrEmail.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    {user.display_name || 'No name set'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user.email}
                  </p>
                </div>
              </div>
            </div>

            {/* Stats with badges */}
            {stats && (
              <div className="px-4 py-3">
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-2 rounded-lg bg-emerald-500/10 dark:bg-emerald-500/10">
                    <div className="flex items-center justify-center gap-1">
                      <CheckCircleIcon className="h-4 w-4 text-emerald-500" />
                      <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                        {stats.completed_tasks}
                      </span>
                    </div>
                    <p className="text-[10px] text-emerald-600/70 dark:text-emerald-400/70 uppercase tracking-wide mt-0.5">Done</p>
                  </div>
                  <div className="p-2 rounded-lg bg-blue-500/10 dark:bg-blue-500/10">
                    <div className="flex items-center justify-center gap-1">
                      <ClockIcon className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                        {stats.pending_tasks}
                      </span>
                    </div>
                    <p className="text-[10px] text-blue-600/70 dark:text-blue-400/70 uppercase tracking-wide mt-0.5">Pending</p>
                  </div>
                  <div className={cn(
                    'p-2 rounded-lg',
                    stats.overdue_tasks > 0
                      ? 'bg-red-500/10 dark:bg-red-500/10'
                      : 'bg-gray-100 dark:bg-gray-800/50'
                  )}>
                    <div className="flex items-center justify-center gap-1">
                      <ExclamationTriangleIcon className={cn(
                        'h-4 w-4',
                        stats.overdue_tasks > 0 ? 'text-red-500' : 'text-gray-400'
                      )} />
                      <span className={cn(
                        'text-sm font-bold',
                        stats.overdue_tasks > 0
                          ? 'text-red-600 dark:text-red-400'
                          : 'text-gray-500 dark:text-gray-400'
                      )}>
                        {stats.overdue_tasks}
                      </span>
                    </div>
                    <p className={cn(
                      'text-[10px] uppercase tracking-wide mt-0.5',
                      stats.overdue_tasks > 0
                        ? 'text-red-600/70 dark:text-red-400/70'
                        : 'text-gray-500/70 dark:text-gray-400/70'
                    )}>Overdue</p>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="py-1.5">
              <MenuItem>
                {({ focus }) => (
                  <button
                    onClick={() => setIsEditModalOpen(true)}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left',
                      'transition-all duration-150',
                      focus
                        ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400'
                        : 'text-gray-700 dark:text-gray-300'
                    )}
                  >
                    <PencilIcon className="h-4 w-4" />
                    Edit Profile
                  </button>
                )}
              </MenuItem>
              <MenuItem>
                {({ focus }) => (
                  <button
                    onClick={handleLogout}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left',
                      'transition-all duration-150',
                      focus
                        ? 'bg-red-500/10 text-red-600 dark:text-red-400'
                        : 'text-gray-700 dark:text-gray-300'
                    )}
                  >
                    <ArrowRightStartOnRectangleIcon className="h-4 w-4" />
                    Sign Out
                  </button>
                )}
              </MenuItem>
            </div>

            {/* Footer with gradient line */}
            <div className="px-4 py-2.5">
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Member since {memberSince}
                </p>
                <span className="badge-linear badge-gray text-[10px]">v1.0</span>
              </div>
            </div>
          </MenuItems>
        </Transition>
      </Menu>

      {/* Edit Profile Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Profile"
        size="sm"
        footer={
          <div className="flex justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditModalOpen(false)}
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleUpdateProfile}
              isLoading={isUpdating}
            >
              Save
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            label="Display Name"
            name="displayName"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Enter your name"
            errorMessage={error || undefined}
          />
          <div className="pt-1">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {user.email}
            </p>
          </div>
        </div>
      </Modal>
    </>
  );
}
