import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "../types";
import { api } from "../services/api";
import { Send, Bot, User as UserIcon, Sparkles, Loader2, CheckCircle } from "lucide-react";

interface FollowUpChatProps {
  tripId: number;
  destination: string;
}

export const FollowUpChat: React.FC<FollowUpChatProps> = ({ tripId, destination }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversation();
  }, [tripId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversation = async () => {
    try {
      const conv = await api.chat.getConversation(tripId);
      if (conv && conv.messages) {
        setMessages(conv.messages);
      }
    } catch (err) {
      console.error("Failed to load conversation", err);
    }
  };

  const handleSend = async (messageText: string) => {
    const textToSend = messageText.trim();
    if (!textToSend || isLoading) return;

    setInput("");
    setIsLoading(true);

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      conversation_id: 0,
      sender: "user",
      content: textToSend,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const reply = await api.chat.sendMessage(tripId, textToSend);
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, reply]);
    } catch (err) {
      console.error("Error sending message", err);
    } finally {
      setIsLoading(false);
    }
  };

  const quickPrompts = [
    "Make Day 3 more relaxed.",
    "Add more vegetarian restaurants.",
    "Can I optimize the budget?",
    "Where is the best sunset view?",
  ];

  return (
    <div className="flex flex-col h-[650px] rounded-2xl glass-panel border border-slate-200 dark:border-slate-800 overflow-hidden shadow-lg">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-voyage-600 to-teal-500 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
              <span>VoyageAI Concierge</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </h4>
            <p className="text-[11px] text-slate-500">
              Trip memory active • Preserves your {destination} itinerary context
            </p>
          </div>
        </div>

        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-voyage-100 dark:bg-voyage-950 text-voyage-700 dark:text-voyage-300">
          Context Aware
        </span>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === "user";
          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                  isUser
                    ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                    : "bg-voyage-600 text-white"
                }`}
              >
                {isUser ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? "bg-voyage-600 text-white rounded-tr-none shadow-sm shadow-voyage-500/10"
                    : "bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none border border-slate-200/80 dark:border-slate-700/80 shadow-sm"
                }`}
              >
                <p className="whitespace-pre-line">{msg.content}</p>

                {msg.actions_taken && Object.keys(msg.actions_taken).some((key) => !["sources", "source_types", "grounded"].includes(key)) && (
                  <div className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/60 text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>
                      Applied to Trip: {Object.entries(msg.actions_taken)
                        .filter(([key]) => !["sources", "source_types", "grounded"].includes(key))
                        .map(([, value]) => String(value))
                        .join(", ")}
                    </span>
                  </div>
                )}
                {!!msg.sources?.length && (
                  <div className="mt-3 pt-2 border-t border-slate-200 dark:border-slate-700/60">
                    <p className="mb-1 text-[10px] font-bold uppercase tracking-wide text-slate-500">
                      Sources · {[...new Set(msg.sources.map((source) => source.source_type))].join(" · ")}
                    </p>
                    <ul className="space-y-1">
                      {msg.sources.map((source, index) => (
                        <li key={`${source.chunk_id ?? source.url ?? source.title}-${index}`}>
                          {source.url ? (
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] text-voyage-700 dark:text-voyage-300 underline underline-offset-2"
                            >
                              {source.title}
                            </a>
                          ) : (
                            <span className="text-[11px] text-slate-600 dark:text-slate-300">{source.title}</span>
                          )}
                          {source.source && <span className="ml-1 text-[10px] text-slate-500">({source.source})</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-voyage-600 text-white flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-tl-none flex items-center gap-2 text-xs text-slate-500">
              <Loader2 className="w-4 h-4 animate-spin text-voyage-600" />
              <span>Analyzing trip memory and formulating adjustment...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Chips */}
      <div className="px-4 py-2 bg-slate-50/50 dark:bg-slate-900/50 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center gap-1.5 overflow-x-auto text-xs no-scrollbar">
        <Sparkles className="w-3.5 h-3.5 text-voyage-500 shrink-0 mr-1" />
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
            className="px-2.5 py-1 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-voyage-400 text-slate-700 dark:text-slate-300 whitespace-nowrap text-[11px] transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(input);
        }}
        className="p-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question or request a modification (e.g. 'Make Day 3 more relaxed')..."
          disabled={isLoading}
          className="flex-1 px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border-none text-xs sm:text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-voyage-500"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-2.5 rounded-xl bg-voyage-600 hover:bg-voyage-700 disabled:opacity-50 text-white shadow-sm transition-transform active:scale-95"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
