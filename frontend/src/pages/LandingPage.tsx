import React from "react";
import {
  Compass,
  ArrowRight,
  Sparkles,
  Bot,
  Plane,
  ShieldCheck,
  Zap,
  Globe,
  Coins,
  CheckCircle2,
  Calendar,
  Users,
} from "lucide-react";

interface LandingPageProps {
  onNavigate: (page: string) => void;
  onSetPrompt?: (prompt: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, onSetPrompt }) => {
  const examplePrompts = [
    "Plan a 7-day trip to Japan from Bangalore for two people in December. My budget is ₹1,50,000. I like food, culture, photography and nature.",
    "Plan a 10-day trip covering Paris, Rome and Florence for a couple with a balanced budget and historic walking tours.",
    "Plan a 5-day adventure in Bali for 3 friends under ₹75,000 each with vegetarian food, waterfalls, and surf spots.",
  ];

  const handlePromptClick = (p: string) => {
    if (onSetPrompt) onSetPrompt(p);
    onNavigate("planner");
  };

  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-voyage-500/15 via-teal-500/10 to-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 text-center space-y-8 relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel border border-voyage-200 dark:border-voyage-800 text-xs font-semibold text-voyage-700 dark:text-voyage-300 shadow-sm animate-bounce-short">
            <Sparkles className="w-3.5 h-3.5 text-voyage-500" />
            <span>Original Multi-Agent Architecture • Real Concurrency Orchestration</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-slate-900 dark:text-white leading-[1.1]">
            Meet <span className="gradient-text">VoyageAI</span>.<br />
            Your Intelligent Team of AI Travel Agents.
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-xl text-slate-600 dark:text-slate-300 leading-relaxed font-normal">
            Describe your dream journey naturally. A coordinated team of 10 specialized AI agents researches flights, stays, regional food, and weather, synthesizing an audited day-by-day plan with smart budget optimization.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onNavigate("planner")}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-voyage-600 to-indigo-600 hover:from-voyage-700 hover:to-indigo-700 text-white font-bold text-base shadow-lg shadow-voyage-500/25 transition-all hover:scale-[1.02] flex items-center justify-center gap-2"
            >
              <span>Plan My Trip</span>
              <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => onNavigate("dashboard")}
              className="w-full sm:w-auto px-6 py-4 rounded-xl glass-panel border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold text-slate-800 dark:text-slate-200 text-base transition-colors"
            >
              View Saved Trips
            </button>
          </div>

          {/* Interactive Prompts Pills */}
          <div className="pt-8 space-y-3">
            <span className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Or click an example to start immediately:
            </span>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-2 max-w-4xl mx-auto">
              {examplePrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePromptClick(prompt)}
                  className="w-full sm:w-auto text-left px-3.5 py-2 rounded-xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-voyage-400 dark:hover:border-voyage-500 text-xs text-slate-700 dark:text-slate-300 transition-all hover:scale-[1.01] line-clamp-1"
                >
                  💡 "{prompt.slice(0, 52)}..."
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Flow Explanation */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-3 mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">
            System Architecture
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            How the Multi-Agent Pipeline Works
          </h2>
          <p className="text-sm text-slate-500 max-w-xl mx-auto">
            Not a single monolithic prompt. Specialized agents run concurrently, cross-validating requirements and enforcing geographical proximity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
          <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-sm">
              1
            </div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white">Travel Manager</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Parses intent, resolves multi-city routing, extracts budget caps, and delegates specialized research tasks.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-voyage-200 dark:border-voyage-900 bg-voyage-50/20 dark:bg-voyage-950/20 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-sky-100 dark:bg-sky-950 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold text-sm">
              2
            </div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white">6 Parallel Agents</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Flight, Hotel, Destination, Weather, Food, and Activities execute concurrently with real APIs and fallbacks.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-yellow-100 dark:bg-yellow-950 text-yellow-600 dark:text-yellow-400 flex items-center justify-center font-bold text-sm">
              3
            </div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white">Budget Strategist</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Computes 7 category allocations, per-person costs, and injects a 7% emergency contingency buffer.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-sm">
              4
            </div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white">Itinerary Architect</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Clusters sites geographically into Morning, Afternoon, and Evening blocks with realistic commute buffers.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-panel border border-emerald-200 dark:border-emerald-900 bg-emerald-50/20 dark:bg-emerald-950/20 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-sm">
              5
            </div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white">Critic QA Validation</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Audits travel pacing, duplicate sights, and meal pauses. Triggers automatic revision if conflicts arise.
            </p>
          </div>
        </div>
      </section>

      {/* Agent Roster Showcase */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-3 mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">
            Meet the Agents
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            10 Dedicated Specialists for Every Journey
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[
            { title: "Travel Manager Agent", desc: "Central coordinator parsing natural prompts, dates, and strict user constraints.", icon: "🧭", tag: "Coordinator" },
            { title: "Flight Agent", desc: "Analyzes airport corridors, carriers, fare ranges, and live AviationStack feeds.", icon: "✈️", tag: "Transit" },
            { title: "Hotel Agent", desc: "Researches verified accommodations matching style, amenities, and metro access.", icon: "🏨", tag: "Lodging" },
            { title: "Destination Agent", desc: "Maps UNESCO sites, hidden gems, and districts via Tavily AI web citations.", icon: "📍", tag: "Research" },
            { title: "Weather Agent", desc: "Monitors OpenWeather conditions, seasonal temperatures, and packing advice.", icon: "🌤️", tag: "Climate" },
            { title: "Food Agent", desc: "Curates regional gastronomy, food alleys, and certified vegetarian/vegan venues.", icon: "🍜", tag: "Gastronomy" },
            { title: "Activity Agent", desc: "Ranks personalized workshops, nature excursions, and scenic viewpoints.", icon: "📸", tag: "Experiences" },
            { title: "Budget Agent", desc: "Calculates subtotal, per-person rates, currency conversion, and contingency reserves.", icon: "💰", tag: "Financial" },
            { title: "Itinerary Agent", desc: "Synthesizes cohesive day-by-day blocks with geographic clustering.", icon: "📅", tag: "Synthesis" },
            { title: "Critic QA Agent", desc: "Performs adversarial schedule inspection to eliminate rush and impossible timetables.", icon: "🛡️", tag: "Quality Assurance" },
          ].map((agent, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-voyage-400/50 transition-all space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl">{agent.icon}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                  {agent.tag}
                </span>
              </div>
              <h4 className="font-bold text-base text-slate-900 dark:text-white">{agent.title}</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{agent.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-tr from-voyage-900 via-slate-900 to-indigo-950 text-white text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="space-y-3 relative z-10">
            <h3 className="text-3xl sm:text-4xl font-black">
              Ready to Experience Multi-Agent Travel Planning?
            </h3>
            <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto">
              Plan custom itineraries with live agent feedback, audited schedules, and memory-backed follow-up conversations.
            </p>
          </div>
          <button
            onClick={() => onNavigate("planner")}
            className="px-8 py-4 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-extrabold text-sm shadow-md transition-all hover:scale-105 inline-flex items-center gap-2 relative z-10"
          >
            <span>Start Your Free Trip Plan</span>
            <ArrowRight className="w-4 h-4 text-voyage-600" />
          </button>
        </div>
      </section>
    </div>
  );
};
