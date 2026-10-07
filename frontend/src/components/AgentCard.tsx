import React from "react";
import {
  Compass,
  Plane,
  Hotel,
  MapPin,
  CloudSun,
  Utensils,
  Camera,
  Coins,
  CalendarDays,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Loader2,
  AlertTriangle,
} from "lucide-react";

interface AgentCardProps {
  name: string;
  roleTitle: string;
  status: "pending" | "running" | "completed" | "failed";
  message?: string;
}

const AGENT_ICONS: Record<string, React.ReactNode> = {
  TravelManagerAgent: <Compass className="w-5 h-5 text-indigo-500" />,
  FlightAgent: <Plane className="w-5 h-5 text-sky-500" />,
  HotelAgent: <Hotel className="w-5 h-5 text-amber-500" />,
  DestinationAgent: <MapPin className="w-5 h-5 text-emerald-500" />,
  WeatherAgent: <CloudSun className="w-5 h-5 text-orange-500" />,
  FoodAgent: <Utensils className="w-5 h-5 text-rose-500" />,
  ActivityAgent: <Camera className="w-5 h-5 text-purple-500" />,
  BudgetAgent: <Coins className="w-5 h-5 text-yellow-500" />,
  ItineraryAgent: <CalendarDays className="w-5 h-5 text-blue-500" />,
  CriticAgent: <ShieldCheck className="w-5 h-5 text-teal-500" />,
};

const AGENT_LABELS: Record<string, { title: string; subtitle: string }> = {
  TravelManagerAgent: { title: "Travel Manager", subtitle: "Extracts criteria & delegates tasks" },
  FlightAgent: { title: "Flight Agent", subtitle: "Identifies routes & fare corridors" },
  HotelAgent: { title: "Hotel Agent", subtitle: "Curates verified accommodation" },
  DestinationAgent: { title: "Destination Agent", subtitle: "Catalogs monuments & districts" },
  WeatherAgent: { title: "Weather Agent", subtitle: "Analyzes climate & packing advice" },
  FoodAgent: { title: "Food Agent", subtitle: "Researches local cuisine & dietary spots" },
  ActivityAgent: { title: "Activity Agent", subtitle: "Ranks personalized experiences" },
  BudgetAgent: { title: "Budget Agent", subtitle: "Computes financial allocation & buffer" },
  ItineraryAgent: { title: "Itinerary Agent", subtitle: "Synthesizes day-by-day timetable" },
  CriticAgent: { title: "Critic Agent", subtitle: "Validates schedule & prevents clashes" },
};

export const AgentCard: React.FC<AgentCardProps> = ({ name, roleTitle, status, message }) => {
  const meta = AGENT_LABELS[name] || { title: name, subtitle: roleTitle };
  const icon = AGENT_ICONS[name] || <Compass className="w-5 h-5 text-slate-500" />;

  let badgeColor = "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700";
  let statusIcon = <Clock className="w-3.5 h-3.5" />;
  let cardBorder = "border-slate-200 dark:border-slate-800";

  if (status === "running") {
    badgeColor = "bg-voyage-100 text-voyage-700 dark:bg-voyage-950/80 dark:text-voyage-300 border-voyage-300 dark:border-voyage-800 animate-pulse";
    statusIcon = <Loader2 className="w-3.5 h-3.5 animate-spin" />;
    cardBorder = "border-voyage-400 dark:border-voyage-500 shadow-sm shadow-voyage-500/10";
  } else if (status === "completed") {
    badgeColor = "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800";
    statusIcon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />;
    cardBorder = "border-emerald-200/80 dark:border-emerald-900/60";
  } else if (status === "failed") {
    badgeColor = "bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800";
    statusIcon = <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />;
    cardBorder = "border-amber-200 dark:border-amber-800";
  }

  return (
    <div className={`p-4 rounded-xl glass-panel border ${cardBorder} transition-all duration-200 flex flex-col justify-between`}>
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/80">
              {icon}
            </div>
            <div>
              <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">
                {meta.title}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1">
                {meta.subtitle}
              </p>
            </div>
          </div>

          <span
            className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeColor}`}
          >
            {statusIcon}
            <span className="capitalize">{status}</span>
          </span>
        </div>
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/60 text-xs">
        <p className="text-slate-600 dark:text-slate-300 italic line-clamp-2">
          {message || (status === "completed" ? "Research verified." : "Queued in orchestration pipeline.")}
        </p>
      </div>
    </div>
  );
};
