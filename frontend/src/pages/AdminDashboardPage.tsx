import React, { FormEvent, useCallback, useEffect, useState } from "react";
import { AlertCircle, Database, FileText, Loader2, RefreshCw, ShieldCheck, Trash2, Users, Workflow } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { AdminOverview, RagDocument } from "../types";
import { api } from "../services/api";

interface AdminDashboardPageProps {
  onNavigate: (page: string) => void;
}

export const AdminDashboardPage: React.FC<AdminDashboardPageProps> = ({ onNavigate }) => {
  const { user, logout, isLoading } = useAuth();
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [documents, setDocuments] = useState<RagDocument[]>([]);
  const [ragAvailable, setRagAvailable] = useState(true);
  const [ragUnavailableMessage, setRagUnavailableMessage] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const [data, ragDocs] = await Promise.all([api.admin.overview(), api.admin.listRagDocuments()]);
      setOverview(data);
      setDocuments(ragDocs.documents);
      setRagAvailable(ragDocs.available);
      setRagUnavailableMessage(ragDocs.message ?? null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load administrator data.");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (isLoading) return;
    const timer = window.setTimeout(() => {
      if (!user?.is_admin) {
        logout();
        onNavigate("admin-login");
        return;
      }
      void load();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [isLoading, load, logout, onNavigate, user?.is_admin]);

  const addDocument = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || !title.trim() || !source.trim()) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("title", title.trim());
      form.append("source", source.trim());
      if (destination.trim()) form.append("destination", destination.trim());
      const result = await api.admin.uploadRagDocument(form);
      setNotice(result.duplicate ? "This document was already ingested." : `Document added with ${result.chunk_count} searchable chunks.`);
      setTitle("");
      setSource("");
      setDestination("");
      setFile(null);
      const input = document.getElementById("rag-file") as HTMLInputElement | null;
      if (input) input.value = "";
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Document ingestion failed.");
    } finally {
      setBusy(false);
    }
  };

  const removeDocument = async (documentId: number) => {
    if (!window.confirm("Delete this knowledge document and all of its chunks?")) return;
    setBusy(true);
    setError(null);
    try {
      await api.admin.deleteRagDocument(documentId);
      setDocuments((current) => current.filter((item) => item.id !== documentId));
      setNotice("Knowledge document deleted.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Document deletion failed.");
    } finally {
      setBusy(false);
    }
  };

  const signOut = () => {
    logout();
    onNavigate("admin-login");
  };

  return (
    <div className="space-y-8 pb-12">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-voyage-600 dark:text-voyage-400">VoyageAI control room</p>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white">Administrator dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">Signed in as {user?.username}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => void load()} disabled={busy} className="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${busy ? "animate-spin" : ""}`} /> Refresh
          </button>
          <button onClick={signOut} className="px-4 py-2 rounded-xl bg-slate-900 text-white">Sign out</button>
        </div>
      </header>

      {error && <div role="alert" className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 flex gap-2"><AlertCircle className="w-5 h-5 shrink-0" />{error}</div>}
      {notice && <div role="status" className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300">{notice}</div>}

      <section className="grid grid-cols-2 xl:grid-cols-5 gap-3">
        {[
          { label: "Users", value: overview?.counts.users, icon: Users },
          { label: "Trips", value: overview?.counts.trips, icon: FileText },
          { label: "Agent runs", value: overview?.counts.agent_runs, icon: Workflow },
          { label: "Research sources", value: overview?.counts.research_sources, icon: ShieldCheck },
          { label: "RAG documents", value: overview?.counts.rag_documents ?? documents.length, icon: Database },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="glass-panel p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
            <Icon className="w-5 h-5 text-voyage-600 mb-3" />
            <p className="text-2xl font-extrabold text-slate-900 dark:text-white">{value ?? "—"}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        ))}
      </section>

      <section className="grid xl:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <h2 className="font-bold text-lg mb-4">Recent users</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase text-slate-500"><tr><th className="py-2">Account</th><th className="py-2">Role</th><th className="py-2">Created</th></tr></thead>
              <tbody>{overview?.users.map((item) => <tr key={item.id} className="border-t border-slate-200 dark:border-slate-800"><td className="py-2"><span className="block font-semibold">{item.username}</span><span className="text-xs text-slate-500">{item.email}</span></td><td>{item.is_admin ? "Admin" : "Traveler"}</td><td>{item.created_at ? new Date(item.created_at).toLocaleDateString() : "—"}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <h2 className="font-bold text-lg mb-4">Recent trips</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase text-slate-500"><tr><th className="py-2">Trip</th><th className="py-2">Traveler</th><th className="py-2">Status</th></tr></thead>
              <tbody>{overview?.trips.map((item) => <tr key={item.id} className="border-t border-slate-200 dark:border-slate-800"><td className="py-2"><span className="block font-semibold">{item.title}</span><span className="text-xs text-slate-500">{item.destination}</span></td><td>{item.username}</td><td className="capitalize">{item.status}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-5">
        <div>
          <h2 className="font-bold text-xl">RAG knowledge</h2>
          <p className="text-sm text-slate-500">Add stable travel references. Live prices, weather, and availability belong to live providers.</p>
        </div>
        {!ragAvailable && (
          <div role="status" className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 text-sm">
            {ragUnavailableMessage || "RAG is unavailable in the current database configuration."}
          </div>
        )}
        <form onSubmit={addDocument} className="grid md:grid-cols-2 xl:grid-cols-4 gap-3 items-end">
          <label className="text-xs font-semibold">Title<input required value={title} onChange={(event) => setTitle(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent p-2" /></label>
          <label className="text-xs font-semibold">Source / publisher<input required value={source} onChange={(event) => setSource(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent p-2" /></label>
          <label className="text-xs font-semibold">Destination (optional)<input value={destination} onChange={(event) => setDestination(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent p-2" /></label>
          <label className="text-xs font-semibold">Document<input id="rag-file" required type="file" accept=".pdf,.txt,.md,.markdown,.html,.htm" onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="mt-1 block w-full text-xs" /></label>
          <button disabled={busy || !file} className="md:col-span-2 xl:col-span-4 px-4 py-2.5 rounded-xl bg-voyage-600 text-white font-semibold disabled:opacity-50 flex justify-center items-center gap-2">
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />} Ingest document
          </button>
        </form>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase text-slate-500"><tr><th className="py-2">Document</th><th>Destination</th><th>Chunks</th><th /></tr></thead>
            <tbody>{documents.map((item) => <tr key={item.id} className="border-t border-slate-200 dark:border-slate-800"><td className="py-3"><span className="font-semibold">{item.title}</span><span className="block text-xs text-slate-500">{item.source}</span></td><td>{item.destination || "General"}</td><td>{item.chunk_count}</td><td className="text-right"><button aria-label={`Delete ${item.title}`} onClick={() => void removeDocument(item.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg"><Trash2 className="w-4 h-4" /></button></td></tr>)}</tbody>
          </table>
          {!documents.length && <p className="py-4 text-sm text-slate-500">No knowledge documents have been ingested yet.</p>}
        </div>
      </section>

      <section className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
        <h2 className="font-bold text-lg mb-4">Latest agent runs</h2>
        <div className="grid sm:grid-cols-2 xl:grid-cols-5 gap-3">
          {overview?.agent_runs.map((run) => (
            <div key={run.id} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900">
              <p className="font-semibold text-sm">{run.agent_name}</p>
              <p className="text-xs text-slate-500">Trip #{run.trip_id} · <span className="capitalize">{run.status}</span></p>
            </div>
          ))}
        </div>
        {!overview?.agent_runs.length && <p className="text-sm text-slate-500">No agent runs yet.</p>}
      </section>
    </div>
  );
};
