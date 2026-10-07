import React, { useState, useEffect } from "react";
import { TripListItem } from "../types";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import {
  PlusCircle,
  Search,
  Calendar,
  Users,
  Coins,
  MapPin,
  ArrowRight,
  Trash2,
  Clock,
  Sparkles,
  Loader2,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

interface DashboardPageProps {
  onNavigate: (page: string) => void;
  onSelectTrip: (tripId: number) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate, onSelectTrip }) => {
  const { user } = useAuth();
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    loadTrips();
  }, [search]);

  const loadTrips = async () => {
    setLoading(true);
    try {
      const data = await api.trips.list(search.trim() || undefined);
      setTrips(data);
    } catch (err) {
      console.error("Failed to load trips", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, tripId: number) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this trip plan?")) return;

    setDeletingId(tripId);
    try {
      await api.trips.deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
    } catch (err) {
      console.error("Failed to delete trip", err);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Banner / Header */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-sm">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>VoyageAI Command Center</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
            Welcome back, {user?.full_name || user?.username || "Traveler"}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-xl">
            Manage your AI-curated journeys, reopen saved itineraries, or launch a new multi-agent planning task.
          </p>
        </div>

        <button
          onClick={() => onNavigate("planner")}
          className="px-6 py-3.5 rounded-xl bg-voyage-600 hover:bg-voyage-700 text-white font-bold text-sm shadow-md shadow-voyage-500/20 transition-all hover:scale-[1.02] flex items-center gap-2 self-start md:self-auto shrink-0"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Plan New Trip</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by destination, origin, or title..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
          />
        </div>

        <span className="text-xs text-slate-500 font-medium self-end sm:self-center">
          Showing {trips.length} trip plan{trips.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Trip Cards Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-voyage-600" />
          <p className="text-xs font-semibold">Loading your itineraries...</p>
        </div>
      ) : trips.length === 0 ? (
        <div className="p-12 text-center rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
            <MapPin className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            {search ? "No matching trips found" : "No trip plans yet"}
          </h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {search
              ? "Try adjusting your search query to find your saved trip plans."
              : "Launch your first multi-agent travel planning task to get an audited day-by-day itinerary."}
          </p>
          <button
            onClick={() => onNavigate("planner")}
            className="px-5 py-2.5 rounded-xl bg-voyage-600 hover:bg-voyage-700 text-white font-semibold text-xs shadow-sm transition-colors"
          >
            Create Your First Trip
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => {
            let statusBadge = (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Ready
              </span>
            );

            if (trip.status === "planning") {
              statusBadge = (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-voyage-50 text-voyage-700 dark:bg-voyage-950 dark:text-voyage-300 border border-voyage-200 animate-pulse">
                  <Loader2 className="w-3 h-3 animate-spin" /> Planning
                </span>
              );
            } else if (trip.status === "failed") {
              statusBadge = (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border border-amber-200">
                  <AlertTriangle className="w-3 h-3" /> Retry Needed
                </span>
              );
            }

            return (
              <div
                key={trip.id}
                onClick={() => {
                  onSelectTrip(trip.id);
                  if (trip.status === "planning") onNavigate("progress");
                  else onNavigate("trip-detail");
                }}
                className="group p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-voyage-400/60 dark:hover:border-voyage-500/50 hover:shadow-lg transition-all duration-200 cursor-pointer flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-voyage-500" />
                      {trip.destination}
                    </span>
                    {statusBadge}
                  </div>

                  <h3 className="font-bold text-base sm:text-lg text-slate-900 dark:text-white group-hover:text-voyage-600 dark:group-hover:text-voyage-400 transition-colors line-clamp-1">
                    {trip.title}
                  </h3>

                  {trip.summary && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                      {trip.summary}
                    </p>
                  )}

                  {/* Metadata chips */}
                  <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-slate-600 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {trip.duration_days} Days
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      {trip.travellers} {trip.travellers === 1 ? "Traveler" : "Travelers"}
                    </span>
                    {trip.budget && (
                      <span className="flex items-center gap-1 font-semibold text-slate-800 dark:text-slate-200">
                        <Coins className="w-3.5 h-3.5 text-amber-500" />
                        {trip.currency} {trip.budget.toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Action Footer */}
                <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-[11px] text-slate-400">
                    Created {new Date(trip.created_at).toLocaleDateString()}
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => handleDelete(e, trip.id)}
                      disabled={deletingId === trip.id}
                      className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                      title="Delete trip"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <span className="font-bold text-voyage-600 dark:text-voyage-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
                      <span>Open Plan</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
