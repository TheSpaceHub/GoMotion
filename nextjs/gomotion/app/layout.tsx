import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
  title: "GoMotion",
  description: "Mobility peak detection in Barcelona.",
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
      <body>{children}
      </body>
    </html>
  );
}
