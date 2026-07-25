"use client";

import React, { useState } from "react";
import { BrainCircuit, Sparkles, X, Send, Bot, ChevronUp, ChevronDown, Minimize2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function FloatingCopilotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputQuery, setInputQuery] = useState("");
  const [messages, setMessages] = useState([
    { id: "1", sender: "assistant", text: "Commander, Security Copilot active. Ask me about Sector 4 getaway risks or syndicate link graphs." }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim()) return;

    const userMsg = { id: Date.now().toString(), sender: "user", text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsTyping(true);

    setTimeout(() => {
      const botResponse = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: `Analysis complete: "${textToSend}" correlates with Marcus Vance's syndicate nodes. ANPR radar pre-positioned on Sector 4 Highway 101.`,
      };
      setMessages((prev) => [...prev, botResponse]);
      setIsTyping(false);
    }, 1200);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="w-80 sm:w-96 rounded-3xl border border-slate-200 dark:border-white/[0.12] bg-white/95 dark:bg-[#0f172a]/95 backdrop-blur-2xl shadow-2xl overflow-hidden flex flex-col h-[450px]"
          >
            {/* Widget Header */}
            <div className="p-4 bg-gradient-to-r from-primary to-accent text-white flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-xl bg-white/20 backdrop-blur-md">
                  <BrainCircuit className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="font-bold text-xs">Security Copilot AI</h4>
                  <span className="text-[9px] font-mono opacity-80 block">LIVE REASONING ENGINE</span>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Messages Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 font-sans text-xs">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex items-start gap-2 ${m.sender === "user" ? "flex-row-reverse" : ""}`}
                >
                  {m.sender === "assistant" && (
                    <div className="h-6 w-6 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="h-3.5 w-3.5" />
                    </div>
                  )}

                  <div
                    className={`p-3 rounded-2xl max-w-[80%] leading-relaxed ${
                      m.sender === "user"
                        ? "bg-primary text-white font-medium"
                        : "bg-slate-100 dark:bg-white/[0.04] text-slate-800 dark:text-white/90 border border-slate-200/80 dark:border-white/[0.06]"
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex items-center gap-2 text-slate-400 font-mono text-[10px]">
                  <Bot className="h-3.5 w-3.5 text-accent animate-spin" />
                  Copilot is analyzing GNN tensor graphs...
                </div>
              )}
            </div>

            {/* Prompt Suggestion Chips */}
            <div className="p-2 border-t border-slate-100 dark:border-white/[0.06] flex items-center gap-1.5 overflow-x-auto no-scrollbar bg-slate-50/50 dark:bg-white/[0.01]">
              {["Getaway Risk", "Bank Threat", "Dossier REP-9041"].map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(prompt)}
                  className="px-2.5 py-1 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-[10px] font-mono text-slate-600 dark:text-white/70 hover:text-primary shrink-0"
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="p-3 border-t border-slate-200/80 dark:border-white/[0.08] flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Ask Copilot a tactical question..."
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                className="flex-1 px-3 py-2 text-xs rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-sans"
              />
              <button
                type="submit"
                className="p-2 rounded-xl bg-primary text-white font-bold hover:bg-primary/90 transition-colors"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          </motion.div>
        ) : (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            className="p-4 rounded-full bg-gradient-to-r from-primary to-accent text-white shadow-2xl flex items-center gap-3 border border-white/20 group"
          >
            <div className="relative">
              <BrainCircuit className="h-6 w-6 group-hover:rotate-12 transition-transform" />
              <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping" />
            </div>
            <span className="font-bold text-xs tracking-tight hidden sm:inline">Ask Copilot AI</span>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
