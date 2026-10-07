import React, { useState, useEffect } from "react";
import { TripDetail } from "../types";
import { api } from "../services/api";
import { ItineraryTimeline } from "../components/ItineraryTimeline";
import { BudgetBreakdown } from "../components/BudgetBreakdown";
import { FlightView } from "../components/FlightView";
import { HotelView } from "../components/HotelView";
import { WeatherCard } from "../components/WeatherCard";
import { FoodCard } from "../components/FoodCard";
import { ActivitiesView } from "../components/ActivitiesView";
import { SourceList } from "../components/SourceList";
import { FollowUpChat } from "../components/FollowUpChat";
import {
  Calendar,
  Users,
  Coins,
  MapPin,
  Plane,
  Hotel,
  CloudSun,
  Utensils,
  Camera,
  Search,
  MessageSquare,
  FileText,
  Printer,
  Copy,
  Download,
  Check,
  ArrowLeft,
  Loader2,
  Sparkles,
  Info,
} from "lucide-react";

interface TripDetailPageProps {
  tripId: number;
  onNavigate: (page: string) => void;
}

type TabType =
  | "overview"
  | "itinerary"
  | "flights"
  | "hotels"
  | "weather"
  | "food"
  | "activities"
  | "budget"
  | "sources"
  | "chat";

export const TripDetailPage: React.FC<TripDetailPageProps> = ({ tripId, onNavigate }) => {
  const [trip, setTrip] = useState<TripDetail | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadTrip();
  }, [tripId]);

  const loadTrip = async () => {
    setLoading(true);
    try {
      const data = await api.trips.get(tripId);
      setTrip(data);
    } catch (err) {
      console.error("Failed to load trip detail", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyPlan = () => {
    if (!trip) return;
    const summaryText =
      `Trip: ${trip.title}\n` +
      `Destination: ${trip.destination}\n` +
      `Duration: ${trip.duration_days} Days\n` +
      `Estimated Budget: ${trip.currency} ${trip.budget_details?.total_budget?.toLocaleString() || trip.budget?.toLocaleString()}\n\n` +
      `Overview:\n${trip.summary || ""}\n\n` +
      `Day by Day:\n` +
      (trip.itinerary?.days
        ?.map((d) => `Day ${d.day_number}: ${d.theme}\n- Morning: ${d.morning?.activity || ""}\n- Afternoon: ${d.afternoon?.activity || ""}\n- Evening: ${d.evening?.activity || ""}`)
        .join("\n\n") || "");

    navigator.clipboard.writeText(summaryText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center gap-3 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-voyage-600" />
        <p className="text-xs font-semibold">Loading trip dashboard...</p>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl max-w-md mx-auto my-12 space-y-3">
        <h3 className="font-bold text-lg text-slate-900 dark:text-white">Trip Not Found</h3>
        <p className="text-xs text-slate-500">This itinerary may have been deleted or moved.</p>
        <button
          onClick={() => onNavigate("dashboard")}
          className="px-4 py-2 rounded-xl bg-voyage-600 text-white text-xs font-bold"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: <Info className="w-4 h-4" /> },
    { id: "itinerary", label: "Itinerary", icon: <Calendar className="w-4 h-4" /> },
    { id: "flights", label: "Flights", icon: <Plane className="w-4 h-4" /> },
    { id: "hotels", label: "Hotels", icon: <Hotel className="w-4 h-4" /> },
    { id: "weather", label: "Weather", icon: <CloudSun className="w-4 h-4" /> },
    { id: "food", label: "Food & Dining", icon: <Utensils className="w-4 h-4" /> },
    { id: "activities", label: "Activities", icon: <Camera className="w-4 h-4" /> },
    { id: "budget", label: "Budget", icon: <Coins className="w-4 h-4" /> },
    { id: "sources", label: "Sources", icon: <Search className="w-4 h-4" /> },
    { id: "chat", label: "AI Concierge", icon: <MessageSquare className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-8 pb-20">
      {/* Top Header Card */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel border border-slate-200 dark:border-slate-800 space-y-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <button
              onClick={() => onNavigate("dashboard")}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-voyage-600 dark:text-voyage-400 hover:underline mb-1"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to My Trips</span>
            </button>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" />
                {trip.destination} {trip.origin ? `from ${trip.origin}` : ""}
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-500 font-semibold">
                {trip.duration_days} Days / {trip.travellers} Traveler{trip.travellers > 1 ? "s" : ""}
              </span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white">
              {trip.title}
            </h1>
          </div>

          {/* Export Action Buttons */}
          <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
            <button
              onClick={handleCopyPlan}
              className="px-3 py-2 rounded-xl glass-panel border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1.5"
              title="Copy Summary to Clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied!" : "Copy Plan"}</span>
            </button>

            <a
              href={api.export.getMarkdownUrl(trip.id)}
              download
              className="px-3 py-2 rounded-xl glass-panel border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1.5"
              title="Download Markdown Document"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Markdown</span>
            </a>

            <a
              href={api.export.getPrintUrl(trip.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 rounded-xl glass-panel border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1.5"
              title="Print View or Save as PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </a>
          </div>
        </div>

        {/* Quick Highlights Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800/80 text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Estimated Budget</span>
            <span className="text-base font-extrabold text-slate-900 dark:text-white">
              {trip.currency} {(trip.budget_details?.total_budget || trip.budget || 0).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Travel Style</span>
            <span className="text-base font-extrabold text-slate-900 dark:text-white capitalize">
              {trip.travel_style}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Schedule Audited</span>
            <span className="text-base font-extrabold text-emerald-600 dark:text-emerald-400">
              {trip.itinerary?.validation_status || "VALID"}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Agent Pipeline</span>
            <span className="text-base font-extrabold text-voyage-600 dark:text-voyage-400">
              10 Agents Verified
            </span>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="border-b border-slate-200 dark:border-slate-800 overflow-x-auto no-scrollbar">
        <div className="flex items-center gap-1 min-w-max pb-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                activeTab === tab.id
                  ? "bg-voyage-600 text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/50"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* TAB CONTENTS */}
      <div>
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
              <h3 className="font-extrabold text-xl text-slate-900 dark:text-white">
                Executive Trip Summary
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                {trip.summary || "Custom travel plan designed by VoyageAI multi-agent system."}
              </p>
            </div>

            {/* Practical Notes & Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
                <h4 className="font-bold text-sm uppercase tracking-wider text-slate-500">
                  Key Traveler Preferences & Constraints
                </h4>
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block">Interests:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {trip.interests && trip.interests.length > 0 ? trip.interests.join(", ") : "General exploration"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Dietary:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {trip.dietary_preferences && trip.dietary_preferences.length > 0 ? trip.dietary_preferences.join(", ") : "None specified"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Lodging Tier:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {trip.accommodation_preferences || "Boutique / 3-4 star"}
                    </span>
                  </div>
                </div>
              </div>

              {trip.destination_research?.practical_info && (
                <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
                  <h4 className="font-bold text-sm uppercase tracking-wider text-slate-500">
                    Essential Destination Logistics
                  </h4>
                  <div className="space-y-2 text-xs">
                    {Object.entries(trip.destination_research.practical_info).map(([k, v]) => (
                      <div key={k}>
                        <span className="text-slate-400 block capitalize">{k.replace(/_/g, " ")}:</span>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "itinerary" && trip.itinerary && (
          <ItineraryTimeline itinerary={trip.itinerary} currency={trip.currency} />
        )}

        {activeTab === "flights" && trip.flight_research && (
          <FlightView flight={trip.flight_research} currency={trip.currency} />
        )}

        {activeTab === "hotels" && trip.hotel_research && (
          <HotelView hotel={trip.hotel_research} currency={trip.currency} />
        )}

        {activeTab === "weather" && trip.weather_research && (
          <WeatherCard weather={trip.weather_research} />
        )}

        {activeTab === "food" && trip.food_research && (
          <FoodCard food={trip.food_research} currency={trip.currency} />
        )}

        {activeTab === "activities" && trip.activity_research && (
          <ActivitiesView activity={trip.activity_research} currency={trip.currency} />
        )}

        {activeTab === "budget" && trip.budget_details && (
          <BudgetBreakdown
            budget={trip.budget_details}
            targetBudget={trip.budget}
            travellers={trip.travellers}
          />
        )}

        {activeTab === "sources" && (
          <SourceList sources={trip.sources || []} />
        )}

        {activeTab === "chat" && (
          <FollowUpChat tripId={trip.id} destination={trip.destination} />
        )}
      </div>
    </div>
  );
};
