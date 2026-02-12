import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Chat from './pages/Chat';
import Memory from './pages/Memory';
import Dashboard from './pages/Dashboard';
import { Menu, X } from 'lucide-react';
import './App.css';

export default function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState('online');

  // Check system health on startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8001/health', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
          setSystemHealth('online');
        } else {
          setSystemHealth('offline');
        }
      } catch (error) {
        setSystemHealth('offline');
        console.error('Health check failed:', error);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Header Navigation */}
        <nav className="bg-slate-950 border-b border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              
              {/* Logo */}
              <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">TARS</span>
                </div>
                <span className="text-white font-bold text-lg hidden sm:inline">TARS</span>
              </Link>

              {/* Desktop Menu */}
              <div className="hidden md:flex gap-1">
                <NavLink to="/">💬 Chat</NavLink>
                <NavLink to="/memory">🧠 Memory</NavLink>
                <NavLink to="/dashboard">📊 Dashboard</NavLink>
              </div>

              {/* Health Status */}
              <div className="flex items-center gap-3">
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
                  systemHealth === 'online' 
                    ? 'bg-green-500/10 text-green-400' 
                    : 'bg-red-500/10 text-red-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    systemHealth === 'online' ? 'bg-green-400' : 'bg-red-400'
                  }`} />
                  {systemHealth === 'online' ? 'Online' : 'Offline'}
                </div>

                {/* Mobile Menu Button */}
                <button 
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="md:hidden p-2 hover:bg-slate-800 rounded-lg transition"
                >
                  {isMenuOpen ? (
                    <X className="text-white" size={24} />
                  ) : (
                    <Menu className="text-white" size={24} />
                  )}
                </button>
              </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
              <div className="md:hidden pb-4 space-y-2 border-t border-slate-700 pt-4">
                <MobileNavLink to="/" onClick={() => setIsMenuOpen(false)}>💬 Chat</MobileNavLink>
                <MobileNavLink to="/memory" onClick={() => setIsMenuOpen(false)}>🧠 Memory</MobileNavLink>
                <MobileNavLink to="/dashboard" onClick={() => setIsMenuOpen(false)}>📊 Dashboard</MobileNavLink>
              </div>
            )}
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/memory" element={<Memory />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-700 bg-slate-950 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-slate-400 text-sm">
              <p>TARS v1.0.0 - Distributed AI System</p>
              <p className="mt-2">© 2026 All rights reserved</p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

function NavLink({ to, children }) {
  return (
    <Link
      to={to}
      className="px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition"
    >
      {children}
    </Link>
  );
}

function MobileNavLink({ to, children, onClick }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className="block px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition"
    >
      {children}
    </Link>
  );
}
