import React, { useState, useEffect } from 'react'
import { 
  ShieldCheck, ShieldX, Clock, RefreshCw, AlertTriangle, 
  CheckCircle2, XCircle, FileText, Hash, ArrowRight, UserCheck 
} from 'lucide-react'
import { apiService } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function ApprovalsPage() {
  const { user } = useAuth()
  const [approvals, setApprovals] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedApproval, setSelectedApproval] = useState(null)
  const [reviewNote, setReviewNote] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [notification, setNotification] = useState(null)

  const fetchPending = async () => {
    setLoading(true)
    try {
      const res = await apiService.getPendingApprovals()
      setApprovals(res.data || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPending()
  }, [])

  const handleDecision = async (verdict) => {
    if (!selectedApproval) return
    setActionLoading(true)
    try {
      // 1. Submit human manager decision
      await apiService.decideApproval(selectedApproval.approval_id, {
        verdict,
        reason: reviewNote || `Manager ${verdict} via dashboard`,
      })

      // 2. Resume the checkpointed task workflow
      if (selectedApproval.task_id) {
        await apiService.resumeTask(selectedApproval.task_id, {
          approval_id: selectedApproval.approval_id,
          verdict,
        })
      }

      setNotification({
        type: verdict === 'approved' ? 'success' : 'error',
        message: `Approval ${selectedApproval.approval_id} ${verdict} and workflow resumed!`,
      })

      setSelectedApproval(null)
      setReviewNote('')
      fetchPending()
    } catch (err) {
      console.error(err)
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Error recording decision',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const isSelfApproval = selectedApproval?.requester_id === user?.id

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-purple-600" />
            Human Approval Manager
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Cryptographically bound exact-action review for high-risk agent operations.
          </p>
        </div>
        <button
          onClick={fetchPending}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg border border-purple-200 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div className={`p-4 rounded-xl border text-sm flex items-center justify-between ${
          notification.type === 'success' 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
            : 'bg-rose-50 border-rose-200 text-rose-800'
        }`}>
          <div className="flex items-center gap-2">
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-600" />
            )}
            <span>{notification.message}</span>
          </div>
          <button 
            onClick={() => setNotification(null)}
            className="text-xs font-bold underline hover:opacity-75"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Approvals Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-500" />
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Pending Authorization Queue ({approvals.length})
            </h3>
          </div>
          <span className="text-xs text-slate-400">Precedence: BLOCK &gt; ESCALATE &gt; ALLOW</span>
        </div>

        {approvals.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600">No Pending Approvals</p>
            <p className="text-xs text-slate-400 mt-1">
              All agent actions have been processed or auto-resolved by policy.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Ticket ID</th>
                  <th className="py-3 px-4">Requester</th>
                  <th className="py-3 px-4">Proposed Tool</th>
                  <th className="py-3 px-4">Amount / Category</th>
                  <th className="py-3 px-4">Trigger Policy</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {approvals.map((appr) => {
                  const prop = appr.proposed_action?.parameters || {}
                  return (
                    <tr key={appr.approval_id} className="hover:bg-slate-50/60 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-purple-700">
                        {appr.approval_id}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-800">
                        {appr.requester_id}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">
                        {appr.proposed_action?.tool || 'submit_claim'}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-semibold text-slate-900">
                          ₹{Number(prop.amount || 0).toLocaleString()}
                        </span>
                        <span className="text-slate-400 mx-1">•</span>
                        <span className="capitalize text-slate-600">{prop.category || 'expense'}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                          {appr.reasons?.join(', ') || 'R1_AMOUNT_LIMIT'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedApproval(appr)}
                          className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs rounded-md shadow-sm transition"
                        >
                          Review &amp; Decide
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {selectedApproval && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-5 animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-xs font-mono text-purple-600 font-bold">{selectedApproval.approval_id}</span>
                <h3 className="text-lg font-bold text-slate-900 mt-0.5">Manager Action Review</h3>
              </div>
              <button
                onClick={() => setSelectedApproval(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Self-approval Warning */}
            {isSelfApproval && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-lg flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>
                  <strong>Self-Approval Blocked:</strong> You requested this transaction. Another manager must review and authorize it.
                </span>
              </div>
            )}

            {/* Exact Action Hash Binding */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1 font-mono text-xs">
              <div className="flex items-center justify-between text-slate-500">
                <span className="flex items-center gap-1 font-semibold">
                  <Hash className="w-3.5 h-3.5 text-purple-600" />
                  Exact Action Hash (SHA-256)
                </span>
                <span className="text-[10px] text-emerald-600 font-bold">TAMPER-PROOF BOUND</span>
              </div>
              <p className="text-slate-800 font-bold break-all">{selectedApproval.action_hash}</p>
            </div>

            {/* Proposed Parameters Preview */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                <span className="text-slate-400 font-medium">Claim Amount</span>
                <p className="text-base font-bold text-slate-900 mt-1">
                  ₹{Number(selectedApproval.proposed_action?.parameters?.amount || 0).toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                <span className="text-slate-400 font-medium">Category &amp; Merchant</span>
                <p className="text-sm font-semibold text-slate-800 mt-1 capitalize">
                  {selectedApproval.proposed_action?.parameters?.category} • {selectedApproval.proposed_action?.parameters?.merchant}
                </p>
              </div>
            </div>

            {/* Manager Note Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Manager Review Note / Justification
              </label>
              <textarea
                rows={2}
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
                placeholder="e.g., Verified business purpose for client travel"
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Decision Buttons */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                onClick={() => setSelectedApproval(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDecision('rejected')}
                disabled={actionLoading || isSelfApproval}
                className="px-4 py-2 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition disabled:opacity-50"
              >
                Reject Claim
              </button>
              <button
                onClick={() => handleDecision('approved')}
                disabled={actionLoading || isSelfApproval}
                className="px-4 py-2 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg shadow-sm transition disabled:opacity-50 flex items-center gap-1.5"
              >
                {actionLoading && <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                <span>Authorize &amp; Resume Agent</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
