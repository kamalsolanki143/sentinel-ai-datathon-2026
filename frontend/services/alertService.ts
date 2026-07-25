import apiClient from "./api";

export interface AlertItem {
  id: string;
  title: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  category: string;
  location: string;
  timestamp: string;
  description: string;
  status: "Active" | "Acknowledged" | "Resolved";
  unitsDispatched: number;
}

export const alertService = {
  async getAlerts(): Promise<AlertItem[]> {
    try {
      const response = await apiClient.get<AlertItem[]>("/alerts");
      return response.data;
    } catch {
      return [
        {
          id: "ALT-9901",
          title: "Armed Robbery Alarm - First National Vault",
          priority: "Critical",
          category: "Armed Intrusion",
          location: "Sector 4 - Downtown Commercial",
          timestamp: "2m ago",
          description: "Silent vault alarm tripped. ANPR scan detected getaway vehicle XYZ-9082 leaving northbound corridor.",
          status: "Active",
          unitsDispatched: 4,
        },
        {
          id: "ALT-9902",
          title: "Suspicious Vessel Gathering & Contraband Transfer",
          priority: "High",
          category: "Narcotics Trafficking",
          location: "Sector 2 - Port Terminal 3",
          timestamp: "18m ago",
          description: "Thermal drone feed spotted unlisted speedboat docking near Apex Logistics cargo container.",
          status: "Active",
          unitsDispatched: 2,
        },
        {
          id: "ALT-9903",
          title: "ANPR License Plate Hit - Wanted Fugitive",
          priority: "Medium",
          category: "Surveillance Hit",
          location: "Sector 1 - Highway 101 Toll",
          timestamp: "45m ago",
          description: "Black SUV matched vehicle registered to Marcus Vance. Heading towards Sector 4.",
          status: "Acknowledged",
          unitsDispatched: 1,
        },
        {
          id: "ALT-9904",
          title: "Cyber Signal Jamming Anomaly Detected",
          priority: "Medium",
          category: "Cyber Anomaly",
          location: "Sector 3 - Suburbs Tower #12",
          timestamp: "1h ago",
          description: "Encrypted frequency pulse overriding police radio band for 45 seconds.",
          status: "Resolved",
          unitsDispatched: 0,
        },
      ];
    }
  },

  async acknowledgeAlert(id: string): Promise<boolean> {
    try {
      await apiClient.post(`/alerts/${id}/acknowledge`);
      return true;
    } catch {
      return true;
    }
  },
};
