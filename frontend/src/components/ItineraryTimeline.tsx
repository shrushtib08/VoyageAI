import React, { useState } from "react";
import { Itinerary, ItineraryDay } from "../types";
import {
  ChevronDown,
  ChevronUp,
  Sun,
  Sunset,
  Moon,
  MapPin,
  Bus,
  Coins,
  ShieldCheck,
  CheckCircle,
  Sparkles,
  Info,
} from "lucide-react";

interface ItineraryTimelineProps {
  itinerary: Itinerary;
  currency: string;
}

export const ItineraryTimeline: React.FC<ItineraryTimelineProps> = ({ itinerary, currency }) => {
  const [expandedDays, setExpandedDays] = useState<Record<number, boolean>>(() => {
    // Default first 3 days expanded
    const initial: Record<number, boolean> = {};
    itinerary.days.forEach((d, idx) => {
      initial[d.day_number] = idx < 3;
    });
    return initial;
  });

  const toggleDay = (dayNum: number) => {
    setExpandedDays((prev) => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const expandAll = () => {
    const all: Record<number, boolean> = {};
    itinerary.days.forEach((d) => (all[d.day_number] = true));
    setExpandedDays(all);
  };

  const collapseAll = () => {
    setExpandedDays({});
  };

  return (
    <div className="space-y-6">
      {/* Overview & Validation Bar */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                <ShieldCheck className="w-3.5 h-3.5" />
                Audited Feasible ({itinerary.validation_status})
              </span>
              {itinerary.revision_count > 0 && (
                <span className="text-[11px] text-slate-500 dark:text-slate-400">
                  Refined through {itinerary.revision_count} critique cycle{itinerary.revision_count > 1 ? "s" : ""}
                </span>
              )}
            </div>
            <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
              {itinerary.title || `${itinerary.total_days}-Day Curated Journey`}
            </h3>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <button
              onClick={expandAll}
              className="px-3 py-1 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300"
            >
              Expand All
            </button>
            <button
              onClick={collapseAll}
              className="px-3 py-1 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300"
            >
              Collapse All
            </button>
          </div>
        </div>

        {itinerary.overview && (
          <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed border-t border-slate-100 dark:border-slate-800/80 pt-3">
            {itinerary.overview}
          </p>
        )}

        {itinerary.practical_tips && itinerary.practical_tips.length > 0 && (
          <div className="pt-2 flex flex-wrap gap-2 text-xs">
            {itinerary.practical_tips.map((tip, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium"
              >
                <Sparkles className="w-3 h-3 text-voyage-500" />
                {tip}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Days Timeline */}
      <div className="space-y-4">
        {itinerary.days.map((day) => {
          const isExpanded = !!expandedDays[day.day_number];

          return (
            <div
              key={day.day_number}
              className="rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 overflow-hidden transition-all duration-200"
            >
              {/* Day Header Trigger */}
              <button
                onClick={() => toggleDay(day.day_number)}
                className="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-voyage-600 to-indigo-600 text-white font-black text-sm flex items-center justify-center shrink-0 shadow-sm shadow-voyage-500/20">
                    D{day.day_number}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">
                        {day.date_str || `Day ${day.day_number}`}
                      </span>
                      {day.estimated_daily_spend > 0 && (
                        <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                          • Est. Spend: {currency} {day.estimated_daily_spend.toLocaleString()}
                        </span>
                      )}
                    </div>
                    <h4 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      {day.theme}
                    </h4>
                  </div>
                </div>

                <div className="p-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500">
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </div>
              </button>

              {/* Day Expanded Details */}
              {isExpanded && (
                <div className="p-4 sm:p-6 border-t border-slate-200/60 dark:border-slate-800/60 space-y-5 bg-slate-50/30 dark:bg-slate-900/40">
                  {/* Time Blocks (Morning, Afternoon, Evening) */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Morning */}
                    <div className="p-4 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 space-y-2.5">
                      <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-bold text-xs uppercase tracking-wider">
                        <Sun className="w-4 h-4" />
                        <span>Morning • {day.morning?.time || "09:00 - 12:30"}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 font-medium leading-snug">
                        {day.morning?.activity || "Morning excursion"}
                      </p>
                      {day.morning?.location && (
                        <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                          <MapPin className="w-3.5 h-3.5 text-amber-600" />
                          <span>{day.morning.location}</span>
                        </div>
                      )}
                      {day.morning?.practical_tip && (
                        <p className="text-[11px] text-amber-900/80 dark:text-amber-300/80 italic pt-1 border-t border-amber-200/40 dark:border-amber-900/30">
                          💡 {day.morning.practical_tip}
                        </p>
                      )}
                    </div>

                    {/* Afternoon */}
                    <div className="p-4 rounded-xl bg-sky-50/60 dark:bg-sky-950/20 border border-sky-200/60 dark:border-sky-900/40 space-y-2.5">
                      <div className="flex items-center gap-2 text-sky-700 dark:text-sky-400 font-bold text-xs uppercase tracking-wider">
                        <Sunset className="w-4 h-4" />
                        <span>Afternoon • {day.afternoon?.time || "13:30 - 17:30"}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 font-medium leading-snug">
                        {day.afternoon?.activity || "Afternoon exploration"}
                      </p>
                      {day.afternoon?.location && (
                        <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                          <MapPin className="w-3.5 h-3.5 text-sky-600" />
                          <span>{day.afternoon.location}</span>
                        </div>
                      )}
                      {day.afternoon?.practical_tip && (
                        <p className="text-[11px] text-sky-900/80 dark:text-sky-300/80 italic pt-1 border-t border-sky-200/40 dark:border-sky-900/30">
                          💡 {day.afternoon.practical_tip}
                        </p>
                      )}
                    </div>

                    {/* Evening */}
                    <div className="p-4 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200/60 dark:border-indigo-900/40 space-y-2.5">
                      <div className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400 font-bold text-xs uppercase tracking-wider">
                        <Moon className="w-4 h-4" />
                        <span>Evening • {day.evening?.time || "18:30 - 21:30"}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 font-medium leading-snug">
                        {day.evening?.activity || "Evening dining & night exploration"}
                      </p>
                      {day.evening?.location && (
                        <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                          <MapPin className="w-3.5 h-3.5 text-indigo-600" />
                          <span>{day.evening.location}</span>
                        </div>
                      )}
                      {day.evening?.practical_tip && (
                        <p className="text-[11px] text-indigo-900/80 dark:text-indigo-300/80 italic pt-1 border-t border-indigo-200/40 dark:border-indigo-900/30">
                          💡 {day.evening.practical_tip}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Highlights and transport footer */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 text-xs border-t border-slate-200/60 dark:border-slate-800/60">
                    {day.transport_notes && (
                      <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                        <Bus className="w-3.5 h-3.5 text-voyage-500" />
                        <span>{day.transport_notes}</span>
                      </div>
                    )}

                    {day.food_suggestions && day.food_suggestions.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-slate-500">Dining Picks:</span>
                        {day.food_suggestions.map((food, fidx) => (
                          <span
                            key={fidx}
                            className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-[11px]"
                          >
                            {food}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
