import apiClient from "./api";

export interface NetworkNodeData {
  id: string;
  name: string;
  alias?: string;
  type: "kingpin" | "associate" | "front_company" | "vehicle" | "location";
  syndicate: string;
  riskScore: number;
  role: string;
  lastLocation: string;
  warrants: number;
  x: number;
  y: number;
}

export interface NetworkEdgeData {
  id: string;
  source: string;
  target: string;
  type: "financial" | "co_offender" | "command" | "wiretap" | "kinship";
  label: string;
}

export interface NetworkGraphResponse {
  nodes: NetworkNodeData[];
  edges: NetworkEdgeData[];
}

export const networkService = {
  async getNetworkData(): Promise<NetworkGraphResponse> {
    try {
      const response = await apiClient.get<NetworkGraphResponse>("/network");
      return response.data;
    } catch {
      return {
        nodes: [
          { id: "node-1", name: "Marcus Vance", alias: "Viper", type: "kingpin", syndicate: "Viper Syndicate", riskScore: 96, role: "Syndicate Boss", lastLocation: "Sector 4 Downtown", warrants: 4, x: 48, y: 35 },
          { id: "node-2", name: "Viktor Thorne", alias: "The Hammer", type: "kingpin", syndicate: "Apex Cartel", riskScore: 92, role: "Armed Ops Commander", lastLocation: "Sector 2 Harbor", warrants: 6, x: 72, y: 25 },
          { id: "node-3", name: "Darius Black", alias: "Shadow", type: "associate", syndicate: "Viper Syndicate", riskScore: 84, role: "Getaway Lead", lastLocation: "Sector 4 Commercial", warrants: 2, x: 32, y: 45 },
          { id: "node-4", name: "Elena Rostova", alias: "Broker", type: "associate", syndicate: "Viper Syndicate", riskScore: 78, role: "Crypto Launderer", lastLocation: "Sector 1 Financial", warrants: 1, x: 58, y: 60 },
          { id: "node-5", name: "Apex Logistics LLC", type: "front_company", syndicate: "Viper Syndicate", riskScore: 68, role: "Import/Export Shell", lastLocation: "Sector 2 Port Gate 4", warrants: 0, x: 75, y: 58 },
          { id: "node-6", name: "Jax Miller", alias: "Ghost", type: "associate", syndicate: "Apex Cartel", riskScore: 81, role: "Weapons Procurement", lastLocation: "Sector 5 Industrial", warrants: 3, x: 85, y: 40 },
          { id: "node-7", name: "Armored SUV (XYZ-9082)", type: "vehicle", syndicate: "Viper Syndicate", riskScore: 72, role: "Primary Getaway Vehicle", lastLocation: "Highway 101 North", warrants: 1, x: 22, y: 68 },
          { id: "node-8", name: "Kai Vance", alias: "Cipher", type: "associate", syndicate: "Shadow Syndicate", riskScore: 74, role: "Cyber Warfare Lead", lastLocation: "Sector 3 Suburbs", warrants: 1, x: 40, y: 75 },
        ],
        edges: [
          { id: "e-1", source: "node-1", target: "node-3", type: "command", label: "Direct Orders" },
          { id: "e-2", source: "node-1", target: "node-4", type: "financial", label: "$450k Crypto Wire" },
          { id: "e-3", source: "node-4", target: "node-5", type: "financial", label: "Shell Transfer" },
          { id: "e-4", source: "node-1", target: "node-2", type: "co_offender", label: "Joint Heist Planning" },
          { id: "e-5", source: "node-2", target: "node-6", type: "command", label: "Arms Order" },
          { id: "e-6", source: "node-3", target: "node-7", type: "kinship", label: "Driver Match" },
          { id: "e-7", source: "node-1", target: "node-8", type: "wiretap", label: "Phone Call x42" },
        ],
      };
    }
  },
};
