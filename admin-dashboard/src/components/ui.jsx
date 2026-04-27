import React from 'react';

export const ICONS = {
  dashboard:   'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  users:       'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
  deposit:     'M19 14l-7 7m0 0l-7-7m7 7V3',
  withdrawal:  'M5 10l7-7m0 0l7 7m-7-7v18',
  bets:        'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  matches:     'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  reports:     'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  logout:      'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1',
  menu:        'M4 6h16M4 12h16M4 18h16',
  close:       'M6 18L18 6M6 6l12 12',
  search:      'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  download:    'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
  check:       'M5 13l4 4L19 7',
  plus:        'M12 4v16m8-8H4',
  chevronLeft: 'M15 19l-7-7 7-7',
  chevronRight:'M9 5l7 7-7 7',
  lock:        'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
  coin:        'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  wallet:      'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
  user:        'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
};

export const Icon = ({ name, className = 'w-5 h-5' }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={1.5}
    aria-hidden="true"
  >
    <path strokeLinecap="round" strokeLinejoin="round" d={ICONS[name] || ''} />
  </svg>
);

const BADGE_CLS = {
  pending:   'bg-amber-400/10   text-amber-400   border-amber-400/20',
  approved:  'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  rejected:  'bg-red-400/10     text-red-400     border-red-400/20',
  won:       'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  lost:      'bg-red-400/10     text-red-400     border-red-400/20',
  active:    'bg-blue-400/10    text-blue-400    border-blue-400/20',
  open:      'bg-blue-400/10    text-blue-400    border-blue-400/20',
  settled:   'bg-slate-400/10   text-slate-400   border-slate-400/20',
  cancelled: 'bg-slate-400/10   text-slate-400   border-slate-400/20',
  blocked:   'bg-red-400/10     text-red-400     border-red-400/20',
};

export const Badge = ({ status }) => {
  const cls = BADGE_CLS[status?.toLowerCase()] ||
    'bg-slate-400/10 text-slate-400 border-slate-400/20';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${cls}`}>
      {status}
    </span>
  );
};

export const Modal = ({ open, onClose, title, children, maxWidth = 'max-w-lg' }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-start justify-center z-50 p-4 overflow-y-auto">
      <div className={`bg-kasi-800 border border-white/10 rounded-2xl w-full ${maxWidth} shadow-2xl my-8`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.06]">
          <h2 className="text-base font-semibold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <Icon name="close" className="w-4 h-4" />
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
};

export const Pagination = ({ page, totalPages, total, pageSize, onPage }) => {
  if (totalPages <= 1) return null;
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  return (
    <div className="flex items-center justify-between px-6 py-3 border-t border-white/[0.05]">
      <span className="text-xs text-slate-500">{from}–{to} of {total.toLocaleString()}</span>
      <div className="flex gap-1.5">
        <button
          onClick={() => onPage(page - 1)}
          disabled={page === 1}
          className="p-2 rounded-lg bg-kasi-750 border border-white/[0.08] text-slate-400 hover:text-white hover:bg-kasi-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"
          aria-label="Previous"
        >
          <Icon name="chevronLeft" className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPage(page + 1)}
          disabled={page === totalPages}
          className="p-2 rounded-lg bg-kasi-750 border border-white/[0.08] text-slate-400 hover:text-white hover:bg-kasi-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"
          aria-label="Next"
        >
          <Icon name="chevronRight" className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export const SkeletonRows = ({ cols = 5, rows = 7 }) => (
  <>
    {Array.from({ length: rows }).map((_, i) => (
      <tr key={i} className="border-b border-white/[0.04]">
        {Array.from({ length: cols }).map((_, j) => (
          <td key={j} className="px-6 py-4">
            <div
              className="h-3.5 bg-kasi-700 rounded animate-pulse"
              style={{ width: `${50 + ((i * 7 + j * 13) % 40)}%` }}
            />
          </td>
        ))}
      </tr>
    ))}
  </>
);

/* ── Shared class strings ── */
export const inputCls =
  'w-full px-3 py-2.5 bg-kasi-750 border border-white/[0.08] text-slate-100 placeholder-slate-500 ' +
  'rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 ' +
  'transition-colors duration-150';

export const selectCls = inputCls + ' cursor-pointer';
export const labelCls  = 'block text-sm font-medium text-slate-300 mb-1.5';
export const textareaCls = inputCls + ' resize-none leading-relaxed';

export const btnPrimary =
  'inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 ' +
  'text-white text-sm font-medium rounded-lg transition-colors duration-150 cursor-pointer ' +
  'disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500/40';

export const btnSecondary =
  'inline-flex items-center gap-2 px-4 py-2.5 bg-kasi-700 hover:bg-kasi-650 ' +
  'text-slate-200 text-sm font-medium rounded-lg border border-white/[0.08] ' +
  'transition-colors duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

export const btnDanger =
  'inline-flex items-center gap-2 px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 ' +
  'text-red-400 text-sm font-medium rounded-lg border border-red-500/20 ' +
  'transition-colors duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

export const btnSuccess =
  'inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 ' +
  'text-emerald-400 text-sm font-medium rounded-lg border border-emerald-500/20 ' +
  'transition-colors duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

/* ── Table primitives ── */
export const tableCls   = 'bg-kasi-800 border border-white/[0.05] rounded-xl overflow-hidden';
export const theadCls   = 'bg-kasi-750';
export const thCls      = 'px-6 py-3.5 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider';
export const tdCls      = 'px-6 py-4 text-sm text-slate-300';
export const trHoverCls = 'border-b border-white/[0.04] hover:bg-kasi-750 transition-colors duration-100';
