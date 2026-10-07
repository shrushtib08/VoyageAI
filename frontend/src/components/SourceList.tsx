import React from "react";
import { ResearchSource } from "../types";
import { ExternalLink, ShieldCheck, Database, Search } from "lucide-react";

interface SourceListProps {
  sources: ResearchSource[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="p-1.5 rounded-lg bg-teal-100 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400">
            <Search className="w-4 h-4" />
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Audit Trail & Research Citations
          </span>
        </div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
          Verified Information Sources & Data Attribution
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          In VoyageAI, every recommendation is traced back to an agent and authoritative research repository.
          Below is the complete citation manifest for this generated itinerary.
        </p>
      </div>

      {/* Sources Grid */}
      <div className="space-y-3">
        {sources && sources.length > 0 ? (
          sources.map((source, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-bold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                    {source.agent_name}
                  </span>
                  <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                    {source.title}
                  </h4>
                </div>
                {source.snippet && (
                  <p className="text-slate-600 dark:text-slate-300 line-clamp-2">
                    {source.snippet}
                  </p>
                )}
              </div>

              {source.url && (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-voyage-50 hover:bg-voyage-100 dark:bg-voyage-950/60 dark:hover:bg-voyage-900 text-voyage-700 dark:text-voyage-300 font-semibold shrink-0 transition-colors self-start sm:self-center"
                >
                  <span>Visit Source</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-400 italic">No external citations registered for this trip.</p>
        )}
      </div>
    </div>
  );
};
