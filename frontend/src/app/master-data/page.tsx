'use client';
import { useState, useEffect } from 'react';
import api from '../../utils/api';

export default function MasterDataPage() {
  const [activeTab, setActiveTab] = useState('units');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const tabs = [
    { id: 'units', name: 'Units' },
    { id: 'departments', name: 'Departments' },
    { id: 'designations', name: 'Designations' },
    { id: 'buyers', name: 'Buyers' },
    { id: 'items', name: 'Items' },
    { id: 'operations', name: 'Operations' },
    { id: 'sizes', name: 'Sizes' },
    { id: 'operation-rates', name: 'Operation Rates' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/api/master-data/${activeTab}/`);
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch master data', error);
        setData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeTab]);

  const renderTableHeaders = () => {
    switch (activeTab) {
      case 'operation-rates':
        return (
          <>
            <th className="p-4 font-bold border-b text-slate-700">Buyer</th>
            <th className="p-4 font-bold border-b text-slate-700">Item</th>
            <th className="p-4 font-bold border-b text-slate-700">Operation</th>
            <th className="p-4 font-bold border-b text-slate-700">Size</th>
            <th className="p-4 font-bold border-b text-slate-700">Rate</th>
            <th className="p-4 font-bold border-b text-slate-700 text-right">Actions</th>
          </>
        );
      case 'departments':
        return (
          <>
            <th className="p-4 font-bold border-b text-slate-700">Name</th>
            <th className="p-4 font-bold border-b text-slate-700">Unit</th>
            <th className="p-4 font-bold border-b text-slate-700 text-right">Actions</th>
          </>
        );
      default:
        return (
          <>
            <th className="p-4 font-bold border-b text-slate-700">ID</th>
            <th className="p-4 font-bold border-b text-slate-700">Name</th>
            <th className="p-4 font-bold border-b text-slate-700 text-right">Actions</th>
          </>
        );
    }
  };

  const renderTableRow = (item: any) => {
    switch (activeTab) {
      case 'operation-rates':
        return (
          <>
            <td className="p-4">{item.buyer_name || item.buyer}</td>
            <td className="p-4">{item.item_name || item.item}</td>
            <td className="p-4">{item.operation_name || item.operation}</td>
            <td className="p-4">{item.size_name || item.size || 'N/A'}</td>
            <td className="p-4 font-semibold text-green-600">₹{item.rate}</td>
            <td className="p-4 text-right">
              <button className="text-blue-600 hover:underline mr-4">Edit</button>
              <button className="text-red-600 hover:underline">Delete</button>
            </td>
          </>
        );
      case 'departments':
        return (
          <>
            <td className="p-4">{item.name}</td>
            <td className="p-4">{item.unit_name || item.unit}</td>
            <td className="p-4 text-right">
              <button className="text-blue-600 hover:underline mr-4">Edit</button>
              <button className="text-red-600 hover:underline">Delete</button>
            </td>
          </>
        );
      default:
        return (
          <>
            <td className="p-4">{item.id}</td>
            <td className="p-4">{item.name}</td>
            <td className="p-4 text-right">
              <button className="text-blue-600 hover:underline mr-4">Edit</button>
              <button className="text-red-600 hover:underline">Delete</button>
            </td>
          </>
        );
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Master Data Engine</h1>
          <p className="text-slate-500 mt-2">Configure and manage global textile production constants.</p>
        </div>
        <button className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-bold shadow-lg hover:bg-indigo-700 transition-all flex items-center space-x-2">
          <span>+ Add {tabs.find(t => t.id === activeTab)?.name.slice(0, -1) || 'New'}</span>
        </button>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-8 border-b border-slate-200 pb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-md font-bold text-sm transition-all duration-200 ${
              activeTab === tab.id 
              ? 'bg-slate-900 text-white shadow-md transform scale-105' 
              : 'bg-white text-slate-600 border border-slate-200 hover:border-slate-400 hover:bg-slate-50'
            }`}
          >
            {tab.name}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800 capitalize">{activeTab.replace('-', ' ')} Overview</h2>
          <div className="relative">
            <input 
              type="text" 
              placeholder={`Search ${activeTab}...`} 
              className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-64"
            />
            <svg className="w-4 h-4 absolute left-3 top-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50">
              <tr>
                {renderTableHeaders()}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={10} className="p-12 text-center text-slate-400">
                    <div className="flex justify-center items-center space-x-2">
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:-.3s]" />
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:-.5s]" />
                    </div>
                    <span className="mt-4 block font-medium">Loading production data...</span>
                  </td>
                </tr>
              ) : data.length > 0 ? (
                data.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-indigo-50/30 transition-colors group">
                    {renderTableRow(item)}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="p-12 text-center text-slate-400 font-medium">
                    No {activeTab.replace('-', ' ')} records found in system.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
