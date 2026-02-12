'use client';

/**
 * Linear-inspired sidebar with gradient accents.
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export interface NavItem {
  label: string;
  href: string;
  icon?: ReactNode;
  badge?: string | number;
}

export interface SidebarProps {
  items: NavItem[];
  isCollapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  className?: string;
}

export function Sidebar({
  items,
  isCollapsed = false,
  className,
}: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'hidden lg:fixed lg:inset-y-0 lg:z-30 lg:flex lg:flex-col',
        'bg-white/50 dark:bg-[#0d0d0f]/80',
        'backdrop-blur-xl',
        'border-r border-gray-200/50 dark:border-gray-800/50',
        isCollapsed ? 'lg:w-16' : 'lg:w-56',
        'transition-all duration-200',
        className
      )}
    >
      {/* Logo area */}
      <div className="flex h-14 shrink-0 items-center px-4 border-b border-gray-200/50 dark:border-gray-800/50">
        {isCollapsed ? (
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <SparklesIcon className="h-4 w-4 text-white" />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <SparklesIcon className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">
              Tasks
            </span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col overflow-y-auto p-2">
        <ul role="list" className="flex flex-1 flex-col gap-y-1">
          {items.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'group flex h-9 items-center gap-x-3 rounded-lg px-3 text-sm font-medium',
                    'transition-all duration-200',
                    isActive
                      ? 'bg-indigo-500/10 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/50 dark:hover:text-white',
                    isCollapsed && 'justify-center px-0'
                  )}
                  title={isCollapsed ? item.label : undefined}
                >
                  {item.icon && (
                    <span className={cn(
                      'h-4 w-4 shrink-0 transition-colors duration-200',
                      isActive ? 'text-indigo-500 dark:text-indigo-400' : 'opacity-70 group-hover:opacity-100'
                    )}>
                      {item.icon}
                    </span>
                  )}
                  {!isCollapsed && (
                    <>
                      <span className="truncate">{item.label}</span>
                      {item.badge !== undefined && (
                        <span className={cn(
                          'ml-auto badge-linear',
                          isActive
                            ? 'badge-purple'
                            : 'badge-gray'
                        )}>
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom gradient accent */}
      <div className="h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
    </aside>
  );
}
