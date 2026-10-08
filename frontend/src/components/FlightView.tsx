import React from "react";
import { FlightResearch } from "../types";
import { Plane, ArrowRight, ShieldCheck, AlertCircle, Clock, CheckCircle2 } from "lucide-react";

interface FlightViewProps {
  flight: FlightResearch;
  currency: string;
}

export const FlightView: React.FC<FlightViewProps> = ({ flight, currency }) => {
  return (
    <div className="space-y-6">
      {/* Flight Header Card */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span
                className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
                  flight.is_live_data
                    ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
                }`}
              >
                {flight.is_live_data ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> LIVE API DATA
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-3.5 h-3.5 text-voyage-500" /> ESTIMATED INFORMATION
                  </>
                )}
              </span>
              {flight.estimated_duration_hours && (
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> Approx {flight.estimated_duration_hours}h duration
                </span>
              )}
            </div>

            {/* Route corridor */}
            <div className="flex items-center gap-3">
              <span className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                {flight.origin_airport || "Origin Hub"}
              </span>
              <ArrowRight className="w-5 h-5 text-voyage-600 dark:text-voyage-400 shrink-0" />
              <span className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                {flight.destination_airport || "Destination Hub"}
              </span>
            </div>
          </div>

          {/* Fare range */}
          {flight.fare_range_low && flight.fare_range_high && (
            <div className="sm:text-right">
              <span className="text-xs text-slate-500 block mb-0.5">Est. Fare Corridor (Roundtrip)</span>
              <div className="text-2xl font-extrabold text-voyage-600 dark:text-voyage-400">
                {currency} {flight.fare_range_low.toLocaleString()} – {flight.fare_range_high.toLocaleString()}
              </div>
              <span className="text-[11px] text-slate-400">per person estimate</span>
            </div>
          )}
        </div>

        {flight.route_summary && (
          <p className="text-sm text-slate-600 dark:text-slate-300 border-t border-slate-100 dark:border-slate-800 pt-3">
            {flight.route_summary}
          </p>
        )}

        {flight.api_status_note && (
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/50 p-2.5 rounded-lg border border-slate-200/50 dark:border-slate-800/50">
            <AlertCircle className="w-4 h-4 text-slate-400 shrink-0" />
            <span>{flight.api_status_note}</span>
          </div>
        )}
      </div>

      {/* Airlines Operating on Route */}
      {flight.airlines && flight.airlines.length > 0 && (
        <div className="glass-panel p-5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Major Carriers Operating this Corridor
          </h4>
          <div className="flex flex-wrap gap-2">
            {flight.airlines.map((airline, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-800 dark:text-slate-200 shadow-sm"
              >
                <Plane className="w-3.5 h-3.5 text-voyage-500" />
                {airline}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Direct and Connecting Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Direct */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
            <span>Direct Flight Options</span>
            <span className="text-[10px] text-emerald-600 font-semibold">Non-stop</span>
          </h4>
          {flight.direct_options && flight.direct_options.length > 0 ? (
            flight.direct_options.map((opt, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between font-bold text-slate-900 dark:text-white">
                  <span>{opt.airline}</span>
                  {opt.estimated_price && (
                    <span className="text-voyage-600 dark:text-voyage-400">
                      {currency} {opt.estimated_price.toLocaleString()}
                    </span>
                  )}
                </div>
                <div className="text-slate-500 flex items-center gap-2">
                  <span>{opt.departure_airport} → {opt.arrival_airport}</span>
                  {opt.duration_hours && <span>• {opt.duration_hours}h</span>}
                </div>
                {opt.notes && <p className="text-[11px] text-slate-400 italic">{opt.notes}</p>}
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-400 italic">No non-stop commercial flights registered for this corridor. Transit flights recommended.</p>
          )}
        </div>

        {/* Connecting */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
            <span>Connecting / 1-Stop Options</span>
            <span className="text-[10px] text-sky-600 font-semibold">1 Stop Transit</span>
          </h4>
          {flight.connecting_options && flight.connecting_options.length > 0 ? (
            flight.connecting_options.map((opt, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between font-bold text-slate-900 dark:text-white">
                  <span>{opt.airline}</span>
                  {opt.estimated_price && (
                    <span className="text-voyage-600 dark:text-voyage-400">
                      {currency} {opt.estimated_price.toLocaleString()}
                    </span>
                  )}
                </div>
                <div className="text-slate-500 flex items-center gap-2">
                  <span>{opt.departure_airport} → {opt.arrival_airport}</span>
                  {opt.duration_hours && <span>• {opt.duration_hours}h total</span>}
                </div>
                {opt.notes && <p className="text-[11px] text-slate-400 italic">{opt.notes}</p>}
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-400 italic">Connecting routes are calculated automatically based on airline hub schedules.</p>
          )}
        </div>
      </div>
    </div>
  );
};
