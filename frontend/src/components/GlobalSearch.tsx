'use client';
import { useState } from 'react';
import { Search } from 'lucide-react';

export default function GlobalSearch() {
  const [query, setQuery] = useState('');

  return (
    <div className="relative w-64">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-400" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out"
        placeholder="Global Search (Employees, Orders...)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
    </div>
  );
}
