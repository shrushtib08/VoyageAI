import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import {
  Sparkles,
  Compass,
  Sliders,
  Send,
  Loader2,
  Calendar,
  Users,
  Coins,
  MapPin,
  Utensils,
  Camera,
  Heart,
  HelpCircle,
  ArrowRight,
} from "lucide-react";

interface PlannerPageProps {
  onNavigate: (page: string) => void;
  onTripCreated: (tripId: number) => void;
  initialPrompt?: string;
}

const INTERESTS_OPTIONS = [
  "Culture & Temples",
  "Food & Street Cuisine",
  "Photography",
  "Nature & Hiking",
  "Historic Landmarks",
  "Shopping & Markets",
  "Relaxation & Spas",
  "Adventure & Sports",
  "Nightlife & Lounges",
];

const DIETARY_OPTIONS = [
  "Vegetarian",
  "Vegan",
  "Halal",
  "Gluten-Free",
  "No Restrictions",
];

const TRAVEL_STYLES = [
  { id: "balanced", label: "Balanced", desc: "Best mix of sightseeing and downtime" },
  { id: "relaxed", label: "Relaxed", desc: "Leisurely pace with open afternoons" },
  { id: "adventure", label: "Adventure", desc: "Action-packed & active exploration" },
  { id: "budget", label: "Budget Backpacker", desc: "Maximum sights, minimal spend" },
  { id: "luxury", label: "Luxury Comfort", desc: "Premium stays and fine dining" },
];

export const PlannerPage: React.FC<PlannerPageProps> = ({
  onNavigate,
  onTripCreated,
  initialPrompt,
}) => {
  const { user } = useAuth();
  const [mode, setMode] = useState<"prompt" | "builder">("prompt");
  const [prompt, setPrompt] = useState(initialPrompt || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Structured form state
  const [origin, setOrigin] = useState("Bangalore");
  const [destination, setDestination] = useState("Japan");
  const [durationDays, setDurationDays] = useState(7);
  const [travellers, setTravellers] = useState(2);
  const [budget, setBudget] = useState<number>(150000);
  const [currency, setCurrency] = useState("INR");
  const [travelStyle, setTravelStyle] = useState("balanced");
  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    "Culture & Temples",
    "Food & Street Cuisine",
    "Photography",
    "Nature & Hiking",
  ]);
  const [selectedDietary, setSelectedDietary] = useState<string[]>(["Vegetarian"]);
  const [accommodationPref, setAccommodationPref] = useState("Boutique / 3-4 star");
  const [specialConstraints, setSpecialConstraints] = useState("Keep under ₹1.5 lakh, avoid excessive daily transit");

  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt);
      setMode("prompt");
    }
  }, [initialPrompt]);

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  };

  const toggleDietary = (diet: string) => {
    setSelectedDietary((prev) =>
      prev.includes(diet) ? prev.filter((d) => d !== diet) : [...prev, diet]
    );
  };

  const handleGeneratePromptFromForm = () => {
    const formatted =
      `Plan a ${durationDays}-day trip to ${destination} from ${origin} for ${travellers} people ` +
      `with a budget of ${currency} ${budget.toLocaleString()}. ` +
      `Travel style is ${travelStyle}. ` +
      `Interests: ${selectedInterests.join(", ")}. ` +
      `Dietary requirements: ${selectedDietary.join(", ")}. ` +
      `Lodging: ${accommodationPref}. ` +
      (specialConstraints ? `Constraints: ${specialConstraints}.` : "");
    setPrompt(formatted);
    setMode("prompt");
  };

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;

    if (!user) {
      alert("Please sign in or register to orchestrate trips.");
      onNavigate("login");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const created = await api.trips.createFromPrompt(prompt.trim());
      onTripCreated(created.id);
      onNavigate("progress");
    } catch (err: any) {
      setError(err.message || "Failed to launch planning task.");
    } finally {
      setLoading(false);
    }
  };

  const handleStructuredSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination.trim() || loading) return;

    if (!user) {
      alert("Please sign in or register to orchestrate trips.");
      onNavigate("login");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const created = await api.trips.createStructured({
        origin: origin.trim() || undefined,
        destination: destination.trim(),
        duration_days: Number(durationDays),
        travellers: Number(travellers),
        budget: budget ? Number(budget) : undefined,
        currency,
        travel_style: travelStyle,
        interests: selectedInterests,
        dietary_preferences: selectedDietary,
        accommodation_preferences: accommodationPref,
        special_constraints: specialConstraints.trim() || undefined,
      });
      onTripCreated(created.id);
      onNavigate("progress");
    } catch (err: any) {
      setError(err.message || "Failed to launch planning task.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-voyage-50 dark:bg-voyage-950 text-voyage-700 dark:text-voyage-300 text-xs font-bold border border-voyage-200 dark:border-voyage-800">
          <Sparkles className="w-3.5 h-3.5 text-voyage-500" />
          <span>Multi-Agent AI Trip Builder</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
          Where would you like to travel?
        </h2>
        <p className="text-sm text-slate-500 max-w-lg mx-auto">
          Describe your vision in natural language, or use our structured builder to fine-tune every parameter.
        </p>
      </div>

      {/* Mode Switch Tabs */}
      <div className="flex items-center justify-center">
        <div className="p-1 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 flex items-center gap-1">
          <button
            onClick={() => setMode("prompt")}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
              mode === "prompt"
                ? "bg-voyage-600 text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Natural Language</span>
          </button>
          <button
            onClick={() => setMode("builder")}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
              mode === "builder"
                ? "bg-voyage-600 text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Structured Builder</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* TAB 1: NATURAL LANGUAGE PROMPT */}
      {mode === "prompt" ? (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 space-y-6 shadow-xl">
          <form onSubmit={handlePromptSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
                Describe Your Trip In Freeform Plain English
              </label>
              <textarea
                rows={5}
                required
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Example: Plan a 7-day trip to Japan from Bangalore for two people in December. My budget is ₹1,50,000. I like food, culture, photography and nature..."
                className="w-full p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-voyage-500 leading-relaxed resize-none"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
              <span className="text-xs text-slate-500">
                The Travel Manager will extract 12+ parameters and dispatch 6 specialized research agents.
              </span>

              <button
                type="submit"
                disabled={!prompt.trim() || loading}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-voyage-600 hover:bg-voyage-700 text-white font-bold text-sm shadow-md shadow-voyage-500/20 transition-all hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Deploying Agents...</span>
                  </>
                ) : (
                  <>
                    <span>Orchestrate Trip</span>
                    <Send className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Quick Prompts */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
              Quick Suggestions (Click to load):
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                "Plan a 7-day trip to Japan from Bangalore for two people in December. My budget is ₹1,50,000. I like food, culture, photography and nature.",
                "Plan a 10-day trip covering Paris, Rome and Florence for a couple with a balanced budget and historic walking tours.",
                "Plan a 4-day trip to Kyoto from Tokyo for 2 people with a ₹80,000 budget. I love photography, temples, and ramen.",
              ].map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(example)}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs transition-colors text-left"
                >
                  💡 {example.slice(0, 58)}...
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* TAB 2: STRUCTURED BUILDER */
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 space-y-6 shadow-xl">
          <form onSubmit={handleStructuredSubmit} className="space-y-6">
            {/* Origin & Destination */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Origin City / Airport
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    placeholder="e.g. Bangalore or New York"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Destination (or Multi-City: Paris, Rome, Florence)
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-voyage-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="e.g. Japan or Paris, Rome and Florence"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                  />
                </div>
              </div>
            </div>

            {/* Duration, Travellers, Budget, Currency */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Duration (Days)
                </label>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={durationDays}
                  onChange={(e) => setDurationDays(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Travelers
                </label>
                <input
                  type="number"
                  min={1}
                  max={12}
                  value={travellers}
                  onChange={(e) => setTravellers(Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Target Budget
                </label>
                <input
                  type="number"
                  step="1000"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  placeholder="e.g. 150000"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                  Currency
                </label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
                >
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="JPY">JPY (¥)</option>
                </select>
              </div>
            </div>

            {/* Travel Style */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                Travel Style & Pace
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {TRAVEL_STYLES.map((style) => (
                  <button
                    key={style.id}
                    type="button"
                    onClick={() => setTravelStyle(style.id)}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      travelStyle === style.id
                        ? "border-voyage-600 bg-voyage-50/50 dark:bg-voyage-950/40 text-slate-900 dark:text-white shadow-sm"
                        : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    <span className="font-bold text-xs block mb-0.5">{style.label}</span>
                    <span className="text-[10px] text-slate-500 leading-tight block">{style.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Interests Chips */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                Core Passions & Traveler Interests
              </label>
              <div className="flex flex-wrap gap-2">
                {INTERESTS_OPTIONS.map((interest) => (
                  <button
                    key={interest}
                    type="button"
                    onClick={() => toggleInterest(interest)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      selectedInterests.includes(interest)
                        ? "bg-voyage-600 text-white shadow-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
            </div>

            {/* Dietary Preferences Chips */}
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                Dietary Requirements
              </label>
              <div className="flex flex-wrap gap-2">
                {DIETARY_OPTIONS.map((diet) => (
                  <button
                    key={diet}
                    type="button"
                    onClick={() => toggleDietary(diet)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      selectedDietary.includes(diet)
                        ? "bg-emerald-600 text-white shadow-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                    }`}
                  >
                    {diet}
                  </button>
                ))}
              </div>
            </div>

            {/* Accommodation Preference */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                Accommodation Preference
              </label>
              <select
                value={accommodationPref}
                onChange={(e) => setAccommodationPref(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
              >
                <option value="Boutique / 3-4 star">Boutique / 3-4 Star</option>
                <option value="Hostel / Budget Inn">Hostel / Budget Inn</option>
                <option value="Luxury 5-Star Resort">Luxury 5-Star Resort</option>
                <option value="Traditional Heritage / Ryokan / Villa">Traditional Heritage / Ryokan / Villa</option>
              </select>
            </div>

            {/* Special Constraints */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                Smart Constraints (e.g. "Max 3h travel", "No luxury hotels", "Prioritize photography")
              </label>
              <input
                type="text"
                value={specialConstraints}
                onChange={(e) => setSpecialConstraints(e.target.value)}
                placeholder="e.g. Keep under budget, focus on cultural landmarks"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-voyage-500"
              />
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                onClick={handleGeneratePromptFromForm}
                className="text-xs text-voyage-600 dark:text-voyage-400 font-bold hover:underline flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Auto-Generate Natural Prompt from Form</span>
              </button>

              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-voyage-600 hover:bg-voyage-700 text-white font-bold text-sm shadow-md shadow-voyage-500/20 transition-all hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Deploying Agents...</span>
                  </>
                ) : (
                  <>
                    <span>Orchestrate Trip</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
