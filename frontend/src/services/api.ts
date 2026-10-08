import {
  AuthResponse,
  User,
  TripListItem,
  TripDetail,
  ProgressState,
  Conversation,
  ChatMessage,
  AdminOverview,
  RagDocumentList,
} from "../types";

const API_BASE = "/api";

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("voyageai_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `Request failed (${res.status})`;
    try {
      const errData = await res.json();
      if (errData.detail) {
        errorMsg = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  auth: {
    async register(data: { email: string; username: string; password: string; full_name?: string }): Promise<AuthResponse> {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return handleResponse<AuthResponse>(res);
    },

    async login(data: { username_or_email: string; password: string }): Promise<AuthResponse> {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return handleResponse<AuthResponse>(res);
    },

    async getMe(): Promise<User> {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<User>(res);
    },
  },

  admin: {
    async login(data: { username_or_email: string; password: string }): Promise<AuthResponse> {
      const res = await fetch(`${API_BASE}/admin/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return handleResponse<AuthResponse>(res);
    },

    async overview(): Promise<AdminOverview> {
      const res = await fetch(`${API_BASE}/admin/overview`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<AdminOverview>(res);
    },

    async listRagDocuments(): Promise<RagDocumentList> {
      const res = await fetch(`${API_BASE}/rag/admin/documents`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<RagDocumentList>(res);
    },

    async uploadRagDocument(formData: FormData): Promise<{ document_id: number; chunk_count: number; duplicate: boolean }> {
      const res = await fetch(`${API_BASE}/rag/admin/documents`, {
        method: "POST",
        headers: { ...getAuthHeader() },
        body: formData,
      });
      return handleResponse(res);
    },

    async deleteRagDocument(documentId: number): Promise<void> {
      const res = await fetch(`${API_BASE}/rag/admin/documents/${documentId}`, {
        method: "DELETE",
        headers: { ...getAuthHeader() },
      });
      if (!res.ok) throw new Error(`Failed to delete document (${res.status})`);
    },
  },

  trips: {
    async createFromPrompt(prompt: string): Promise<TripListItem> {
      const res = await fetch(`${API_BASE}/trips/plan-prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({ prompt }),
      });
      return handleResponse<TripListItem>(res);
    },

    async createStructured(params: {
      origin?: string;
      destination: string;
      start_date?: string;
      end_date?: string;
      duration_days: number;
      travellers: number;
      budget?: number;
      currency: string;
      travel_style: string;
      interests: string[];
      dietary_preferences: string[];
      accommodation_preferences?: string;
      special_constraints?: string;
    }): Promise<TripListItem> {
      const res = await fetch(`${API_BASE}/trips/plan-structured`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify(params),
      });
      return handleResponse<TripListItem>(res);
    },

    async list(search?: string): Promise<TripListItem[]> {
      const url = search ? `${API_BASE}/trips?search=${encodeURIComponent(search)}` : `${API_BASE}/trips`;
      const res = await fetch(url, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<TripListItem[]>(res);
    },

    async get(tripId: number): Promise<TripDetail> {
      const res = await fetch(`${API_BASE}/trips/${tripId}`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<TripDetail>(res);
    },

    async getProgress(tripId: number): Promise<ProgressState> {
      const res = await fetch(`${API_BASE}/trips/${tripId}/progress`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<ProgressState>(res);
    },

    async deleteTrip(tripId: number): Promise<void> {
      const res = await fetch(`${API_BASE}/trips/${tripId}`, {
        method: "DELETE",
        headers: { ...getAuthHeader() },
      });
      if (!res.ok) throw new Error("Failed to delete trip");
    },
  },

  chat: {
    async getConversation(tripId: number): Promise<Conversation> {
      const res = await fetch(`${API_BASE}/trips/${tripId}/chat`, {
        headers: { ...getAuthHeader() },
      });
      return handleResponse<Conversation>(res);
    },

    async sendMessage(tripId: number, message: string): Promise<ChatMessage> {
      const res = await fetch(`${API_BASE}/trips/${tripId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeader() },
        body: JSON.stringify({ message }),
      });
      return handleResponse<ChatMessage>(res);
    },
  },

  export: {
    getMarkdownUrl(tripId: number): string {
      return `${API_BASE}/trips/${tripId}/export/markdown`;
    },
    getPrintUrl(tripId: number): string {
      return `${API_BASE}/trips/${tripId}/export/print`;
    },
    getPdfUrl(tripId: number): string {
      return `${API_BASE}/trips/${tripId}/export/pdf`;
    },
  },

  integrations: {
    async getStatus(): Promise<any> {
      const res = await fetch(`${API_BASE}/integrations`);
      return handleResponse<any>(res);
    },
  },
};
