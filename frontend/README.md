# FormForge Frontend

This is the frontend application for FormForge, a comprehensive SaaS platform for AI-powered form building with advanced features including conversational interfaces, A/B testing, predictive analytics, and enterprise-grade collaboration tools.

## Tech Stack

- **Framework**: Next.js 16.0.1 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS 3.4.1
- **Charts**: Recharts 2.15.0
- **State Management**: React Hooks + Context API
- **HTTP Client**: Axios with interceptors and retry logic
- **Notifications**: Sonner for toast notifications
- **TypeScript**: Full type safety with strict mode
- **PWA**: Service Workers, Web App Manifest
- **Real-time**: WebSockets for live updates
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Code splitting, lazy loading, optimization

## Features

### Core Features
- **AI Form Generation**: Natural language to form conversion
- **Visual Form Editor**: Drag & drop, inline editing, 15+ field types
- **Analytics Dashboard**: Real-time charts and insights
- **Multi-format Embeds**: iFrame, JavaScript, React components

### Advanced Features
- **Conversational Forms**: Chatbot-style form filling
- **A/B Testing**: Form variant testing and optimization
- **Progressive Web App**: Offline-capable with service workers
- **Real-time Collaboration**: Team editing and permissions
- **Predictive Analytics**: AI-powered lead scoring
- **Multi-step Forms**: Wizard-style form experiences
- **Theme Customization**: Brand-aligned form styling
- **Internationalization**: Multi-language support
- **Mobile Optimization**: Responsive design with touch interactions

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
│   ├── app/                    # Next.js app router pages
│   │   ├── (auth)/            # Authentication pages
│   │   ├── dashboard/         # Dashboard and analytics
│   │   ├── forms/             # Form management
│   │   │   ├── new/           # AI form creation
│   │   │   ├── [id]/          # Form editor & analytics
│   │   │   ├── templates/     # Template gallery
│   │   │   └── embed/         # Public form renderer
│   │   ├── teams/             # Team collaboration
│   │   ├── integrations/      # Integration marketplace
│   │   ├── settings/          # User & app settings
│   │   └── api/               # API routes (if needed)
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── forms/             # Form-specific components
│   │   ├── dashboard/         # Dashboard components
│   │   ├── analytics/         # Analytics & charts
│   │   ├── conversational/    # Chatbot components
│   │   ├── collaboration/     # Team features
│   │   └── integrations/      # Integration components
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts         # Authentication hooks
│   │   ├── useForms.ts        # Form management hooks
│   │   ├── useAnalytics.ts    # Analytics hooks
│   │   └── useRealtime.ts     # WebSocket hooks
│   ├── lib/                   # Utilities and configurations
│   │   ├── api.ts             # Axios instance & interceptors
│   │   ├── api-client.ts      # API functions
│   │   ├── utils.ts           # General utilities
│   │   ├── validations.ts     # Form validation schemas
│   │   └── constants.ts       # App constants
│   ├── types/                 # TypeScript type definitions
│   │   ├── index.ts           # Main types
│   │   ├── forms.ts           # Form-related types
│   │   ├── analytics.ts       # Analytics types
│   │   └── api.ts             # API response types
│   ├── contexts/              # React contexts
│   │   ├── AuthContext.tsx    # Authentication context
│   │   └── ThemeContext.tsx   # Theme context
│   └── styles/                # Global styles
├── public/                    # Static assets
│   ├── embed.js              # Form embedding script
│   ├── manifest.json         # PWA manifest
│   ├── sw.js                 # Service worker
│   └── icons/                # App icons
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── eslint.config.mjs
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build optimized production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint for code quality
- `npm run type-check` - Run TypeScript type checking
- `npm run test` - Run test suite (if implemented)
- `npm run analyze` - Analyze bundle size

## Development Guidelines

### Code Style
- Use TypeScript for all new components
- Follow React best practices and hooks
- Use shadcn/ui components for consistency
- Implement proper error boundaries
- Add loading states for async operations

### Performance
- Use React.memo for expensive components
- Implement code splitting for routes
- Optimize images and assets
- Use React.lazy for dynamic imports
- Monitor bundle size with build analysis

### Accessibility
- Use semantic HTML elements
- Add proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers
- Maintain WCAG 2.1 AA compliance

## Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_PWA_ENABLED=true
```

## Deployment

### Vercel (Recommended)
1. Connect GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. Deploy automatically on push

### Other Platforms
- **Netlify**: Connect repo, set build command to `npm run build`
- **Railway**: Use Nixpacks or custom Dockerfile
- **Docker**: Use provided Dockerfile for containerized deployment

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test components across different screen sizes
4. Ensure accessibility compliance
5. Update documentation as needed

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
- [React Best Practices](https://react.dev/learn)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
