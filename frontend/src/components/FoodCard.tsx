import React from "react";
import { FoodResearch } from "../types";
import { Utensils, MapPin, Sparkles, CheckCircle2, DollarSign } from "lucide-react";

interface FoodCardProps {
  food: FoodResearch;
  currency: string;
}

export const FoodCard: React.FC<FoodCardProps> = ({ food, currency }) => {
  return (
    <div className="space-y-6">
      {/* Culinary Banner */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <span className="p-1.5 rounded-lg bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
            <Utensils className="w-4 h-4" />
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Gastronomic Discovery & Regional Dining
          </span>
        </div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
          Authentic Regional Specialties & Dining Districts
        </h3>
        {food.price_level_summary && (
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Price Expectation: {food.price_level_summary}
          </p>
        )}
      </div>

      {/* Signature Dishes */}
      {food.local_dishes && food.local_dishes.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-500">
            Must-Try Signature Dishes
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {food.local_dishes.map((dish, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl glass-panel border border-slate-200 dark:border-slate-800 space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <h5 className="font-bold text-sm text-slate-900 dark:text-white">
                    {dish.name}
                  </h5>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900">
                    Iconic Flavor
                  </span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  {dish.description}
                </p>
                {dish.must_try_reason && (
                  <p className="text-[11px] text-slate-400 italic">
                    ✨ {dish.must_try_reason}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Restaurants & Street Food */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Recommended Restaurants */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Utensils className="w-4 h-4 text-rose-500" />
            Curated Dining Venues
          </h4>
          <div className="space-y-3">
            {food.recommended_spots.map((spot, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between font-bold text-slate-900 dark:text-white">
                  <span>{spot.name}</span>
                  <span className="text-slate-500 font-semibold">{spot.price_level}</span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-500">
                  <MapPin className="w-3.5 h-3.5 text-rose-500" />
                  <span>{spot.area} • Specialty: {spot.specialty}</span>
                </div>
                {spot.description && (
                  <p className="text-slate-600 dark:text-slate-400">{spot.description}</p>
                )}
                {spot.dietary_suitability && spot.dietary_suitability.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {spot.dietary_suitability.map((d, didx) => (
                      <span
                        key={didx}
                        className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 text-[10px] font-medium"
                      >
                        {d}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Dietary Advice & Popular Food Areas */}
        <div className="space-y-5">
          {/* Dietary Suitability */}
          {food.dietary_suitability && Object.keys(food.dietary_suitability).length > 0 && (
            <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2.5">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                Dietary Guidance (Veg / Vegan / Halal)
              </h4>
              <div className="space-y-2 text-xs">
                {Object.entries(food.dietary_suitability).map(([k, v]) => (
                  <div key={k} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                    <span className="font-bold text-slate-800 dark:text-slate-200 capitalize block mb-0.5">
                      {k}:
                    </span>
                    <span className="text-slate-600 dark:text-slate-400">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Popular Food Areas */}
          {food.popular_food_areas && food.popular_food_areas.length > 0 && (
            <div className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 space-y-2.5">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-amber-500" />
                Famous Food Alleys & Market Halls
              </h4>
              <div className="flex flex-wrap gap-2">
                {food.popular_food_areas.map((area, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-xs font-semibold text-amber-800 dark:text-amber-300"
                  >
                    🍜 {area}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
