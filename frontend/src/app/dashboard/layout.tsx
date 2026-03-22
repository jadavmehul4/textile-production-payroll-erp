'use client';
import Sidebar from '../../components/Sidebar';
import GlobalSearch from '../../components/GlobalSearch';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex bg-gray-50 min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <header className="h-16 bg-white border-b flex items-center justify-between px-8 fixed top-0 right-0 left-64 z-10">
          <h1 className="text-lg font-semibold text-gray-800">Textile ERP v1.0</h1>
          <GlobalSearch />
        </header>
        <main className="flex-1 mt-16 p-8 overflow-y-auto scrollbar-hide">
          {children}
        </main>
      </div>
    </div>
  );
}
