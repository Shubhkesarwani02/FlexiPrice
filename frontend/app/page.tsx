import ProductGrid from '@/components/ProductGrid';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                FlexiPrice Store
              </h1>
              <p className="text-gray-600 mt-1 flex items-center gap-2">
                <span>💰</span>
                <span>Dynamic pricing for smart shopping</span>
              </p>
            </div>
            <Link 
              href="/admin" 
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-md hover:shadow-lg font-medium"
            >
              🔧 Admin
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Page Header */}
        <div className="mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">All Products</h2>
            <p className="text-gray-600">
              Browse our products with <span className="font-semibold text-blue-600">real-time dynamic pricing</span>. 
              Prices update automatically every 30 seconds based on inventory and discounts.
            </p>
          </div>
        </div>

        {/* Product Grid */}
        <ProductGrid />
      </main>
    </div>
  );
}
