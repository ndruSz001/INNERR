import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import '../styles/Dashboard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8001/health', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
          const data = await response.json();
          setStats({
            conversations: data.conversations || 0,
            messages: data.messages || 0,
            projects: data.projects || 0,
            documents: data.documents || 0,
            uptime: data.uptime || 0,
            lastBackup: data.last_backup || 'N/A'
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
      setIsLoading(false);
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-slate-700 border-t-purple-400 rounded-full"></div>
        <p className="text-slate-400 mt-4">Loading dashboard...</p>
      </div>
    );
  }

  // Chart data
  const conversationTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Conversations',
        data: [12, 19, 15, 25],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }
    ]
  };

  const messageDistributionData = {
    labels: ['User Messages', 'AI Responses'],
    datasets: [
      {
        data: [stats?.messages || 0, stats?.messages || 0],
        backgroundColor: ['#3b82f6', '#8b5cf6'],
        borderColor: '#1e293b'
      }
    ]
  };

  const resourceUsageData = {
    labels: ['Memory', 'CPU', 'Disk', 'Network'],
    datasets: [
      {
        label: 'Usage (%)',
        data: [45, 32, 28, 15],
        backgroundColor: [
          '#3b82f6',
          '#8b5cf6',
          '#ec4899',
          '#f59e0b'
        ]
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: '#cbd5e1' }
      }
    },
    scales: {
      y: { ticks: { color: '#cbd5e1' }, grid: { color: '#334155' } },
      x: { ticks: { color: '#cbd5e1' }, grid: { color: '#334155' } }
    }
  };

  return (
    <div className="dashboard-container max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 mb-6 shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-2">📊 Dashboard</h1>
        <p className="text-purple-100">System overview and analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Conversations"
          value={stats?.conversations || 0}
          icon="💬"
          trend="+12%"
        />
        <StatCard
          title="Messages"
          value={stats?.messages || 0}
          icon="✉️"
          trend="+8%"
        />
        <StatCard
          title="Projects"
          value={stats?.projects || 0}
          icon="📁"
          trend="+5%"
        />
        <StatCard
          title="Documents"
          value={stats?.documents || 0}
          icon="📄"
          trend="+15%"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Conversation Trends */}
        <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Conversation Trends</h2>
          <div className="h-80">
            <Line data={conversationTrendData} options={chartOptions} />
          </div>
        </div>

        {/* Message Distribution */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Message Distribution</h2>
          <div className="h-80">
            <Doughnut data={messageDistributionData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Resource Usage */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Resource Usage</h2>
        <div className="h-80">
          <Bar data={resourceUsageData} options={chartOptions} />
        </div>
      </div>

      {/* System Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
          <div className="space-y-3">
            <HealthItem label="API Server" status="online" />
            <HealthItem label="Database" status="online" />
            <HealthItem label="Cache" status="online" />
            <HealthItem label="Backup Service" status="online" />
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-3 text-sm">
            <ActivityItem time="5 min ago" event="Backup completed" />
            <ActivityItem time="15 min ago" event="New conversation started" />
            <ActivityItem time="1 hour ago" event="Project created" />
            <ActivityItem time="2 hours ago" event="System health check passed" />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, trend }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition">
      <div className="flex justify-between items-start mb-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-green-400 text-sm font-medium">{trend}</span>
      </div>
      <h3 className="text-slate-400 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

function HealthItem({ label, status }) {
  const statusColor = status === 'online' ? 'text-green-400' : 'text-red-400';
  const statusDot = status === 'online' ? '🟢' : '🔴';
  
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-300">{label}</span>
      <span className={`flex items-center gap-1 ${statusColor}`}>
        {statusDot} {status}
      </span>
    </div>
  );
}

function ActivityItem({ time, event }) {
  return (
    <div className="border-b border-slate-700 pb-3 last:border-b-0">
      <p className="text-slate-300">{event}</p>
      <p className="text-slate-500 text-xs mt-1">{time}</p>
    </div>
  );
}
