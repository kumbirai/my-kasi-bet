import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Icon } from './ui';

const NAV_ITEMS = [
  { name: 'Dashboard',   href: '/dashboard',   icon: 'dashboard' },
  { name: 'Users',       href: '/users',        icon: 'users'     },
  { name: 'Deposits',    href: '/deposits',     icon: 'deposit'   },
  { name: 'Withdrawals', href: '/withdrawals',  icon: 'withdrawal'},
  { name: 'Bets',        href: '/bets',         icon: 'bets'      },
  { name: 'Matches',     href: '/matches',      icon: 'matches'   },
  { name: 'Reports',     href: '/reports',      icon: 'reports'   },
];

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { admin, logout } = useAuth();

  const handleLogout = () => { logout(); navigate('/login'); };
  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-kasi-900 flex">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-kasi-950 border-r border-white/[0.05] flex flex-col transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-white/[0.05] shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-600/30">
              <span className="text-xs font-black text-white tracking-tight">KB</span>
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-tight">MyKasiBets</p>
              <p className="text-[10px] text-slate-500 leading-tight">Admin</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            aria-label="Close sidebar"
          >
            <Icon name="close" className="w-4 h-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 cursor-pointer ${
                isActive(item.href)
                  ? 'bg-blue-500/15 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              <Icon name={item.icon} className="w-[18px] h-[18px] shrink-0" />
              {item.name}
            </Link>
          ))}
        </nav>

        {/* User */}
        <div className="p-3 border-t border-white/[0.05] shrink-0">
          <div className="flex items-center gap-3 px-3 py-2.5 mb-1">
            <div className="w-7 h-7 rounded-full bg-kasi-700 border border-white/10 flex items-center justify-center shrink-0">
              <span className="text-[11px] font-semibold text-slate-300">
                {(admin?.email?.[0] || 'A').toUpperCase()}
              </span>
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">{admin?.email || 'Admin'}</p>
              <p className="text-[10px] text-slate-500 capitalize">{admin?.role || 'admin'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-slate-500 hover:text-red-400 hover:bg-red-400/[0.06] rounded-xl transition-colors duration-150 cursor-pointer"
          >
            <Icon name="logout" className="w-[18px] h-[18px] shrink-0" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Content */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-10 h-16 bg-kasi-900/90 backdrop-blur border-b border-white/[0.05] flex items-center px-6 gap-4 shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            aria-label="Open sidebar"
          >
            <Icon name="menu" className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-kasi-750 border border-white/10 flex items-center justify-center">
              <span className="text-xs font-semibold text-slate-300">
                {(admin?.email?.[0] || 'A').toUpperCase()}
              </span>
            </div>
            <span className="hidden sm:block text-sm text-slate-400 max-w-[180px] truncate">
              {admin?.email || 'Admin'}
            </span>
          </div>
        </header>

        {/* Page */}
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
