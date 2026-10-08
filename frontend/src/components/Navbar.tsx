import React from "react";
import { Compass, Moon, Sun, LogOut, PlusCircle, LayoutDashboard, Sparkles, ShieldCheck } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../hooks/useTheme";

interface NavbarProps {
  onNavigate: (page: string) => void;
  currentPage: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate, currentPage }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const isLanding = currentPage === "landing";

  return (
    <header className={`sticky top-0 z-50 glass-panel border-b border-slate-200/80 dark:border-slate-800/80 ${isLanding ? "site-header-dark" : ""}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div
          onClick={() => onNavigate("landing")}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="landing-brand-mark w-10 h-10 rounded-xl bg-gradient-to-tr from-voyage-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-voyage-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">
                Voyage<span className="text-voyage-600 dark:text-voyage-400">AI</span>
              </span>
              <span className="multi-agent-badge text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-voyage-100 dark:bg-voyage-950 text-voyage-700 dark:text-voyage-300 border border-voyage-200 dark:border-voyage-800">
                Multi-Agent
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block -mt-0.5">
              Your intelligent team of AI travel agents
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center gap-2 sm:gap-4">
          <button
            onClick={() => onNavigate("landing")}
            className={`landing-nav-explore px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              currentPage === "landing"
                ? "text-voyage-600 dark:text-voyage-400 bg-voyage-50 dark:bg-voyage-950/60"
                : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            Explore
          </button>

          {user ? (
            <>
              {user.is_admin ? (
                <button
                  onClick={() => onNavigate("admin-dashboard")}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg text-voyage-700 dark:text-voyage-300"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span className="hidden sm:inline">Admin</span>
                </button>
              ) : <button
                onClick={() => onNavigate("dashboard")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  currentPage === "dashboard"
                    ? "text-voyage-600 dark:text-voyage-400 bg-voyage-50 dark:bg-voyage-950/60"
                    : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span className="hidden sm:inline">My Trips</span>
              </button>}

              {!user.is_admin && <button
                onClick={() => onNavigate("planner")}
                className="landing-plan-button flex items-center gap-1.5 px-3.5 py-1.5 text-sm font-semibold rounded-lg bg-voyage-600 hover:bg-voyage-700 text-white shadow-sm shadow-voyage-500/20 transition-all hover:scale-[1.02]"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Plan Trip</span>
              </button>}
            </>
          ) : (
            <button
              onClick={() => onNavigate("planner")}
              className="landing-plan-button flex items-center gap-1.5 px-3.5 py-1.5 text-sm font-semibold rounded-lg bg-voyage-600 hover:bg-voyage-700 text-white shadow-sm shadow-voyage-500/20 transition-all hover:scale-[1.02]"
            >
              <Sparkles className="w-4 h-4" />
              <span>Plan Trip</span>
            </button>
          )}

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
          >
            {theme === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {/* Auth Actions */}
          {user ? (
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300">
                <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center font-bold text-voyage-600 dark:text-voyage-400">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <span className="hidden md:inline font-medium">{user.username}</span>
              </div>
              <button
                onClick={logout}
                className="p-1.5 text-slate-400 hover:text-red-500 dark:hover:text-red-400 rounded-lg transition-colors"
                title="Log out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => onNavigate("login")}
                className="landing-login px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-voyage-600 dark:hover:text-voyage-400 transition-colors"
              >
                Log in
              </button>
              <button
                onClick={() => onNavigate("register")}
                className="landing-sign-up px-3 py-1.5 text-sm font-semibold rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Sign up
              </button>
              <button
                onClick={() => onNavigate("admin-login")}
                className="landing-admin-link hidden lg:inline px-2 py-1.5 text-xs text-slate-500 hover:text-voyage-600 dark:hover:text-voyage-400"
              >
                Admin
              </button>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};
