# Next.js Dashboard Setup Guide

## 🚀 Quick Start

We'll create a modern Next.js 14 dashboard with TypeScript and TailwindCSS.

### Step 1: Create Next.js Project

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX

# Create Next.js app in dashboard directory
npx create-next-app@latest dashboard --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Answer prompts**:
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ `src/` directory: No
- ✅ App Router: Yes
- ✅ Import alias: @/* (default)

### Step 2: Install Dependencies

```bash
cd dashboard

# Install Shadcn/UI (component library)
npx shadcn-ui@latest init

# Install additional packages
npm install axios swr recharts lucide-react date-fns
```

### Step 3: Start Dev Server

```bash
npm run dev
```

Dashboard will be at: **http://localhost:3000**

---

## 📁 Project Structure

After setup, you'll have:

```
dashboard/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (dashboard)
│   ├── positions/
│   │   └── page.tsx        # Positions page
│   ├── orders/
│   │   └── page.tsx        # Orders page
│   └── pnl/
│       └── page.tsx        # P&L page
├── components/
│   ├── ui/                 # Shadcn components
│   ├── dashboard/
│   │   ├── overview.tsx
│   │   ├── positions-table.tsx
│   │   └── pnl-chart.tsx
│   ├── layout/
│   │   ├── navbar.tsx
│   │   └── sidebar.tsx
│   └── ...
├── lib/
│   ├── api.ts              # API client
│   └── utils.ts
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

---

## 🎨 What We'll Build

### Pages
1. **Dashboard** (/) - Overview with metrics
2. **Positions** (/positions) - Position management
3. **Orders** (/orders) - Order history & placement
4. **P&L** (/pnl) - Performance analytics

### Features
- Real-time updates via WebSocket
- Beautiful dark mode
- Responsive design
- Interactive charts
- Live data from FastAPI backend

---

## 🔗 API Integration

The dashboard will connect to your running API at:
- **Base URL**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws/live

---

## ⏭️ Next Steps

After running the setup commands above, I'll help you:
1. Create the layout components
2. Build the API client
3. Create dashboard pages
4. Add real-time charts

Ready to run the setup commands?
