import React from 'react'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Tasks</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">142</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Policy Enforced</p>
          <p className="text-3xl font-bold text-emerald-600 mt-2">100%</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Approvals</p>
          <p className="text-3xl font-bold text-amber-500 mt-2">3</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Blocked Violations</p>
          <p className="text-3xl font-bold text-rose-600 mt-2">16</p>
        </div>
      </div>
    </div>
  )
}
