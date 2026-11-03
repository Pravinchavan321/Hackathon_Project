import React from 'react'
import { Shield, ShieldAlert, ShieldCheck, ShieldX, Lock, Key, Sliders, CheckCircle2 } from 'lucide-react'

const ACTIVE_POLICIES = [
  {
    id: 'R1_AMOUNT_LIMIT',
    name: 'Single Transaction Threshold',
    trigger: 'Amount > ₹5,000',
    effect: 'REQUIRE_APPROVAL',
    effectType: 'escalate',
    description: 'Autonomous claims exceeding ₹5,000 are paused via LangGraph interrupt() awaiting human sign-off.',
    priority: 30,
  },
  {
    id: 'R2_BANNED_CATEGORY',
    name: 'Prohibited Expense Categories',
    trigger: 'Category in [alcohol, gambling, personal, gift_cards]',
    effect: 'BLOCK',
    effectType: 'block',
    description: 'Strict prohibition on non-compliant expense categories. Hard deny with zero tool execution.',
    priority: 10,
  },
  {
    id: 'R3_SUSPICIOUS_CONTENT',
    name: 'Prompt Injection & Tamper Shield',
    trigger: 'Adversarial override / prompt injection heuristics',
    effect: 'BLOCK',
    effectType: 'block',
    description: 'Deterministic regex & semantic boundary checks neutralize jailbreak attempts before tool access.',
    priority: 15,
  },
  {
    id: 'R4_DAILY_CAP',
    name: 'Cumulative Daily Limit',
    trigger: 'User 24h total spend > ₹15,000',
    effect: 'REQUIRE_APPROVAL',
    effectType: 'escalate',
    description: 'Aggregated claims per employee are tracked to prevent split-transaction threshold circumvention.',
    priority: 35,
  },
  {
    id: 'R5_DUPLICATE_RECEIPT',
    name: 'Cryptographic Duplicate Detection',
    trigger: 'SHA-256 receipt hash matches prior claim',
    effect: 'BLOCK',
    effectType: 'block',
    description: 'Identical invoice files submitted multiple times are automatically flagged and blocked.',
    priority: 20,
  },
  {
    id: 'R6_MISSING_RECEIPT',
    name: 'Receipt Verification Requirement',
    trigger: 'Receipt missing or magic bytes validation fails',
    effect: 'BLOCK',
    effectType: 'block',
    description: 'Only valid PNG, JPEG, PDF, and WEBP files with verified magic bytes are permitted.',
    priority: 25,
  },
]

export default function PoliciesPage() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Shield className="w-6 h-6 text-purple-600" />
          Deterministic Governance Rules &amp; Policies
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Zero-LLM deterministic policy engine. Rule precedence: <strong>BLOCK &gt; ESCALATE &gt; ALLOW</strong>.
        </p>
      </div>

      {/* Architecture Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2 bg-rose-100 text-rose-700 rounded-lg shrink-0">
            <ShieldX className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">1. Hard Blocks (Highest)</h4>
            <p className="text-xs text-slate-500 mt-1">
              Violations like banned categories or injections immediately terminate workflow. Cannot be overridden.
            </p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2 bg-amber-100 text-amber-700 rounded-lg shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">2. Human Escalation</h4>
            <p className="text-xs text-slate-500 mt-1">
              Amounts &gt; ₹5,000 checkpoint state and issue a cryptographic approval ticket bound to action hash.
            </p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2 bg-emerald-100 text-emerald-700 rounded-lg shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">3. Governed Allow</h4>
            <p className="text-xs text-slate-500 mt-1">
              Only compliant requests meeting all bounds receive a single-use signed execution ticket.
            </p>
          </div>
        </div>
      </div>

      {/* Rules Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-purple-600" />
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Active Policy Matrix ({ACTIVE_POLICIES.length} Rules Enforced)
            </h3>
          </div>
          <span className="text-xs font-mono text-emerald-600 font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Fail-Closed Active
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {ACTIVE_POLICIES.map((rule) => (
            <div key={rule.id} className="p-4 hover:bg-slate-50/50 transition flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-purple-700">{rule.id}</span>
                  <span className="text-slate-300">•</span>
                  <span className="text-sm font-bold text-slate-800">{rule.name}</span>
                </div>
                <p className="text-xs text-slate-500">{rule.description}</p>
                <div className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded inline-block">
                  Trigger Condition: {rule.trigger}
                </div>
              </div>

              <div className="shrink-0 flex items-center gap-3">
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                  rule.effectType === 'block' 
                    ? 'bg-rose-50 text-rose-700 border-rose-200' 
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  {rule.effect}
                </span>
                <span className="text-[11px] font-mono text-slate-400">Pri: {rule.priority}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
