import React from "react";
import { Compass, Cpu, ShieldCheck, Globe, CloudSun, Plane, Sparkles } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-950 py-12 text-sm text-slate-500 dark:text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Col */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-voyage-600 to-teal-500 flex items-center justify-center text-white">
                <Compass className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-lg text-slate-900 dark:text-white">
                Voyage<span className="text-voyage-600 dark:text-voyage-400">AI</span>
              </span>
            </div>
            <p className="text-xs max-w-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              An original production-grade Multi-Agent AI Travel Planning system. Powered by specialized coordinators,
              deep regional research agents, financial optimizers, and automated critique validation.
            </p>
            <div className="flex items-center gap-3 pt-2 text-xs">
              <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" /> 10-Agent Verified
              </span>
              <span className="flex items-center gap-1 text-voyage-600 dark:text-voyage-400 font-medium">
                <Cpu className="w-3.5 h-3.5" /> Groq LLM Engine
              </span>
            </div>
          </div>

          {/* Architecture Agents */}
          <div>
            <h4 className="font-semibold text-slate-900 dark:text-slate-200 mb-3 text-xs uppercase tracking-wider">
              Specialized Agents
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li>Travel Manager Coordinator</li>
              <li>Flight & Aviation Agent</li>
              <li>Hotel & Lodging Agent</li>
              <li>Destination Research Agent</li>
              <li>Weather & Climate Agent</li>
              <li>Gastronomy & Food Agent</li>
              <li>Activity & Experience Agent</li>
              <li>Budget & Currency Agent</li>
              <li>Itinerary Synthesis Agent</li>
              <li>Critic & Schedule QA Agent</li>
            </ul>
          </div>

          {/* Connected Integrations */}
          <div>
            <h4 className="font-semibold text-slate-900 dark:text-slate-200 mb-3 text-xs uppercase tracking-wider">
              Connected APIs
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li className="flex items-center gap-1.5">
                <Cpu className="w-3 h-3 text-voyage-500" /> Groq LLM (Llama 3.3 70B)
              </li>
              <li className="flex items-center gap-1.5">
                <Plane className="w-3 h-3 text-sky-500" /> AviationStack Flight API
              </li>
              <li className="flex items-center gap-1.5">
                <CloudSun className="w-3 h-3 text-amber-500" /> OpenWeather Meteorology
              </li>
              <li className="flex items-center gap-1.5">
                <Globe className="w-3 h-3 text-emerald-500" /> Tavily AI Web Research
              </li>
              <li className="flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-purple-500" /> PostgreSQL / SQLite
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-200 dark:border-slate-800/80 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs gap-4">
          <p>© {new Date().getFullYear()} VoyageAI. Built for Advanced Agentic Travel Planning.</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Zero hardcoded mock trips</span>
            <span>•</span>
            <span>Real concurrency orchestration</span>
            <span>•</span>
            <span>Audited itinerary validation</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
