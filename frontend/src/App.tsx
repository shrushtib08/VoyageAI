import React, { useCallback, useEffect, useState } from "react";
import { AuthProvider } from "./hooks/useAuth";
import { ThemeProvider } from "./hooks/useTheme";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PlannerPage } from "./pages/PlannerPage";
import { ProgressPage } from "./pages/ProgressPage";
import { TripDetailPage } from "./pages/TripDetailPage";
import { AdminLoginPage } from "./pages/AdminLoginPage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";

function pageFromPath(path: string): string | null {
  if (path === "/admin/login") return "admin-login";
  if (path === "/admin") return "admin-dashboard";
  return null;
}

const MainApp: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>(() => pageFromPath(window.location.pathname) ?? "landing");
  const [selectedTripId, setSelectedTripId] = useState<number | null>(null);
  const [initialPrompt, setInitialPrompt] = useState<string>("");

  const navigate = useCallback((page: string) => {
    const adminPath = page === "admin-login" ? "/admin/login" : page === "admin-dashboard" ? "/admin" : null;
    if (adminPath) {
      window.history.pushState({}, "", adminPath);
    } else if (pageFromPath(window.location.pathname)) {
      window.history.pushState({}, "", "/");
    }
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPage(pageFromPath(window.location.pathname) ?? "landing");
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const handleTripCreated = (tripId: number) => {
    setSelectedTripId(tripId);
    setCurrentPage("progress");
  };

  const handleSelectTrip = (tripId: number) => {
    setSelectedTripId(tripId);
  };

  const handlePromptFromLanding = (promptText: string) => {
    setInitialPrompt(promptText);
    setCurrentPage("planner");
  };

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-200 ${currentPage === "landing" ? "landing-app" : "bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100"}`}>
      <Navbar onNavigate={navigate} currentPage={currentPage} />

      <main className={currentPage === "landing" ? "flex-1 w-full" : "flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8"}>
        {currentPage === "landing" && (
          <LandingPage onNavigate={navigate} onSetPrompt={handlePromptFromLanding} />
        )}

        {currentPage === "login" && (
          <LoginPage onNavigate={navigate} onSuccess={() => navigate("dashboard")} />
        )}

        {currentPage === "register" && (
          <RegisterPage onNavigate={navigate} onSuccess={() => navigate("dashboard")} />
        )}

        {currentPage === "dashboard" && (
          <DashboardPage onNavigate={navigate} onSelectTrip={handleSelectTrip} />
        )}

        {currentPage === "planner" && (
          <PlannerPage
            onNavigate={navigate}
            onTripCreated={handleTripCreated}
            initialPrompt={initialPrompt}
          />
        )}

        {currentPage === "progress" && selectedTripId && (
          <ProgressPage
            tripId={selectedTripId}
            onNavigate={navigate}
            onSelectTrip={handleSelectTrip}
          />
        )}

        {currentPage === "trip-detail" && selectedTripId && (
          <TripDetailPage tripId={selectedTripId} onNavigate={navigate} />
        )}

        {currentPage === "admin-login" && <AdminLoginPage onNavigate={navigate} />}

        {currentPage === "admin-dashboard" && <AdminDashboardPage onNavigate={navigate} />}
      </main>

      {currentPage !== "landing" && <Footer />}
    </div>
  );
};

export function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainApp />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
