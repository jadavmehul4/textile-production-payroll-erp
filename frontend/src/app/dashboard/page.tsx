'use client';
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function DashboardPage() {
  const [stats, setStats] = useState({ total_employees: 0, total_production: 0, total_payroll: 0 });
  const [recentProduction, setRecentProduction] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://localhost:8000/api/reports/dashboard/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data.stats);
        setRecentProduction(response.data.recent_production);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Total Employees" value={stats.total_employees} color="bg-blue-500" />
        <StatCard title="Total Production" value={stats.total_production} color="bg-green-500" />
        <StatCard title="Total Payroll" value={`₹${stats.total_payroll}`} color="bg-purple-500" />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Recent Production</h3>
        <table className="w-full text-left">
          <thead>
            <tr className="border-b">
              <th className="py-2">Employee</th>
              <th className="py-2">Quantity</th>
              <th className="py-2">Amount</th>
              <th className="py-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {recentProduction.map((entry, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="py-2">{entry.employee}</td>
                <td className="py-2">{entry.quantity}</td>
                <td className="py-2">₹{entry.amount}</td>
                <td className="py-2">{entry.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div className={`${color} text-white p-6 rounded-lg shadow-lg`}>
      <div className="text-sm uppercase font-semibold opacity-75">{title}</div>
      <div className="text-3xl font-bold mt-2">{value}</div>
    </div>
  );
}
