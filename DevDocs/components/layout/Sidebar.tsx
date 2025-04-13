'use client'; // Make this a client component to use hooks

import Link from 'next/link';
import { usePathname } from 'next/navigation'; // Import usePathname
import { cn } from '@/lib/utils';
import TestingIcon from '../icons/TestingIcon';

// Icon components
const IconPlaceholder = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("h-5 w-5", className)}
  >
    <path d="M12 5v14M5 12h14" />
  </svg>
);

// AI Agent icon
const AgentIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("h-5 w-5", className)}
  >
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <path d="M12 7v4" />
    <line x1="8" y1="16" x2="8" y2="16" />
    <line x1="16" y1="16" x2="16" y2="16" />
    <path d="M9 20l3 2 3-2" />
  </svg>
);

// Document icon
const DocumentIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("h-5 w-5", className)}
  >
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10 9 9 9 8 9" />
  </svg>
);

const Sidebar = () => {
  const pathname = usePathname(); // Get the current path

  const menuItems = [
    { href: '/dashboard', label: 'Dashboard', icon: IconPlaceholder },
    { href: '/upload', label: 'Upload Documents', icon: IconPlaceholder },
    { href: '/documents', label: 'My Documents', icon: IconPlaceholder },
    { href: '/document-analysis', label: 'Document Analysis', icon: DocumentIcon },
    { href: '/agents', label: 'AI Agents', icon: AgentIcon },
    { href: '/dev-test-center', label: 'Testing', icon: TestingIcon },
    { href: '/settings', label: 'Settings', icon: IconPlaceholder },
    { href: '/api-keys', label: 'API Keys', icon: IconPlaceholder },
    { href: '/integrations', label: 'Integrations', icon: IconPlaceholder },
  ];

  return (
    <div className="hidden border-r bg-slate-800 md:block w-[250px] text-white flex-shrink-0 h-screen flex flex-col">
      {/* Logo Area */}
      <div className="flex h-[80px] items-center justify-center px-6 bg-slate-900">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="inline-block h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-lg font-bold">F</span>
          <span>FinDoc Analyzer</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-grow px-3 py-4 space-y-1">
        {menuItems.map((item) => {
          // Check if the current pathname starts with the item's href
          // This handles nested routes (e.g., /documents/doc1 should highlight /documents)
          // For the dashboard, we need an exact match.
          const isActive = item.href === '/dashboard'
            ? pathname === item.href
            : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-3 text-slate-300 transition-all hover:bg-slate-700 hover:text-white',
                isActive && 'bg-slate-700 text-white' // Apply active styles
              )}
            >
              <item.icon className={cn(isActive ? 'text-indigo-400' : 'text-slate-400')} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="mt-auto p-4 border-t border-slate-700 bg-slate-900 h-[80px] flex items-center">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold">
            AB {/* Placeholder */}
          </div>
          <div>
            <p className="text-sm font-medium leading-none">Aviad B.</p> {/* Placeholder */}
            <p className="text-xs leading-none text-slate-400">Administrator</p> {/* Placeholder */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;