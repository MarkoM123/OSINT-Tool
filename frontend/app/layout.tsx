import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EIP Dashboard",
  description: "Exposure Intelligence Platform dashboard for assessment insights.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
