import apiClient from "./api";

export interface SimulationParams {
  scenario: string;
  crimeType: string;
  location: string;
  timeHorizon: string;
  weather?: string;
  crowdDensity?: string;
  policeAvailability?: number;
}

export interface SimulationResult {
  simulationId: string;
  mitigationRate: number;
  threatScore: number;
  patrolEfficiency: number;
  projectedIncidents: number;
  hourlyData: { time: string; baseline: number; simulated: number }[];
  sectorData: { sector: string; before: number; after: number }[];
  recommendations: string[];
}

export const simulationService = {
  async runSimulation(params: SimulationParams): Promise<SimulationResult> {
    try {
      const response = await apiClient.post<SimulationResult>("/simulation", params);
      return response.data;
    } catch {
      // Mock simulation calculation fallback
      const mitigation = +(40 + Math.random() * 15).toFixed(1);
      return {
        simulationId: `SIM-${Math.floor(1000 + Math.random() * 9000)}`,
        mitigationRate: mitigation,
        threatScore: Math.floor(75 + Math.random() * 20),
        patrolEfficiency: 94.2,
        projectedIncidents: Math.floor(10 + Math.random() * 8),
        hourlyData: [
          { time: "00:00", baseline: 35, simulated: 18 },
          { time: "04:00", baseline: 22, simulated: 10 },
          { time: "08:00", baseline: 45, simulated: 25 },
          { time: "12:00", baseline: 68, simulated: 32 },
          { time: "16:00", baseline: 92, simulated: 44 },
          { time: "20:00", baseline: 85, simulated: 38 },
          { time: "23:59", baseline: 50, simulated: 22 },
        ],
        sectorData: [
          { sector: "Sec 1 Commercial", before: 78, after: 38 },
          { sector: "Sec 2 Harbor", before: 84, after: 42 },
          { sector: "Sec 3 Suburbs", before: 45, after: 20 },
          { sector: "Sec 4 Downtown", before: 94, after: 48 },
          { sector: "Sec 5 Industrial", before: 65, after: 30 },
        ],
        recommendations: [
          `Deploy 4 Rapid Response Units to ${params.location} by 21:30.`,
          "Activate ANPR Checkpoint #3 along Highway 101 North.",
          "Synchronize automated drone reconnaissance on Sector Port Gate B.",
        ],
      };
    }
  },
};
