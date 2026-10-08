import React, { useState, useEffect } from "react";
import { ProgressState, AgentStatusInfo } from "../types";
import { api } from "../services/api";
import { AgentCard } from "../components/AgentCard";
import confetti from "canvas-confetti";
import {
  Sparkles,
  ArrowRight,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Compass,
  Cpu,
} from "lucide-react";

interface ProgressPageProps {
  tripId: number;
  onNavigate: (page: string) => void;
  onSelectTrip: (tripId: number) => void;
}

const AGENT_ORDER = [
  "TravelManagerAgent",
  "FlightAgent",
  "HotelAgent",
  "DestinationAgent",
  "WeatherAgent",
  "FoodAgent",
  "ActivityAgent",
  "BudgetAgent",
  "ItineraryAgent",
  "CriticAgent",
];

export const ProgressPage: React.FC<ProgressPageProps> = ({
  tripId,
  onNavigate,
  onSelectTrip,
}) => {
  const [progress, setProgress] = useState<ProgressState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    let pollInterval: any;

    // Connect SSE Stream with fallback polling
    const streamUrl = `/api/trips/${tripId}/stream`;
    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(streamUrl);
      eventSource.onmessage = (event) => {
        try {
          const data: ProgressState = JSON.parse(event.data);
          if (isMounted) {
            setProgress(data);
            if (data.status === "completed") {
              confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
              eventSource?.close();
            }
          }
        } catch (e) {
          console.error("SSE parse error", e);
        }
      };

      eventSource.onerror = () => {
        // SSE failed or closed, fallback to polling
        eventSource?.close();
      };
    } catch {
      // SSE unsupported, fallback to polling
    }

    // Polling fallback
    const pollStatus = async () => {
      try {
        const data = await api.trips.getProgress(tripId);
        if (isMounted) {
          setProgress(data);
          if (data.status === "completed") {
            confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
            clearInterval(pollInterval);
          } else if (data.status === "failed") {
            clearInterval(pollInterval);
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message);
      }
    };

    pollStatus();
    pollInterval = setInterval(pollStatus, 1500);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
      if (eventSource) eventSource.close();
    };
  }, [tripId]);

  const percentage = progress?.progress_percentage || 15;
  const isFinished = progress?.status === "completed";
  const isFailed = progress?.status === "failed";

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Top Stage Announcement */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel border border-slate-200 dark:border-slate-800 space-y-5 shadow-lg relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">
              <Cpu className="w-4 h-4 animate-spin text-voyage-500" />
              <span>Multi-Agent Swarm In Progress</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              {isFinished
                ? "Your itinerary was generated and validated."
                : "Your Travel Manager is coordinating 7 research agents."}
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 max-w-xl">
              {progress?.message || "Synthesizing constraints, researching airlines, accommodations, and local sights..."}
            </p>
          </div>

          {/* Action button if finished */}
          {isFinished ? (
            <button
              onClick={() => {
                onSelectTrip(tripId);
                onNavigate("trip-detail");
              }}
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-sm shadow-lg shadow-emerald-500/25 transition-all hover:scale-105 flex items-center gap-2 self-start sm:self-auto shrink-0 animate-bounce-short"
            >
              <span>View Itinerary Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 self-start sm:self-auto bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-voyage-600" />
              <span>Live Concurrency Active</span>
            </div>
          )}
        </div>

        {/* Linear Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-600 dark:text-slate-400">
            <span>Overall Synthesis</span>
            <span>{percentage}%</span>
          </div>
          <div className="w-full h-3 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <div
              style={{ width: `${percentage}%` }}
              className="h-full bg-gradient-to-r from-voyage-600 via-sky-500 to-emerald-500 transition-all duration-500 ease-out"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Status query issue: {error}</span>
        </div>
      )}

      {/* 10 Agent Execution Cards Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
            Active Specialized Agents (10 Specialists)
          </h3>
          <span className="text-xs text-slate-400">
            Real-time backend execution trace
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {AGENT_ORDER.map((agentKey) => {
            const agentData: AgentStatusInfo = progress?.agents?.[agentKey] || {
              status: "pending",
              message: "Queued",
            };

            return (
              <AgentCard
                key={agentKey}
                name={agentKey}
                roleTitle="Specialized Agent"
                status={agentData.status}
                message={agentData.message}
              />
            );
          })}
        </div>
      </div>

      {/* Completion Banner */}
      {isFinished && (
        <div className="p-6 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-600 text-white shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-base text-emerald-900 dark:text-emerald-100">
                All Agents Finished Execution
              </h4>
              <p className="text-xs text-emerald-700 dark:text-emerald-300">
                Flight research, lodging, local food, weather, budget allocation, and critique validation are complete.
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              onSelectTrip(tripId);
              onNavigate("trip-detail");
            }}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all hover:scale-105 flex items-center justify-center gap-1.5"
          >
            <span>Open Complete Trip Plan</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};
