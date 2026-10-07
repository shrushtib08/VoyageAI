import React from "react";
import { HotelResearch } from "../types";
import { Hotel, Star, MapPin, CheckCircle, Info, Sparkles, Building2 } from "lucide-react";

interface HotelViewProps {
  hotel: HotelResearch;
  currency: string;
}

export const HotelView: React.FC<HotelViewProps> = ({ hotel, currency }) => {
  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="p-1 rounded-md bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
              <Building2 className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Curated Accommodations • {hotel.budget_category || "Balanced Tier"}
            </span>
          </div>
          <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            Recommended Stays & Neighborhood Lodging
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Carefully curated properties positioned close to transit lines and primary attractions.
          </p>
        </div>

        {hotel.avg_nightly_price && (
          <div className="sm:text-right">
            <span className="text-xs text-slate-500 block">Avg. Nightly Benchmark</span>
            <span className="text-2xl font-extrabold text-amber-600 dark:text-amber-400">
              {currency} {hotel.avg_nightly_price.toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-400 block">/ night</span>
          </div>
        )}
      </div>

      {/* Hotel Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {hotel.recommendations.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="text-lg font-bold text-slate-900 dark:text-white">
                    {item.name}
                  </h4>
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-amber-500" />
                    <span>{item.area}</span>
                  </div>
                </div>

                {item.rating && (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-300 text-xs font-bold">
                    <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
                    <span>{item.rating}</span>
                  </div>
                )}
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {item.description}
              </p>

              {item.recommendation_reason && (
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 text-xs text-slate-700 dark:text-slate-300 space-y-1">
                  <span className="font-bold text-[11px] text-slate-500 uppercase tracking-wider block">
                    Why VoyageAI Selected This:
                  </span>
                  <p>{item.recommendation_reason}</p>
                </div>
              )}

              {/* Amenities */}
              {item.amenities && item.amenities.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {item.amenities.map((amenity, aidx) => (
                    <span
                      key={aidx}
                      className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[11px] text-slate-600 dark:text-slate-400 font-medium"
                    >
                      {amenity}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Price Footer */}
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 block">Estimated Rate</span>
                <span className="text-base font-extrabold text-slate-900 dark:text-white">
                  {item.currency || currency} {item.approx_price_per_night?.toLocaleString()}
                  <span className="text-xs font-normal text-slate-500"> / night</span>
                </span>
              </div>
              <span className="text-[11px] text-slate-400 italic">
                Researched benchmark
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Booking Notice */}
      <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 flex items-center gap-2.5 text-xs text-slate-500 dark:text-slate-400">
        <Info className="w-4 h-4 text-slate-400 shrink-0" />
        <span>
          Hotel recommendations are generated by our Hotel Agent based on regional hospitality indices and traveler satisfaction metrics. Always verify direct booking terms and taxes before securing reservations.
        </span>
      </div>
    </div>
  );
};
