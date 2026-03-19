# Frontend Implementation Plan - OGOS SaaS Platform

## Overzicht

Next.js frontend met Shadcn/ui componenten voor een clean, professional looking interface. Ondersteuning voor B2B en B2C flows met order management, PDF upload, en voorbereiding voor batch processing.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **UI Library**: Shadcn/ui
- **Styling**: Tailwind CSS
- **Authentication**: Clerk (React SDK)
- **Forms**: React Hook Form + Zod validation
- **File Upload**: react-dropzone of native input
- **API Client**: Fetch API met typed wrappers
- **State Management**: React hooks (useState, useEffect) + React Query (voor server state)
- **Icons**: Lucide React (included met Shadcn)

## Project Structuur

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/
│   │   │   └── page.tsx
│   │   └── sign-up/
│   │       └── page.tsx
│   ├── (b2b)/
│   │   ├── layout.tsx          # B2B layout met navigation
│   │   ├── dashboard/
│   │   │   └── page.tsx        # Dashboard met stats
│   │   ├── organizations/
│   │   │   ├── page.tsx        # List organizations
│   │   │   ├── new/
│   │   │   │   └── page.tsx    # Create organization
│   │   │   └── [id]/
│   │   │       ├── page.tsx    # Organization details
│   │   │       └── edit/
│   │   │           └── page.tsx
│   │   ├── orders/
│   │   │   ├── page.tsx        # List orders
│   │   │   ├── new/
│   │   │   │   └── page.tsx    # Create order (form + upload)
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Order details
│   │   └── subscription/
│   │       └── page.tsx        # Subscription status
│   ├── (b2c)/
│   │   ├── layout.tsx          # B2C layout
│   │   ├── dashboard/
│   │   │   └── page.tsx        # B2C dashboard
│   │   ├── orders/
│   │   │   ├── page.tsx        # List orders
│   │   │   ├── new/
│   │   │   │   └── page.tsx    # Create order
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Order details
│   │   └── credits/
│   │       ├── page.tsx        # Credit balance & purchase
│   │       └── history/
│   │           └── page.tsx    # Credit history
│   ├── api/
│   │   └── proxy/              # API proxy routes (optioneel)
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Landing/redirect page
├── components/
│   ├── ui/                     # Shadcn components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── dialog.tsx
│   │   ├── table.tsx
│   │   ├── tabs.tsx
│   │   ├── badge.tsx
│   │   ├── progress.tsx
│   │   └── ...
│   ├── orders/
│   │   ├── OrderForm.tsx       # Main order form component
│   │   ├── PDFUpload.tsx        # PDF upload component
│   │   ├── OrderPreview.tsx    # Order preview before submit
│   │   ├── OrderList.tsx       # Order list table
│   │   ├── OrderCard.tsx       # Order card component
│   │   └── BatchUpload.tsx     # Batch upload component (future)
│   ├── organizations/
│   │   ├── OrganizationForm.tsx
│   │   ├── OrganizationCard.tsx
│   │   └── SubscriptionStatus.tsx
│   ├── credits/
│   │   ├── CreditBalance.tsx
│   │   ├── PurchaseCredits.tsx
│   │   └── CreditHistory.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Navbar.tsx
│   │   └── Footer.tsx
│   └── providers/
│       ├── ClerkProvider.tsx
│       └── QueryProvider.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts           # API client wrapper
│   │   ├── orders.ts           # Order API functions
│   │   ├── organizations.ts    # Organization API functions
│   │   ├── credits.ts          # Credit API functions
│   │   └── ogos-config.ts     # OGOS config API functions
│   ├── hooks/
│   │   ├── use-auth.ts         # Auth hook
│   │   ├── use-orders.ts       # Orders hook
│   │   └── use-ogos-config.ts  # OGOS config hook
│   ├── utils/
│   │   ├── cn.ts               # Tailwind class merger
│   │   ├── format.ts           # Formatting utilities
│   │   └── validation.ts       # Validation schemas (Zod)
│   └── types/
│       ├── api.ts               # API response types
│       └── orders.ts           # Order types
├── public/
│   └── ...                     # Static assets
├── styles/
│   └── globals.css             # Global styles + Tailwind
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── components.json              # Shadcn config
```

## Core Components

### 1. Order Form (`components/orders/OrderForm.tsx`)

**Functionaliteit:**
- Multi-step form met stepper UI
- Step 1: Select organization (B2B) of skip (B2C)
- Step 2: Order specifications (location, material, quantity, etc.)
- Step 3: Shipping address
- Step 4: PDF upload met preview
- Step 5: Review & submit

**Shadcn Components:**
- `Form` (react-hook-form integration)
- `Input`, `Select`, `Textarea`
- `Button`, `Card`
- `Tabs` of custom stepper
- `Dialog` voor confirmations

**Features:**
- Real-time validation met Zod
- Loading states tijdens API calls
- Error handling met toast notifications
- Form state persistence (localStorage)

### 2. PDF Upload (`components/orders/PDFUpload.tsx`)

**Functionaliteit:**
- Drag & drop zone
- File picker fallback
- PDF preview (thumbnail)
- Validation feedback (file size, format)
- Upload progress indicator
- Multiple file support (voorbereiding batches)

**Shadcn Components:**
- Custom dropzone op basis van `Card`
- `Progress` voor upload status
- `Badge` voor file status
- `Button` voor file picker

**Features:**
- Client-side validation (size, type)
- Preview generation (PDF.js of thumbnail)
- Upload to backend met FormData
- Error handling

### 3. Batch Upload (`components/orders/BatchUpload.tsx`)

**Functionaliteit (Future):**
- Multiple PDF upload
- Bulk specifications
- CSV import voor order data
- Progress tracking per file
- Batch processing queue

**Design:**
- Table view met status per file
- Progress bars per item
- Bulk actions (submit all, cancel all)

## Pages & Routes

### B2B Flow

**Dashboard** (`(b2b)/dashboard/page.tsx`)
- Overview cards: Total orders, Active subscriptions, Today's orders
- Recent orders table
- Quick actions: New order, Manage organizations

**Organizations** (`(b2b)/organizations/page.tsx`)
- List of organizations
- Create/Edit organization form
- Subscription status per org
- OGOS GUID management

**Orders** (`(b2b)/orders/page.tsx`)
- Filterable order list (status, date, org)
- Order cards/table view
- Quick actions: View, Calculate price, Submit

**New Order** (`(b2b)/orders/new/page.tsx`)
- Multi-step order form
- PDF upload
- Price calculation
- Submit to OGOS

### B2C Flow

**Dashboard** (`(b2c)/dashboard/page.tsx`)
- Credit balance display
- Recent orders
- Quick action: New order

**Orders** (`(b2c)/orders/page.tsx`)
- Personal order history
- Order status tracking

**Credits** (`(b2c)/credits/page.tsx`)
- Current balance
- Purchase credits (Stripe integration)
- Credit history

## Design System

### Colors (Tailwind Config)
```js
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  secondary: {
    500: '#64748b',
  },
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
}
```

### Typography
- **Headings**: Inter/Sans-serif, font-semibold/bold
- **Body**: Inter, font-normal
- **Code**: JetBrains Mono

### Spacing & Layout
- Consistent padding: p-4, p-6, p-8
- Card spacing: gap-4, gap-6
- Max width containers: max-w-7xl

### Components Styling
- Cards: Clean white bg, subtle shadow, rounded-lg
- Buttons: Primary (blue), Secondary (gray), Destructive (red)
- Forms: Clean inputs, clear labels, helpful errors
- Tables: Zebra striping, hover effects

## API Integration

### API Client (`lib/api/client.ts`)

```typescript
class APIClient {
  private baseURL: string;
  private getToken: () => Promise<string | null>;

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = await this.getToken();
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options?.headers,
      },
    });
    // Error handling, response parsing
  }

  // Typed methods
  async createOrder(data: CreateOrderRequest): Promise<Order> { ... }
  async uploadPDF(file: File, orderId: string): Promise<void> { ... }
}
```

### React Query Hooks

```typescript
// lib/hooks/use-orders.ts
export function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => api.orders.list(),
  });
}

export function useCreateOrder() {
  return useMutation({
    mutationFn: api.orders.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
    },
  });
}
```

## Key Features

### 1. Order Creation Flow

1. **User selects flow** (B2B/B2C) - auto-detect from user role
2. **Select organization** (B2B only) - dropdown met create option
3. **Fill specifications** - Dynamic form op basis van OGOS config
4. **Enter shipping address** - Address form
5. **Upload PDF** - Drag & drop met preview
6. **Calculate price** - Real-time price calculation
7. **Review & submit** - Confirmation dialog
8. **Track order** - Status updates, OGOS order ID

### 2. PDF Upload & Validation

- **Client-side validation**: File type, size (max 50MB)
- **Preview**: Thumbnail generation
- **Upload progress**: Real-time progress bar
- **Error handling**: Clear error messages
- **Multiple files**: Voorbereiding batch upload

### 3. Batch Processing Preparation

**Architecture:**
- Queue system voor multiple orders
- Progress tracking per order
- Error handling per item
- Retry mechanism

**UI Components:**
- Batch upload component
- Queue table met status
- Bulk actions

## Authentication Flow

### Clerk Integration

```typescript
// app/providers/ClerkProvider.tsx
import { ClerkProvider } from '@clerk/nextjs';

export function Providers({ children }) {
  return (
    <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}>
      {children}
    </ClerkProvider>
  );
}
```

### Protected Routes

```typescript
// middleware.ts
import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  publicRoutes: ['/sign-in', '/sign-up'],
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

## Responsive Design

- **Mobile-first**: Tailwind responsive classes
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Mobile**: Stacked layout, simplified navigation
- **Tablet**: Sidebar navigation, card layout
- **Desktop**: Full sidebar, table views

## Performance Optimizations

- **Code splitting**: Route-based splitting
- **Image optimization**: Next.js Image component
- **Lazy loading**: React.lazy voor heavy components
- **API caching**: React Query caching
- **Form optimization**: Debounced inputs, optimistic updates

## Testing Strategy

- **Unit tests**: Jest + React Testing Library
- **Component tests**: Shadcn components
- **E2E tests**: Playwright (al aanwezig)
- **API mocking**: MSW (Mock Service Worker)

## Deployment

- **Platform**: Vercel (recommended voor Next.js)
- **Environment variables**: Vercel env vars
- **Build**: `next build`
- **Preview deployments**: Automatic op PRs

## Implementation Phases

### Phase 1: Foundation
1. Next.js project setup
2. Shadcn/ui installation
3. Clerk authentication
4. Basic layout & navigation
5. API client setup

### Phase 2: Core Features
1. Order form component
2. PDF upload component
3. Order list & details
4. Organization management (B2B)
5. Credit management (B2C)

### Phase 3: Polish
1. Error handling & loading states
2. Form validation & UX improvements
3. Responsive design
4. Performance optimizations

### Phase 4: Batch Processing
1. Batch upload component
2. Queue management
3. Progress tracking
4. Bulk operations

## Dependencies

```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@clerk/nextjs": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "react-dropzone": "^14.0.0",
    "lucide-react": "^0.300.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

## File Upload Implementation Details

### Single File Upload

```typescript
// components/orders/PDFUpload.tsx
export function PDFUpload({ onFileSelect }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const pdfFile = acceptedFiles[0];
    if (pdfFile) {
      setFile(pdfFile);
      // Generate preview
      generatePreview(pdfFile);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  return (
    <Card {...getRootProps()}>
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop PDF here...</p>
      ) : (
        <p>Drag & drop PDF or click to select</p>
      )}
      {preview && <img src={preview} alt="PDF preview" />}
    </Card>
  );
}
```

### Batch Upload (Future)

```typescript
// components/orders/BatchUpload.tsx
export function BatchUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [queue, setQueue] = useState<OrderQueueItem[]>([]);

  const processBatch = async () => {
    // Upload all files, create orders
    // Track progress per file
  };

  return (
    <div>
      <Dropzone onDrop={handleFiles} multiple />
      <Table>
        {queue.map(item => (
          <OrderQueueRow key={item.id} item={item} />
        ))}
      </Table>
    </div>
  );
}
```

## Next Steps

1. **Initialize Next.js project** met TypeScript
2. **Install Shadcn/ui** en configureer Tailwind
3. **Set up Clerk** authentication
4. **Create basic layout** (Header, Sidebar, Footer)
5. **Build order form** component
6. **Implement PDF upload** met preview
7. **Connect to API** endpoints
8. **Add error handling** en loading states
9. **Polish UI** en responsive design
10. **Prepare batch upload** architecture

