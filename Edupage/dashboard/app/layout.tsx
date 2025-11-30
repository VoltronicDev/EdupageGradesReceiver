import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Edupage Dashboard',
  description: 'Grade overview with rich insights',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#0f172a_0%,_#020617_60%)] text-slate-100">
          {children}
        </div>
      </body>
    </html>
  );
}
