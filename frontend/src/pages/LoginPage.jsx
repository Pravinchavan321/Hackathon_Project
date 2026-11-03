import React from 'react'

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <div className="max-w-md w-full bg-slate-800 p-8 rounded-xl border border-slate-700 shadow-2xl">
        <h2 className="text-2xl font-bold text-white text-center mb-2">AgentShield AI</h2>
        <p className="text-sm text-slate-400 text-center mb-6">Sign in to your policy-governed workspace</p>
        <button
          onClick={() => window.location.href = '/dashboard'}
          className="w-full py-2.5 px-4 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition"
        >
          Enter Dashboard (Demo Mode)
        </button>
      </div>
    </div>
  )
}
