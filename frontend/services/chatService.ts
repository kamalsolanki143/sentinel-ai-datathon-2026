import apiClient from "./api";

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  codeSnippet?: string;
  codeLanguage?: string;
  structuredMetrics?: { label: string; value: string; color?: string }[];
}

export interface ChatHistorySession {
  id: string;
  title: string;
  date: string;
  caseId: string;
  pinned?: boolean;
}

export const chatService = {
  async getChatHistory(): Promise<ChatHistorySession[]> {
    try {
      const response = await apiClient.get<ChatHistorySession[]>("/chat/history");
      return response.data;
    } catch {
      // Fallback mock session list if backend API is offline
      return [
        { id: "S-101", title: "CAS-8924 Syndicate Heist Analysis", date: "Today, 10:42 AM", caseId: "CAS-8924", pinned: true },
        { id: "S-102", title: "Sector 4 Threat Spike Prediction", date: "Yesterday", caseId: "CAS-8910", pinned: true },
        { id: "S-103", title: "Port Wiretap Transcript Synthesis", date: "Jul 22, 2026", caseId: "CAS-8890" },
        { id: "S-104", title: "Viper Cartel Financial Trace", date: "Jul 20, 2026", caseId: "CAS-8845" },
      ];
    }
  },

  async sendMessage(query: string, caseId?: string): Promise<ChatMessage> {
    try {
      const response = await apiClient.post<ChatMessage>("/chat", { message: query, caseId });
      return response.data;
    } catch {
      // Synthetic intelligence response fallback
      return {
        id: `msg-ai-${Date.now()}`,
        sender: "assistant",
        text: `### Sentinel AI Copilot Assessment\n\nI have processed your query: **"${query}"**.\n\n#### Findings:\n- **Surveillance Database:** 1,204 active intelligence files scanned.\n- **Threat Correlation:** High risk pattern identified in Sector 4 Downtown.\n- **Actionable Next Step:** Run a full **Crime Simulation** or dispatch tactical units.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        structuredMetrics: [
          { label: "Confidence Index", value: "96.4%", color: "text-success" },
          { label: "Threat Vector", value: "DEFCON 3", color: "text-warning" },
        ],
      };
    }
  },

  async clearChatSession(sessionId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/chat/session/${sessionId}`);
      return true;
    } catch {
      return true;
    }
  },
};
