'use client';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Users, Factory, FileText, Settings, LogOut } from 'lucide-react';
import Link from 'next/link';

export default function Sidebar() {
  const { user, logout } = useAuth();

  const menuItems = [
    { name: 'Dashboard', icon: <LayoutDashboard size={20} />, href: '/dashboard' },
    { name: 'Employees', icon: <Users size={20} />, href: '/employees' },
    { name: 'Production', icon: <Factory size={20} />, href: '/production' },
    { name: 'Reports', icon: <FileText size={20} />, href: '/reports' },
    { name: 'Master Data', icon: <Settings size={20} />, href: '/master-data' },
  ];

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-slate-900 text-white p-4 flex flex-col">
      <div className="text-xl font-bold mb-8 text-center text-blue-400">
        TEXTILE ERP
      </div>
      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => (
          <Link key={item.name} href={item.href} className="flex items-center space-x-3 p-2 rounded hover:bg-slate-800 transition-colors">
            {item.icon}
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>
      <button onClick={logout} className="flex items-center space-x-3 p-2 rounded hover:bg-red-800 transition-colors mt-auto">
        <LogOut size={20} />
        <span>Logout</span>
      </button>
    </div>
  );
}
