import React, { useState } from "react";
import { AuthProvider, useAuth } from "./hooks/useAuth";
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

const MainApp: React.FC = () => {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState<string>("landing");
  const [selectedTripId, setSelectedTripId] = useState<number | null>(null);
  const [initialPrompt, setInitialPrompt] = useState<string>("");

  const navigate = (page: string) => {
    // If navigating to dashboard or planner when not logged in, allow them to view or prompt them
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

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
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200">
      <Navbar onNavigate={navigate} currentPage={currentPage} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
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
      </main>

      <Footer />
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
