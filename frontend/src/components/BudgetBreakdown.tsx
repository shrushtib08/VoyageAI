import React, { useState } from "react";
import { Budget } from "../types";
import { Coins, AlertCircle, CheckCircle, Info, ShieldAlert, Sparkles } from "lucide-react";

interface BudgetBreakdownProps {
  budget: Budget;
  targetBudget?: number;
  travellers: number;
}

const CURRENCY_RATES: Record<string, number> = {
  INR: 1,
  USD: 0.012,
  EUR: 0.011,
  GBP: 0.0095,
  JPY: 1.85,
};

const CURRENCY_SYMBOLS: Record<string, string> = {
  INR: "₹",
  USD: "$",
  EUR: "€",
  GBP: "£",
  JPY: "¥",
};

export const BudgetBreakdown: React.FC<BudgetBreakdownProps> = ({
  budget,
  targetBudget,
  travellers,
}) => {
  const [selectedCurrency, setSelectedCurrency] = useState<string>(budget.currency || "INR");

  const baseRate = CURRENCY_RATES[budget.currency] || 1;
  const targetRate = CURRENCY_RATES[selectedCurrency] || 1;
  const conversionFactor = targetRate / baseRate;

  const formatAmount = (val: number) => {
    const converted = val * conversionFactor;
    const sym = CURRENCY_SYMBOLS[selectedCurrency] || selectedCurrency;
    return `${sym} ${converted.toLocaleString(undefined, {
      minimumFractionDigits: selectedCurrency === "JPY" ? 0 : 2,
      maximumFractionDigits: selectedCurrency === "JPY" ? 0 : 2,
    })}`;
  };

  const categories = [
    { label: "Flights & Transit", amount: budget.flights_cost, color: "bg-sky-500", key: "Flights" },
    { label: "Accommodation", amount: budget.accommodation_cost, color: "bg-indigo-500", key: "Accommodation" },
    { label: "Food & Dining", amount: budget.food_cost, color: "bg-rose-500", key: "Food & Dining" },
    { label: "Local Transportation", amount: budget.local_transport_cost, color: "bg-amber-500", key: "Local Transportation" },
    { label: "Activities & Tours", amount: budget.activities_cost, color: "bg-purple-500", key: "Activities & Entry Fees" },
    { label: "Miscellaneous", amount: budget.misc_cost, color: "bg-slate-500", key: "Miscellaneous & Shopping" },
    { label: "Emergency Reserve (7%)", amount: budget.emergency_buffer, color: "bg-emerald-500", key: "Emergency Buffer" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Summary Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-voyage-950 to-slate-900 text-white shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1.5 rounded-lg bg-white/10 text-voyage-300">
                <Coins className="w-4 h-4" />
              </span>
              <span className="text-xs font-semibold uppercase tracking-wider text-voyage-200">
                Audited Financial Projection
              </span>
            </div>
            <div className="flex items-baseline gap-3">
              <h3 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
                {formatAmount(budget.total_budget)}
              </h3>
              <span className="text-xs text-voyage-300 font-medium">
                (for {travellers} traveller{travellers > 1 ? "s" : ""})
              </span>
            </div>
          </div>

          {/* Currency Switcher */}
          <div className="flex items-center gap-2 bg-white/10 p-1 rounded-xl self-start sm:self-auto border border-white/10">
            {Object.keys(CURRENCY_RATES).map((curr) => (
              <button
                key={curr}
                onClick={() => setSelectedCurrency(curr)}
                className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-colors ${
                  selectedCurrency === curr
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-white/80 hover:text-white hover:bg-white/5"
                }`}
              >
                {curr}
              </button>
            ))}
          </div>
        </div>

        {/* Per-person & buffer stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Per-Person Cost</span>
            <span className="text-base font-bold text-white">
              {formatAmount(budget.per_person_cost)}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Core Subtotal</span>
            <span className="text-base font-bold text-white">
              {formatAmount(budget.subtotal)}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Contingency Buffer</span>
            <span className="text-base font-bold text-emerald-400">
              {formatAmount(budget.emergency_buffer)}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Confidence Status</span>
            <span className="inline-flex items-center gap-1 text-emerald-300 font-semibold">
              <Sparkles className="w-3 h-3" /> Researched Estimate
            </span>
          </div>
        </div>
      </div>

      {/* Visual Category Distribution Bar */}
      <div className="glass-panel p-5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Resource Allocation Distribution
        </h4>
        <div className="w-full h-3.5 rounded-full overflow-hidden flex bg-slate-200 dark:bg-slate-800">
          {categories.map((c) => {
            const pct = budget.total_budget > 0 ? (c.amount / budget.total_budget) * 100 : 0;
            return (
              <div
                key={c.label}
                style={{ width: `${pct}%` }}
                className={`${c.color} h-full transition-all duration-300`}
                title={`${c.label}: ${pct.toFixed(1)}%`}
              />
            );
          })}
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-2 pt-1 text-[11px] text-slate-600 dark:text-slate-400">
          {categories.map((c) => {
            const pct = budget.total_budget > 0 ? ((c.amount / budget.total_budget) * 100).toFixed(1) : "0";
            return (
              <div key={c.label} className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${c.color}`} />
                <span>{c.label} ({pct}%)</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Categorized Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((c) => {
          const detail = budget.category_breakdown?.[c.key];
          return (
            <div
              key={c.label}
              className="p-4 rounded-xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {c.label}
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                  {budget.total_budget > 0 ? ((c.amount / budget.total_budget) * 100).toFixed(0) : 0}%
                </span>
              </div>
              <p className="text-xl font-bold text-slate-900 dark:text-white">
                {formatAmount(c.amount)}
              </p>
              {detail?.notes && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2">
                  {detail.notes}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Advisory & Comparison Note */}
      {budget.budget_advice && (
        <div className="p-4 rounded-xl bg-voyage-50 dark:bg-voyage-950/40 border border-voyage-200 dark:border-voyage-800/80 flex items-start gap-3">
          <Info className="w-5 h-5 text-voyage-600 dark:text-voyage-400 shrink-0 mt-0.5" />
          <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1">
            <span className="font-bold text-voyage-900 dark:text-voyage-200">
              Budget Strategist Note
            </span>
            <p className="leading-relaxed">{budget.budget_advice}</p>
          </div>
        </div>
      )}
    </div>
  );
};
