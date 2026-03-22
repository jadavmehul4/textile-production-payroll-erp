'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function MasterDataPage() {
  const [activeTab, setActiveTab] = useState('units');
  const [data, setData] = useState([]);

  const tabs = [
    { id: 'units', name: 'Units' },
    { id: 'buyers', name: 'Buyers' },
    { id: 'items', name: 'Items' },
    { id: 'operations', name: 'Operations' },
    { id: 'sizes', name: 'Sizes' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`http://localhost:8000/api/master-data/${activeTab}/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch master data', error);
      }
    };
    fetchData();
  }, [activeTab]);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Master Data Management</h1>
      
      <div className="flex space-x-4 mb-8 border-b pb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              activeTab === tab.id 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.name}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold capitalize">{activeTab} List</h2>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            + Add New
          </button>
        </div>

        <table className="w-full text-left">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-4 font-bold border-b">ID</th>
              <th className="p-4 font-bold border-b">Name</th>
              <th className="p-4 font-bold border-b text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item: any) => (
              <tr key={item.id} className="hover:bg-gray-50 border-b">
                <td className="p-4">{item.id}</td>
                <td className="p-4">{item.name}</td>
                <td className="p-4 text-right">
                  <button className="text-blue-600 hover:underline mr-4">Edit</button>
                  <button className="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
