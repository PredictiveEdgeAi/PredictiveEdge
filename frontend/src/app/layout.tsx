import type { Metadata } from "next";
import "../globals.css";

export const metadata: Metadata = {
  title: "PredictiveEdge",
  description: "AI-powered sports analytics platform for performance analysis and statistical modeling",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}

