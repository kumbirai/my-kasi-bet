import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { admin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Users', href: '/users', icon: '👥' },
    { name: 'Deposits', href: '/deposits', icon: '💰' },
    { name: 'Withdrawals', href: '/withdrawals', icon: '💸' },
    { name: 'Bets', href: '/bets', icon: '🎲' },
    { name: 'Matches', href: '/matches', icon: '⚽' },
    { name: 'Reports', href: '/reports', icon: '📈' },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-shadow-grey-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-shadow-grey-600 bg-opacity-75 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-shadow-grey-900 text-white transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-shadow-grey-800">
          <h1 className="text-xl font-bold">MyKasiBets Admin</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-shadow-grey-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        <nav className="mt-8">
          <div className="px-4 space-y-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  isActive(item.href)
                    ? 'bg-true-cobalt-600 text-white'
                    : 'text-shadow-grey-300 hover:bg-shadow-grey-800 hover:text-white'
                }`}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </div>
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-shadow-grey-800">
          <div className="mb-4 px-4">
            <p className="text-sm text-shadow-grey-400">Logged in as</p>
            <p className="text-sm font-medium text-white">{admin?.email || 'Admin'}</p>
            <p className="text-xs text-shadow-grey-500 capitalize">{admin?.role || 'Admin'}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-sm font-medium text-white bg-shadow-grey-700 rounded-lg hover:bg-shadow-grey-800 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-10 bg-white shadow-sm">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-shadow-grey-600 hover:text-shadow-grey-900"
            >
              ☰
            </button>
            <div className="flex-1" />
            <div className="text-sm text-shadow-grey-600">
              Welcome, {admin?.email || 'Admin'}
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
