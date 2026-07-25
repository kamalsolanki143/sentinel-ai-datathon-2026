import { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Sentinel AI — Crime Intelligence & Decision Operating System",
    short_name: "Sentinel AI",
    description: "Enterprise AI Powered Crime Intelligence, Network Graph & Decision Operating System",
    start_url: "/",
    display: "standalone",
    background_color: "#050816",
    theme_color: "#3b82f6",
    icons: [
      {
        src: "/favicon.ico",
        sizes: "any",
        type: "image/x-icon",
      },
    ],
  };
}
