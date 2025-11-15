# FlexiPrice Frontend

Next.js storefront with dynamic pricing visualization and admin dashboard.

## Features

- **Product Grid**: Browse products with real-time computed prices
- **Product Details**: View individual product details with active discounts
- **Admin Dashboard**: Manage products and discounts (token-protected)
- **SWR Integration**: Real-time data fetching and caching
- **Responsive Design**: Mobile-first Tailwind CSS styling

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ADMIN_TOKEN=your-secret-admin-token-here
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Pages

### Home (`/`)
- Product grid with computed prices
- Real-time price updates via SWR
- Visual discount indicators
- Stock status for each product

### Product Detail (`/product/[sku]`)
- Detailed product information
- Active discount breakdown
- Inventory status
- Price comparison (base vs. final)

### Admin Dashboard (`/admin`)
- Token-based authentication
- Product management table
- Discount management table
- Real-time data updates

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Home page with product grid
│   ├── product/[sku]/
│   │   └── page.tsx          # Product detail page
│   ├── admin/
│   │   └── page.tsx          # Admin dashboard
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── ProductCard.tsx       # Product card component
│   └── ProductGrid.tsx       # Product grid with SWR
├── lib/
│   └── api.ts                # API client and endpoints
├── types/
│   └── index.ts              # TypeScript interfaces
└── public/                   # Static assets
```

## API Integration

The frontend integrates with the FlexiPrice backend API:

- `GET /products` - List all products
- `GET /products/{sku}` - Get product details
- `GET /inventory/{sku}` - Get inventory status
- `GET /discounts/active/{sku}` - Get active discounts
- `GET /discounts` - List all discounts (admin)

## Authentication

The admin dashboard uses simple token-based authentication:

1. Set `ADMIN_TOKEN` in `.env.local`
2. Navigate to `/admin`
3. Enter the token to access the dashboard
4. Token is stored in localStorage for persistence

**Note**: This is a basic implementation. For production, use proper authentication (NextAuth.js, Auth0, etc.)

## Deployment (Vercel)

### Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Manual Deployment

1. Push your code to GitHub

2. Import project in Vercel dashboard

3. Configure environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL
   - `ADMIN_TOKEN`: Admin authentication token

4. Deploy!

### Environment Variables (Production)

Make sure to set these in your Vercel project settings:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
ADMIN_TOKEN=your-secure-production-token
```

## Technologies

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe code
- **Tailwind CSS**: Utility-first styling
- **SWR**: Data fetching and caching
- **Axios**: HTTP client

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
