import React, { useState } from "react";
import { AlertCircle, ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";

interface AdminLoginPageProps {
  onNavigate: (page: string) => void;
}

export const AdminLoginPage: React.FC<AdminLoginPageProps> = ({ onNavigate }) => {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await api.admin.login({
        username_or_email: identifier.trim(),
        password,
      });
      if (!response.user.is_admin) {
        throw new Error("This account does not have administrator privileges.");
      }
      login(response.access_token, response.user);
      onNavigate("admin-dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Administrator sign-in failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-slate-900 dark:bg-slate-700 text-white flex items-center justify-center mx-auto">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Administrator sign-in</h1>
          <p className="text-sm text-slate-500">Use an administrator account created by the server operator.</p>
        </div>

        <form onSubmit={submit} className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
          {error && (
            <div role="alert" className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
            Username or email
            <input
              autoComplete="username"
              required
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              className="mt-1.5 w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
            Password
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1.5 w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Sign in securely <ArrowRight className="w-4 h-4" /></>}
          </button>
          <button type="button" onClick={() => onNavigate("login")} className="w-full text-sm text-voyage-700 dark:text-voyage-300 hover:underline">
            Return to traveler sign-in
          </button>
        </form>
      </div>
    </div>
  );
};
