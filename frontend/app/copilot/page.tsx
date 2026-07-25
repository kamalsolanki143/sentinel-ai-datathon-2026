"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  BrainCircuit,
  Send,
  Sparkles,
  Bot,
  User,
  Copy,
  Check,
  RotateCcw,
  History,
  Plus,
  X,
  ThumbsUp,
  ThumbsDown,
  Bookmark,
  Download,
  Search,
  Pin,
  Cpu,
  Layers,
  FileText,
  ShieldAlert,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import CaseSummaryPanel from "@/components/Copilot/CaseSummaryPanel";
import PageHeader from "@/components/Common/PageHeader";
import StatusBadge from "@/components/Common/StatusBadge";

interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  codeSnippet?: string;
  codeLanguage?: string;
  structuredMetrics?: { label: string; value: string; color?: string }[];
  reaction?: "up" | "down" | "saved";
}

interface ChatSession {
  id: string;
  title: string;
  date: string;
  caseId: string;
  isPinned?: boolean;
}

const promptSuggestions = [
  "Analyze suspect Marcus Vance's syndicate ties",
  "Generate tactical deployment plan for Bank Robbery",
  "Summarize wiretap evidence for CAS-8924",
  "Predict 48h getaway escalation vectors",
];

const mockSessions: ChatSession[] = [
  { id: "S-101", title: "CAS-8924 Syndicate Analysis", date: "Today, 10:42 AM", caseId: "CAS-8924", isPinned: true },
  { id: "S-102", title: "Sector 4 Threat Prediction", date: "Yesterday", caseId: "CAS-8910", isPinned: true },
  { id: "S-103", title: "Port Wiretap Synthesis", date: "Jul 22, 2026", caseId: "CAS-8890" },
  { id: "S-104", title: "Viper Financial Trace", date: "Jul 20, 2026", caseId: "CAS-8845" },
];

const initialMessages: Message[] = [
  {
    id: "m-1",
    sender: "assistant",
    text: `### Sentinel AI Copilot Initialized\n\nWelcome back, Commander. I have synchronized with **Sentinel Central Database** and active surveillance feeds.\n\n**Current Active Context:**\n- **Primary Case:** \`CAS-8924\` (Downtown Commercial Bank Robbery)\n- **High-Risk Target:** Marcus "Viper" Vance (Affiliation: Viper Syndicate)\n- **Current Threat Level:** DEFCON 3 (Elevated Alert)\n\nHow can I assist your intelligence operations today?`,
    timestamp: "10:42 AM",
    structuredMetrics: [
      { label: "AI Model", value: "v4.2-Neural", color: "text-primary" },
      { label: "Nodes Tracked", value: "1,204", color: "text-accent" },
      { label: "Confidence", value: "99.8%", color: "text-emerald-500" },
    ],
  },
];

export default function CopilotPage() {
  const [activeSessionId, setActiveSessionId] = useState("S-101");
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputQuery, setInputQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showHistoryMobile, setShowHistoryMobile] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "workspace">("chat");
  const [searchHistory, setSearchHistory] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = (textOverride?: string) => {
    const query = textOverride || inputQuery;
    if (!query.trim()) return;

    const userMessage: Message = {
      id: `usr-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textOverride) setInputQuery("");
    setIsTyping(true);

    // Simulate AI Copilot Streaming response
    setTimeout(() => {
      let botResponseText = "";
      let codeSnippet: string | undefined;
      let structuredMetrics: Message["structuredMetrics"];

      if (query.toLowerCase().includes("vance") || query.toLowerCase().includes("syndicate")) {
        botResponseText = `### Tactical Dossier Analysis: Marcus "Viper" Vance\n\nCross-referencing **Graph Neural Network** nodes for \`CAS-8924\`:\n\n- **Role:** High-ranking Operations Strategist, Viper Syndicate.\n- **Primary Territory:** Sector 4 Commercial District.\n- **Known Associates:** Viktor Thorne (Enforcer), Apex Logistics LLC (Front Company).\n- **Active Warrants:** 4 Federal Warrants (Armed Robbery, Wire Fraud).\n\n**AI Recommendation:**\nPre-position ANPR license plate scanners on **Highway 101 Northbound Expressway** to intercept getaway vehicle \`XYZ-9082\`.`;
        structuredMetrics = [
          { label: "Target Risk Score", value: "96 / 100", color: "text-red-500" },
          { label: "Network Connectivity", value: "High (42 Edges)", color: "text-amber-500" },
          { label: "Escape Vector Prob.", value: "88.4%", color: "text-primary" },
        ];
        codeSnippet = `// Sentinel AI GNN Spatial Dispatch Script\nconst dispatchPlan = await SentinelAI.predictGetaway({\n  suspectId: "ENT-89402",\n  jurisdiction: "Sector 4",\n  confidenceThreshold: 0.95,\n});`;
      } else {
        botResponseText = `### Operational Intelligence Query Processed\n\nI have analyzed your request regarding: "${query}".\n\n**Key Telemetry Data:**\n- **Surveillance Feeds:** 14 CCTV streams synchronized.\n- **CAD Incident Stream:** 3 active priority calls in Sector 4.\n- **Pattern Match:** 94.2% structural alignment with past commercial robbery signatures.\n\nLet me know if you would like me to generate a formal Intelligence Dossier (PDF/CSV) or trigger unit dispatches.`;
        structuredMetrics = [
          { label: "Query Speed", value: "0.42s", color: "text-emerald-500" },
          { label: "Database Hits", value: "148 Records", color: "text-primary" },
        ];
      }

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        sender: "assistant",
        text: botResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        structuredMetrics,
        codeSnippet,
        codeLanguage: "typescript",
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1400);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleReaction = (id: string, type: "up" | "down" | "saved") => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === id ? { ...msg, reaction: msg.reaction === type ? undefined : type } : msg
      )
    );
  };

  const filteredSessions = mockSessions.filter((s) =>
    s.title.toLowerCase().includes(searchHistory.toLowerCase()) ||
    s.caseId.toLowerCase().includes(searchHistory.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Section Header */}
      <PageHeader
        title="AI Security Copilot"
        subtitle="Conversational Reasoning & Tactical Intelligence Agent"
        breadcrumbs={[
          { label: "Command Center", href: "/dashboard" },
          { label: "AI Security Copilot" },
        ]}
        icon={BrainCircuit}
        statusBadge={<StatusBadge variant="success">MODEL v4.2 PROD</StatusBadge>}
      >
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 flex items-center text-xs font-semibold">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === "chat"
                  ? "bg-primary text-white shadow font-bold"
                  : "text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Copilot Chat
            </button>
            <button
              onClick={() => setActiveTab("workspace")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === "workspace"
                  ? "bg-primary text-white shadow font-bold"
                  : "text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Investigation Workspace
            </button>
          </div>
        </div>
      </PageHeader>

      {/* Primary Layout Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Sidebar: Session History & Context */}
        <div className="hidden lg:block lg:col-span-3 rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-4 shadow-md dark:shadow-xl space-y-4 transition-colors duration-300">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-2 uppercase tracking-wider font-mono">
              <History className="h-4 w-4 text-primary" /> Session Vault
            </h3>
            <button
              onClick={() => setMessages(initialMessages)}
              className="p-1.5 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
              title="New Investigation Chat"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          <div className="relative">
            <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search chat history..."
              value={searchHistory}
              onChange={(e) => setSearchHistory(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-sans"
            />
          </div>

          <div className="space-y-1.5 max-h-[460px] overflow-y-auto no-scrollbar">
            {filteredSessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setActiveSessionId(session.id)}
                className={`w-full p-3 rounded-2xl border text-left transition-all space-y-1 ${
                  activeSessionId === session.id
                    ? "border-primary/40 bg-primary/10 dark:bg-primary/15 text-slate-900 dark:text-white shadow-sm"
                    : "border-transparent hover:bg-slate-50 dark:hover:bg-white/[0.03] text-slate-600 dark:text-white/70"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs tracking-tight truncate">{session.title}</span>
                  {session.isPinned && <Pin className="h-3 w-3 text-accent shrink-0" />}
                </div>
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 dark:text-white/40">
                  <span>{session.caseId}</span>
                  <span>{session.date}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className={`col-span-1 ${activeTab === "chat" ? "lg:col-span-9" : "lg:col-span-12"}`}>
          {activeTab === "chat" ? (
            <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl shadow-md dark:shadow-xl flex flex-col h-[650px] overflow-hidden transition-colors duration-300">
              {/* Chat Stream Header */}
              <div className="p-4 border-b border-slate-100 dark:border-white/[0.08] flex items-center justify-between bg-slate-50/50 dark:bg-white/[0.02]">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shadow-md">
                    <BrainCircuit className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                      Copilot Session: CAS-8924
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                    </h4>
                    <p className="text-[11px] text-slate-500 dark:text-white/40 font-mono">
                      ACTIVE NEURAL AGENT • LATENCY &lt; 0.4s
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setMessages(initialMessages)}
                    className="p-2 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white text-xs font-mono flex items-center gap-1.5 transition-colors"
                  >
                    <RotateCcw className="h-3.5 w-3.5" /> Clear Stream
                  </button>
                </div>
              </div>

              {/* Chat Messages Stream */}
              <div className="flex-1 p-4 md:p-6 overflow-y-auto space-y-6 font-sans">
                {messages.map((m) => (
                  <motion.div
                    key={m.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex items-start gap-3 ${
                      m.sender === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <div
                      className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 font-bold text-xs ${
                        m.sender === "assistant"
                          ? "bg-gradient-to-br from-primary to-accent text-white shadow"
                          : "bg-slate-800 text-white"
                      }`}
                    >
                      {m.sender === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                    </div>

                    <div
                      className={`space-y-3 max-w-[85%] sm:max-w-[75%] ${
                        m.sender === "user" ? "text-right" : ""
                      }`}
                    >
                      <div
                        className={`p-4 rounded-3xl text-xs sm:text-sm leading-relaxed ${
                          m.sender === "user"
                            ? "bg-primary text-white font-medium shadow-md"
                            : "bg-slate-50 dark:bg-white/[0.03] text-slate-800 dark:text-white/90 border border-slate-200/80 dark:border-white/[0.08] shadow-sm"
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{m.text}</div>

                        {/* Structured Metric Chips */}
                        {m.structuredMetrics && (
                          <div className="mt-3 pt-3 border-t border-slate-200/60 dark:border-white/[0.08] grid grid-cols-2 sm:grid-cols-3 gap-2">
                            {m.structuredMetrics.map((sm, idx) => (
                              <div
                                key={idx}
                                className="p-2 rounded-xl bg-white dark:bg-[#0f172a] border border-slate-200 dark:border-white/10 text-[10px] font-mono"
                              >
                                <span className="text-slate-400 dark:text-white/40 block">{sm.label}</span>
                                <span className={`font-bold ${sm.color || "text-slate-900 dark:text-white"}`}>
                                  {sm.value}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Code Snippet Block */}
                        {m.codeSnippet && (
                          <div className="mt-3 rounded-2xl bg-slate-900 text-slate-100 p-3 font-mono text-[11px] overflow-x-auto relative group">
                            <button
                              onClick={() => copyToClipboard(m.codeSnippet!, `code-${m.id}`)}
                              className="absolute top-2 right-2 p-1 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 text-[10px] flex items-center gap-1"
                            >
                              {copiedId === `code-${m.id}` ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                            </button>
                            <pre><code>{m.codeSnippet}</code></pre>
                          </div>
                        )}
                      </div>

                      {/* Footer Info & Actions */}
                      <div
                        className={`flex items-center gap-3 text-[10px] font-mono text-slate-400 dark:text-white/40 ${
                          m.sender === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        <span>{m.timestamp}</span>

                        {m.sender === "assistant" && (
                          <div className="flex items-center gap-1.5 ml-2">
                            <button
                              onClick={() => copyToClipboard(m.text, m.id)}
                              className="p-1 hover:text-slate-700 dark:hover:text-white"
                              title="Copy Response"
                            >
                              {copiedId === m.id ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
                            </button>
                            <button
                              onClick={() => toggleReaction(m.id, "up")}
                              className={`p-1 hover:text-emerald-500 ${m.reaction === "up" ? "text-emerald-500 font-bold" : ""}`}
                            >
                              <ThumbsUp className="h-3 w-3" />
                            </button>
                            <button
                              onClick={() => toggleReaction(m.id, "down")}
                              className={`p-1 hover:text-red-500 ${m.reaction === "down" ? "text-red-500 font-bold" : ""}`}
                            >
                              <ThumbsDown className="h-3 w-3" />
                            </button>
                            <button
                              onClick={() => toggleReaction(m.id, "saved")}
                              className={`p-1 hover:text-accent ${m.reaction === "saved" ? "text-accent font-bold" : ""}`}
                            >
                              <Bookmark className="h-3 w-3" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}

                {isTyping && (
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary to-accent text-white flex items-center justify-center shrink-0">
                      <Cpu className="h-4 w-4 animate-spin" />
                    </div>
                    <div className="p-4 rounded-3xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/[0.08] text-xs font-mono text-slate-500 dark:text-white/60 flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-accent animate-pulse" />
                      Security Copilot is synthesizing tensor graphs & ANPR feeds...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Suggested Prompt Chips */}
              <div className="px-4 py-2 border-t border-slate-100 dark:border-white/[0.06] bg-slate-50/50 dark:bg-white/[0.01] flex items-center gap-2 overflow-x-auto no-scrollbar">
                {promptSuggestions.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(prompt)}
                    className="px-3 py-1.5 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-xs font-medium text-slate-600 dark:text-white/70 hover:text-primary hover:border-primary/40 shrink-0 transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>

              {/* Input Form Bar */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="p-4 border-t border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0f172a] flex items-center gap-3"
              >
                <input
                  type="text"
                  placeholder="Ask Security Copilot an investigative prompt or case query..."
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  className="flex-1 px-4 py-3 text-xs sm:text-sm rounded-2xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-sans"
                />
                <button
                  type="submit"
                  disabled={!inputQuery.trim() || isTyping}
                  className="px-5 py-3 rounded-2xl bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs shadow-lg shadow-primary/20 flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" /> Send
                </button>
              </form>
            </div>
          ) : (
            <CaseSummaryPanel onQuickAction={(action) => handleSendMessage(action)} />
          )}
        </div>
      </div>
    </div>
  );
}
