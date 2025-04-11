'use client'; // Make this a client component

import { usePathname } from 'next/navigation'; // Import usePathname
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Placeholder Icon components - replace with actual icons later
const SearchIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("h-4 w-4 text-slate-400", className)}
  >
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const BellIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={cn("h-5 w-5 text-slate-600", className)}
  >
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
);

const PlusIcon = ({ className }: { className?: string }) => (
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

// Helper function to get title from path
const getTitleFromPath = (path: string): string => {
  if (path === '/') return 'Dashboard'; // Assuming root is dashboard for now
  const segments = path.split('/').filter(Boolean);
  if (segments.length === 0) return 'Dashboard';
  const title = segments[0].replace(/-/g, ' '); // Replace dashes with spaces
  return title.charAt(0).toUpperCase() + title.slice(1); // Capitalize first letter
};


const Header = () => {
  const pathname = usePathname();
  const pageTitle = getTitleFromPath(pathname); // Get title dynamically

  return (
    <header className="flex h-[80px] items-center gap-4 border-b bg-white px-6 sticky top-0 z-30">
      {/* Page Title */}
      <h1 className="text-xl font-semibold text-slate-800 flex-1">
        {pageTitle}
      </h1>

      {/* Search Bar */}
      <div className="relative ml-auto flex-1 md:grow-0 max-w-sm">
        <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
        <Input
          type="search"
          placeholder="Search documents..."
          className="w-full rounded-full bg-slate-100 pl-8 md:w-[200px] lg:w-[300px] h-10"
        />
      </div>

      {/* Upload Button (Placeholder Action) */}
       <Button size="icon" className="rounded-full bg-indigo-600 hover:bg-indigo-700 h-10 w-10">
        <PlusIcon className="h-5 w-5 text-white" />
        <span className="sr-only">Upload Document</span>
      </Button>

      {/* Notifications */}
      <Button variant="outline" size="icon" className="relative rounded-full h-10 w-10">
        <BellIcon className="h-5 w-5" />
        {/* Notification Indicator */}
        <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        <span className="sr-only">Toggle notifications</span>
      </Button>

      {/* User Menu */}
      <Button variant="outline" size="icon" className="rounded-full h-10 w-10">
         <div className="h-full w-full rounded-full bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-800">
            AB {/* Placeholder */}
          </div>
        <span className="sr-only">Toggle user menu</span>
      </Button>
    </header>
  );
};

export default Header;