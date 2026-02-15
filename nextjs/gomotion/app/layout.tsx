import type { Metadata } from "next";

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
        <meta
          name="google-site-verification"
          content="VNDJD0v5PLKh7KZ7S64qefbJgo8WX-arE4jD5-fTru0"
        />
        <link rel="stylesheet" href="/mobile.css" media="(max-width: 768px)" />
        <link rel="stylesheet" href="/globals.css" media="(min-width: 769px)" />
      </head>
      <body>{children}</body>
    </html>
  );
}
