#!/bin/bash
# Setup QuantX Next.js Dashboard

set -e

echo "🎨 Setting up QuantX Dashboard..."
echo ""

# Navigate to dashboard directory
cd "$(dirname "$0")/dashboard"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "Please run this script from the QuantX directory"
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo ""
echo "📁 Creating additional directories..."
mkdir -p components/layout
mkdir -p components/dashboard
mkdir -p components/ui
mkdir -p lib
mkdir -p app/positions
mkdir -p app/orders
mkdir -p app/pnl

echo ""
echo "📝 Creating API client..."
cat > lib/api.ts << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const getHealth = () => api.get('/health');
export const getEngineStatus = () => api.get('/api/v1/engine/status');
export const getPositions = () => api.get('/api/v1/positions');
export const getOrders = () => api.get('/api/v1/orders');
export const getCurrentPnL = () => api.get('/api/v1/pnl/current');
EOF

echo ""
echo "📝 Creating utilities..."
cat > lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(value);
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}
EOF

echo ""
echo "📝 Creating Navbar component..."
cat > components/layout/navbar.tsx << 'EOF'
"use client";

export function Navbar() {
  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary" />
          <span className="text-xl font-bold">QuantX</span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-sm text-muted-foreground">Connected</span>
          </div>
        </div>
      </div>
    </header>
  );
}
EOF

echo ""
echo "📝 Creating Sidebar component..."
cat > components/layout/sidebar.tsx << 'EOF'
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/" },
  { name: "Positions", href: "/positions" },
  { name: "Orders", href: "/orders" },
  { name: "P&L", href: "/pnl" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 border-r bg-background">
      <nav className="flex flex-col gap-1 p-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === item.href
                ? "bg-primary text-primary-foreground"
                : "hover:bg-accent"
            )}
          >
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  );
}
EOF

echo ""
echo "📝 Creating Dashboard Overview..."
cat > components/dashboard/overview.tsx << 'EOF'
"use client";

import { useEffect, useState } from "react";
import { getEngineStatus, getCurrentPnL } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export function DashboardOverview() {
  const [status, setStatus] = useState<any>(null);
  const [pnl, setPnl] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, pnlRes] = await Promise.all([
          getEngineStatus(),
          getCurrentPnL(),
        ]);
        setStatus(statusRes.data);
        setPnl(pnlRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border p-4">
        <p className="text-sm font-medium text-muted-foreground">Engine Status</p>
        <p className="text-2xl font-bold">{status?.state || "Loading..."}</p>
      </div>
      
      <div className="rounded-lg border p-4">
        <p className="text-sm font-medium text-muted-foreground">Total P&L</p>
        <p className="text-2xl font-bold text-green-600">
          {pnl ? formatCurrency(pnl.total_pnl) : "Loading..."}
        </p>
      </div>
      
      <div className="rounded-lg border p-4">
        <p className="text-sm font-medium text-muted-foreground">Positions</p>
        <p className="text-2xl font-bold">0</p>
      </div>
      
      <div className="rounded-lg border p-4">
        <p className="text-sm font-medium text-muted-foreground">Active Orders</p>
        <p className="text-2xl font-bold">0</p>
      </div>
    </div>
  );
}
EOF

echo ""
echo "✅ Dashboard setup complete!"
echo ""
echo "🚀 To start the dashboard:"
echo "   cd dashboard"
echo "   npm run dev"
echo ""
echo "📡 Dashboard will be at: http://localhost:3000"
echo "🔗 Make sure API is running at: http://localhost:8000"
echo ""
