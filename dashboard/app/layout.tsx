import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "QuantX Dashboard",
    description: "AI-Powered Algorithmic Trading Platform",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="flex h-screen bg-background">
                    {/* Sidebar */}
                    <Sidebar />

                    {/* Main content */}
                    <div className="flex flex-1 flex-col overflow-hidden">
                        {/* Navbar */}
                        <Navbar />

                        {/* Page content */}
                        <main className="flex-1 overflow-y-auto p-6">
                            {children}
                        </main>
                    </div>
                </div>
            </body>
        </html>
    );
}
