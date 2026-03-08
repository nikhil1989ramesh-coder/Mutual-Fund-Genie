import { Inter } from "next/font/google";
import "./globals.css";

// next/font/google handles all Google Fonts loading server-side.
// No @import url() needed in CSS — avoids Turbopack CSS parse errors.
const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata = {
  title: "Mutual Fund Genie Assistant — HDFC Mutual Fund AI",
  description:
    "A RAG-powered chatbot for factual information about the top 5 HDFC Mutual Fund schemes. Powered by Groq + Llama-3.",
  openGraph: {
    title: "Mutual Fund Genie Assistant",
    description: "Ask questions about HDFC Mutual Fund NAV, AUM, exit loads, and more.",
    type: "website",
  },
};

// Proper mobile viewport — prevents layout zoom and ensures fluid rendering
export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
