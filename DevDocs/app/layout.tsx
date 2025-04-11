import type { Metadata } from 'next';
import { Inter } from 'next/font/google'; // Using Inter as a default sans-serif font
import './globals.css';
import Sidebar from '@/components/layout/Sidebar'; // Import Sidebar
import Header from '@/components/layout/Header';   // Import Header
import { cn } from '@/lib/utils'; // Assuming this path is now correct after tsconfig fix
import { Toaster } from "@/components/ui/toaster" // For shadcn/ui toasts
import LanguageProvider from '@/i18n/LanguageProvider'; // Import Language Provider
import { ThemeProvider } from '@/providers/ThemeProvider'; // Import Theme Provider

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
    <html suppressHydrationWarning>{/* Added suppressHydrationWarning for potential server/client mismatches */}
      <body className={cn("min-h-screen bg-background font-sans antialiased", inter.className)}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <LanguageProvider>
            <div className="flex min-h-screen w-full">
              <Sidebar />
              <div className="flex flex-col flex-1">
                <Header />
                <main className="flex-1 p-6 bg-slate-50 dark:bg-slate-900"> {/* Added padding and background with dark mode support */}
                  {children}
                </main>
              </div>
            </div>
            <Toaster /> {/* Add Toaster for shadcn/ui notifications */}
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
