import { DashboardOverview } from "@/components/dashboard/overview";

export default function Home() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-muted-foreground">
                    Welcome to QuantX - AI-Powered Algorithmic Trading
                </p>
            </div>

            <DashboardOverview />
        </div>
    );
}
