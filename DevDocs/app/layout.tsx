import type { Metadata } from 'next';
import { Inter } from 'next/font/google'; // Using Inter as a default sans-serif font
import './globals.css';
import Sidebar from '@/components/layout/Sidebar'; // Import Sidebar
import Header from '@/components/layout/Header';   // Import Header
import { cn } from '@/lib/utils'; // Assuming this path is now correct after tsconfig fix
import { Toaster } from "@/components/ui/toaster" // For shadcn/ui toasts

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'FinDoc Analyzer', // Updated title
  description: 'Analyze your financial documents efficiently.', // Updated description
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>{/* Added suppressHydrationWarning for potential server/client mismatches */}
      <body className={cn("min-h-screen bg-background font-sans antialiased", inter.className)}>
        <div className="flex min-h-screen w-full">
          <Sidebar />
          <div className="flex flex-col flex-1">
            <Header />
            <main className="flex-1 p-6 bg-slate-50"> {/* Added padding and background */}
              {children}
            </main>
          </div>
        </div>
        <Toaster /> {/* Add Toaster for shadcn/ui notifications */}
      </body>
    </html>
  );
}
