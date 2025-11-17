# FormForge Frontend

This is the frontend application for FormForge, a SaaS platform for AI-powered form building.

## Tech Stack

- **Framework**: Next.js 16.0.1 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS 3.4.1
- **Charts**: Recharts 2.15.0
- **State Management**: React Hooks
- **HTTP Client**: Axios with interceptors
- **Notifications**: Sonner
- **TypeScript**: Full type safety

## Getting Started

### Prerequisites

- Node.js 18+
- Backend server running (see root README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

3. Run development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
frontend/
├── src/
│   ├── app/               # Next.js app router pages
│   │   ├── dashboard/     # Dashboard page
│   │   ├── forms/
│   │   │   ├── new/       # Form creation
│   │   │   └── [id]/      # Form edit & analytics
│   │   └── ...
│   ├── components/        # React components
│   │   └── ui/            # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts         # Axios instance
│   │   └── api-client.ts  # API functions
│   └── types/
│       └── index.ts       # TypeScript types
├── package.json
└── ...
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Deployment

Deploy to Vercel:

1. Connect GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
