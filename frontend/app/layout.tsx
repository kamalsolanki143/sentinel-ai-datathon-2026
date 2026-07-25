import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar/Navbar";
import Sidebar from "@/components/Sidebar/Sidebar";
import MainContent from "@/components/Layout/MainContent";
import { ThemeProvider } from "@/components/Theme/ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sentinel AI | Command Center",
  description: "AI-Powered Crime Intelligence & Decision Operating System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen transition-colors duration-300`}
      >
        <ThemeProvider>
          {/* Ambient Background Orbs */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            <div className="orb absolute -top-40 -left-40 w-[500px] h-[500px] bg-primary/20" />
            <div className="orb absolute top-1/2 -right-40 w-[400px] h-[400px] bg-accent/15" style={{ animationDelay: "-7s" }} />
          </div>

          {/* Shell Container */}
          <div className="relative z-10 flex flex-col min-h-screen">
            <Navbar />
            <div className="flex flex-1 overflow-hidden">
              <Sidebar />
              <MainContent>{children}</MainContent>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
