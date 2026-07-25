import apiClient from "./api";

export interface ReportItem {
  id: string;
  title: string;
  caseId: string;
  crimeType: string;
  location: string;
  officer: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  status: "Published" | "Under Review" | "Draft" | "Archived";
  createdDate: string;
  summary: string;
}

export const reportService = {
  async getReports(): Promise<ReportItem[]> {
    try {
      const response = await apiClient.get<ReportItem[]>("/reports");
      return response.data;
    } catch {
      return [
        {
          id: "REP-9041",
          title: "Downtown Commercial Bank Vault Intrusion & Explosive Heist",
          caseId: "CAS-8924",
          crimeType: "Armed Robbery",
          location: "Sector 4 - Downtown",
          officer: "Capt. Kamal Solanki",
          priority: "Critical",
          status: "Published",
          createdDate: "2026-07-24",
          summary: "High-priority intelligence synthesis regarding the Sector 4 commercial bank breach. Multi-modal surveillance analysis identifies Marcus 'Viper' Vance as lead suspect.",
        },
        {
          id: "REP-9040",
          title: "Port Harbor Narcotics Cargo Intercept & Wiretap Synthesis",
          caseId: "CAS-8923",
          crimeType: "Gang Activity",
          location: "Sector 2 - Port",
          officer: "Det. Maya Lin",
          priority: "High",
          status: "Under Review",
          createdDate: "2026-07-23",
          summary: "Cross-referenced encrypted comms and container manifest logs revealing illegal contraband distribution networks linked to Apex Logistics LLC.",
        },
        {
          id: "REP-9038",
          title: "Suburbs Coordinated Vehicle Theft Ring Investigation",
          caseId: "CAS-8921",
          crimeType: "Vehicle Theft",
          location: "Sector 3 - Suburbs",
          officer: "Off. Marcus Brody",
          priority: "Medium",
          status: "Published",
          createdDate: "2026-07-22",
          summary: "ANPR camera logs and chop-shop spatial heatmaps indicating systematic vehicle targeting across Sector 3 arterial roads.",
        },
        {
          id: "REP-9035",
          title: "Sector 1 Financial District Ransomware & Crypto Breach",
          caseId: "CAS-8918",
          crimeType: "Cybercrime",
          location: "Sector 1 - Commercial",
          officer: "Agent Krrish Yaduka",
          priority: "High",
          status: "Draft",
          createdDate: "2026-07-21",
          summary: "Cyber forensics report detailing ransomware payload signatures and crypto wallet trace originating from Shadow Syndicate servers.",
        },
      ];
    }
  },

  async createReport(reportData: Partial<ReportItem>): Promise<ReportItem> {
    try {
      const response = await apiClient.post<ReportItem>("/reports", reportData);
      return response.data;
    } catch {
      return {
        id: `REP-${Math.floor(1000 + Math.random() * 9000)}`,
        title: reportData.title || "Automated AI Intelligence Report",
        caseId: reportData.caseId || "CAS-8924",
        crimeType: reportData.crimeType || "Armed Robbery",
        location: reportData.location || "Sector 4 - Downtown",
        officer: reportData.officer || "Agent Sarah Connor",
        priority: reportData.priority || "Critical",
        status: "Published",
        createdDate: new Date().toISOString().split("T")[0],
        summary: reportData.summary || "Synthesized intelligence report combining AI Copilot findings.",
      };
    }
  },

  async deleteReport(id: string): Promise<boolean> {
    try {
      await apiClient.delete(`/reports/${id}`);
      return true;
    } catch {
      return true;
    }
  },
};
