import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GoMotion",
  description:
    "Analyze and predict traffic trends, event impacts, and mobility statistics in Barcelona.",
  keywords: ["Barcelona", "GoMotion", "mobility", "prediction", "dashboard"],
  openGraph: {
    title: "GoMotion",
    description: "Mobility peak detection in Barcelona.",
    url: "https://go-motion.vercel.app",
    siteName: "GoMotion",
    images: [
      {
        url: "https://go-motion.vercel.app/GoMotionPreview.png",
        width: 681,
        height: 562,
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>GoMotion</title>
      </head>
      <body>{children}</body>
    </html>
  );
}
