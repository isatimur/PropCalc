import type { Metadata } from "next";
import { Inter } from "next/font/google";
import * as Sentry from '@sentry/nextjs';
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// Add generateMetadata function to include Sentry trace data
export function generateMetadata(): Metadata {
  return {
    title: "Vantage AI - Trust Protocol for Real Estate",
    description: "From Speculation to Science - Transform real estate investment decisions with data-driven insights",
  };
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body className={`${inter.className} bg-gray-50`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
