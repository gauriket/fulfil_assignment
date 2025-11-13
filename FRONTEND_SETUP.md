# Frontend Setup & Documentation

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see BACKEND_SETUP.md)
- Code editor (VS Code recommended)

### Installation & Running

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Run development server
npm run dev

# Frontend will be available at http://localhost:3000
```

---

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout component
│   ├── page.tsx             # CSV upload page (home)
│   ├── globals.css          # Global styles
│   ├── products/
│   │   └── page.tsx         # Product management page
│   └── webhooks/
│       └── page.tsx         # Webhook management page
├── public/                  # Static assets (images, icons)
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── next.config.ts           # Next.js configuration
├── postcss.config.mjs       # Tailwind CSS configuration
├── eslint.config.mjs        # ESLint configuration
└── README.md                # Frontend-specific readme
```

---

## Technology Stack

### Core Framework

- **Next.js 14+**: React-based framework with SSR, routing, and optimization
- **React 18+**: UI library with hooks
- **TypeScript**: Type-safe JavaScript

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **PostCSS**: CSS processing tool

### HTTP Client

- **Axios**: Promise-based HTTP client for API calls

### Build Tools

- **Webpack**: Module bundler (via Next.js)
- **Babel**: JavaScript transpiler (via Next.js)
- **ESLint**: Code quality tool

---

## Pages

### 1. Home / Upload Page (`app/page.tsx`)

**URL:** `/`

**Purpose:** Allow users to upload CSV files for bulk product import

#### Features

- **File Selection**: Browse and select CSV files
- **Upload Progress**: Real-time progress bar (0-50% upload, 50-100% processing)
- **Status Messages**: User-friendly feedback
- **Job Tracking**: Display job ID
- **Error Handling**: Show error messages with retry option
- **Navigation**: Links to products and webhooks pages

#### State Management

```typescript
const [status, setStatus] = useState("");        // Status message
const [loading, setLoading] = useState(false);   // Loading state
const [progress, setProgress] = useState(0);     // Progress 0-100
const [jobId, setJobId] = useState<string | null>(null);
const [uploadError, setUploadError] = useState(false);
```

#### API Integration

**Upload:**
```typescript
POST /upload
Content-Type: multipart/form-data
file: [CSV file]

Response: { job_id: "uuid-string" }
```

**Poll Status:**
```typescript
GET /job_status/{job_id}

Response: {
  status: "processing|completed|unknown",
  progress: 0-100,
  message: "Status message"
}
```

#### CSV Format Expected

```csv
sku,name,description,price
PROD001,Product Name,Description,29.99
PROD002,Another Product,Description,49.99
```

---

### 2. Products Page (`app/products/page.tsx`)

**URL:** `/products`

**Purpose:** Manage products - view, search, create, update, delete

#### Features

- **Product List**: Display all products with pagination
- **Search & Filter**: Filter by SKU, name, description, active status
- **Pagination**: Navigate through products (limit 20 per page)
- **Create Product**: Form to add new product
- **Update Product**: Edit existing product details
- **Delete Product**: Remove single or multiple products
- **Bulk Operations**: Select multiple products
- **Back Button**: Return to upload page

#### State Management

```typescript
const [products, setProducts] = useState([]);
const [filters, setFilters] = useState({
  sku: "",
  name: "",
  description: "",
  active: undefined
});
const [loading, setLoading] = useState(false);
const [error, setError] = useState("");
```

#### API Integration

**List Products:**
```typescript
GET /products?sku=&name=&description=&active=&skip=0&limit=20

Response: [
  {
    sku: "PROD001",
    name: "Product Name",
    description: "Description",
    price: 29.99,
    active: true
  }
]
```

**Create Product:**
```typescript
POST /products
{
  sku: "PROD003",
  name: "New Product",
  description: "Description",
  price: 99.99,
  active: true
}
```

**Update Product:**
```typescript
PUT /products/{sku}
{
  name: "Updated Name",
  price: 109.99
}
```

**Delete Product:**
```typescript
DELETE /products/{sku}
DELETE /products (delete all)
```

---

### 3. Webhooks Page (`app/webhooks/page.tsx`)

**URL:** `/webhooks`

**Purpose:** Configure webhooks for event notifications

#### Features

- **Webhook List**: Display all configured webhooks
- **Create Webhook**: Form to add new webhook endpoint
- **Update Webhook**: Edit webhook configuration
- **Delete Webhook**: Remove webhook
- **Test Webhook**: Send test payload to verify endpoint
- **Enable/Disable**: Toggle webhook status
- **Event Types**: Select which events to subscribe to
- **Back Button**: Return to upload page

#### State Management

```typescript
const [webhooks, setWebhooks] = useState([]);
const [loading, setLoading] = useState(false);
const [error, setError] = useState("");
const [testResult, setTestResult] = useState(null);
```

#### API Integration

**List Webhooks:**
```typescript
GET /webhooks

Response: [
  {
    id: 1,
    url: "https://example.com/webhook",
    event_types: ["product.imported"],
    active: true
  }
]
```

**Create Webhook:**
```typescript
POST /webhooks
{
  url: "https://example.com/webhook",
  event_types: ["product.imported", "product.updated"],
  active: true
}
```

**Update Webhook:**
```typescript
PUT /webhooks/{id}
{
  active: false
}
```

**Test Webhook:**
```typescript
POST /webhooks/{id}/test

Response: {
  status_code: 200,
  response_time_ms: 145.32,
  response_body: "OK"
}
```

**Delete Webhook:**
```typescript
DELETE /webhooks/{id}
```

---

## Component Structure

### Layout Component (`layout.tsx`)

Root layout wrapping all pages:

```typescript
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="...">
        {children}
      </body>
    </html>
  );
}
```

### Page Components

Each page is a client component:

```typescript
"use client";  // Enable client-side features

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function UploadPage() {
  // State and logic
  // JSX
}
```

---

## Environment Variables

### Configuration File

Create `.env.local` in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Variable Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API base URL |

**Note:** Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

### Development vs Production

**Development (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production (Vercel Environment Variables)**
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## Styling with Tailwind CSS

### Tailwind Setup

Tailwind CSS is pre-configured with:
- PostCSS for CSS processing
- Content paths configured in `postcss.config.mjs`
- Global styles in `app/globals.css`

### Common Classes Used

```typescript
// Layout
className="flex flex-col items-center justify-center"
className="w-full max-w-md"

// Spacing
className="p-6 mb-4 mt-4"
className="gap-2"

// Colors & Styling
className="bg-blue-600 hover:bg-blue-700"
className="text-white font-medium"
className="rounded-lg shadow"

// Responsive
className="px-4 md:px-8"
className="grid grid-cols-1 md:grid-cols-2"
```

### Custom Styling

Global styles in `app/globals.css`:

```css
/* Add custom styles here */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
}
```

---

## API Integration Pattern

### Setting API URL

```typescript
let API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  API_URL = "http://localhost:8000";  // Fallback
}
```

### Making API Calls with Axios

```typescript
import axios from "axios";

// POST request
const response = await axios.post(`${API_URL}/upload`, formData, {
  headers: { "Content-Type": "multipart/form-data" },
  onUploadProgress: (event) => {
    const percent = Math.round((event.loaded / event.total) * 100);
    setProgress(percent);
  },
});

// GET request
const { data } = await axios.get(`${API_URL}/products?limit=20`);

// PUT request
await axios.put(`${API_URL}/products/${sku}`, { name: "Updated" });

// DELETE request
await axios.delete(`${API_URL}/products/${sku}`);
```

### Using Fetch API

```typescript
// GET request
const response = await fetch(`${API_URL}/job_status/${jobId}`);
const data = await response.json();

// POST request
const response = await fetch(`${API_URL}/webhooks`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url, event_types, active })
});
```

### Error Handling

```typescript
try {
  const response = await axios.post(`${API_URL}/upload`, formData);
} catch (error: any) {
  const message = error.response?.data?.detail || "Unknown error";
  setError(message);
  console.error(error);
}
```

---

## Running & Building

### Development Server

```bash
npm run dev

# With custom port
npm run dev -- -p 3001
```

### Build for Production

```bash
npm run build

# Build output in .next/ directory
```

### Start Production Server

```bash
npm run build
npm run start

# Runs on port 3000 by default
```

### Linting & Code Quality

```bash
# Run ESLint
npm run lint

# Fix linting issues
npx eslint --fix .
```

---

## Deployment

### Deploying to Vercel (Recommended)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Select GitHub repository
5. Configure environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend URL
6. Deploy

Vercel handles:
- Automatic builds on push
- Preview deployments for PRs
- Serverless functions
- CDN distribution

### Manual Deployment to Server

```bash
# Build application
npm run build

# Copy .next/ directory and public/ to server
# Install production dependencies only
npm install --production

# Start with Node.js
npm run start
```

---

## Troubleshooting

### CORS Errors

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**

1. Check backend CORS configuration includes frontend URL
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Ensure backend is running and accessible
4. Check browser console for exact error

### API URL Issues

**Error:**
```
404 Not Found
```

**Solution:**

Check `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # Must include protocol
```

### Build Errors

**Error:**
```
Error: ENOENT: no such file or directory
```

**Solutions:**

1. Install dependencies: `npm install`
2. Clear cache: `rm -rf .next node_modules`
3. Reinstall: `npm install`

### Module Import Errors

**Error:**
```
Module not found: Can't resolve 'axios'
```

**Solution:**

```bash
npm install axios
```

### Port Already in Use

**Error:**
```
Port 3000 is already in use
```

**Solution:**

Use different port:
```bash
npm run dev -- -p 3001
```

---

## Performance Optimization

### Image Optimization

Use Next.js Image component:

```typescript
import Image from "next/image";

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority
/>
```

### Code Splitting

Routes are automatically code-split by Next.js:

```typescript
import dynamic from "next/dynamic";

const ProductsPage = dynamic(() => import("./products"));
```

### Caching

- Static generation for pages that don't change frequently
- Incremental Static Regeneration (ISR) for periodic updates
- Client-side caching with React Query or SWR

### Lazy Loading

```typescript
import { useState, useEffect } from "react";

const [data, setData] = useState(null);

useEffect(() => {
  fetchProducts();
}, []);

// Only fetch when needed
```

---

## Best Practices

### Component Organization

```typescript
// 1. Imports
import { useState } from "react";
import axios from "axios";

// 2. Component definition
export default function MyComponent() {
  // 3. State
  const [state, setState] = useState("");

  // 4. Effects
  useEffect(() => {}, []);

  // 5. Event handlers
  const handleClick = () => {};

  // 6. JSX
  return <div>...</div>;
}
```

### Error Boundaries

Wrap error-prone sections:

```typescript
try {
  // API call
} catch (error) {
  setError(error.message);
  // Show user-friendly message
}
```

### Type Safety

Use TypeScript interfaces:

```typescript
interface Product {
  sku: string;
  name: string;
  price: number;
  active: boolean;
}

const products: Product[] = [];
```

---

## Environment-Specific Configuration

### Different APIs per Environment

```typescript
const getApiUrl = (): string => {
  if (typeof window === "undefined") {
    // Server-side
    return process.env.API_URL_INTERNAL || "http://localhost:8000";
  }
  // Client-side
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};
```

---

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Axios Documentation](https://axios-http.com/docs)

