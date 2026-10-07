import React from "react";
import { WeatherResearch } from "../types";
import { CloudSun, Droplets, Thermometer, ShieldCheck, CheckCircle2, Luggage, Info } from "lucide-react";

interface WeatherCardProps {
  weather: WeatherResearch;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ weather }) => {
  return (
    <div className="space-y-6">
      {/* Weather Header Card */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span
                className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
                  weather.is_live_forecast
                    ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
                }`}
              >
                {weather.is_live_forecast ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Live OpenWeather Feed
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-3.5 h-3.5 text-amber-500" /> Seasonal Climate Guidance
                  </>
                )}
              </span>
            </div>
            <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
              Climate & Weather Conditions in {weather.destination}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {weather.season_summary}
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-4">
            {weather.avg_temp_min !== undefined && weather.avg_temp_max !== undefined && (
              <div className="p-3 rounded-xl bg-orange-50 dark:bg-orange-950/40 border border-orange-200 dark:border-orange-900/60 text-center">
                <div className="flex items-center justify-center gap-1 text-orange-600 dark:text-orange-400 mb-0.5">
                  <Thermometer className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase">Temp</span>
                </div>
                <span className="text-lg font-black text-slate-900 dark:text-white">
                  {weather.avg_temp_min}° – {weather.avg_temp_max}°C
                </span>
              </div>
            )}

            {weather.precipitation_probability !== undefined && (
              <div className="p-3 rounded-xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-900/60 text-center">
                <div className="flex items-center justify-center gap-1 text-sky-600 dark:text-sky-400 mb-0.5">
                  <Droplets className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase">Rain</span>
                </div>
                <span className="text-lg font-black text-slate-900 dark:text-white">
                  {weather.precipitation_probability}%
                </span>
              </div>
            )}
          </div>
        </div>

        {weather.weather_conditions && (
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 dark:text-slate-200 pt-2 border-t border-slate-100 dark:border-slate-800">
            <CloudSun className="w-4 h-4 text-orange-500" />
            <span>Expected: {weather.weather_conditions}</span>
          </div>
        )}
      </div>

      {/* Travel Advice & Packing List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Travel Advice */}
        {weather.travel_advice && (
          <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Info className="w-4 h-4 text-voyage-500" />
              Meteorological Travel Advice
            </h4>
            <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {weather.travel_advice}
            </p>
          </div>
        )}

        {/* Packing Suggestions */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Luggage className="w-4 h-4 text-emerald-500" />
            Recommended Wardrobe & Gear
          </h4>
          <div className="flex flex-wrap gap-2">
            {weather.packing_suggestions.map((item, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-xs font-medium text-emerald-800 dark:text-emerald-300"
              >
                ✓ {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
