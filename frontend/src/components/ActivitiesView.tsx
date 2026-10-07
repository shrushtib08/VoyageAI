import React from "react";
import { ActivityResearch } from "../types";
import { Camera, Clock, Coins, Sun, Sparkles } from "lucide-react";

interface ActivitiesViewProps {
  activity: ActivityResearch;
  currency: string;
}

export const ActivitiesView: React.FC<ActivitiesViewProps> = ({ activity, currency }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="p-1.5 rounded-lg bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
            <Camera className="w-4 h-4" />
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Ranked Experiential Activities
          </span>
        </div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
          Curated Experiences & Adventures Tailored to Your Passions
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Ranked in order of relevance to your specified interests, travel pace, and photography vantage points.
        </p>
      </div>

      {/* Ranked List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {activity.ranked_activities.map((act) => (
          <div
            key={act.rank}
            className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-purple-100 dark:bg-purple-950/80 text-purple-700 dark:text-purple-300 text-xs font-black flex items-center justify-center shrink-0">
                    #{act.rank}
                  </div>
                  <h4 className="font-bold text-base text-slate-900 dark:text-white">
                    {act.title}
                  </h4>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 uppercase tracking-wider shrink-0">
                  {act.category}
                </span>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {act.description}
              </p>
            </div>

            {/* Metrics Footer */}
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  {act.estimated_duration_hours}h
                </span>
                {act.best_time_of_day && (
                  <span className="flex items-center gap-1">
                    <Sun className="w-3.5 h-3.5 text-amber-500" />
                    {act.best_time_of_day}
                  </span>
                )}
              </div>

              <span className="font-extrabold text-sm text-slate-900 dark:text-white">
                {currency} {act.estimated_cost?.toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
