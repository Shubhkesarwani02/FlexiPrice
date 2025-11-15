import ProductGrid from '@/components/ProductGrid';
import Link from 'next/link';

export default function Home() {
  return (
    <div>
      {/* Header */}
      <header className="fp-shell-header">
        <div className="fp-shell-header-inner">
          <div className="fp-brand">
            <h1 className="fp-brand-title">
              <span>FlexiPrice</span> Console
            </h1>
            <p className="fp-brand-subtitle">Dynamic Pricing · Experiments · Inventory</p>
          </div>
          <nav className="fp-nav">
            <Link
              href="/"
              className="text-xs tracking-[0.16em] uppercase text-[var(--foreground-muted)] hover:text-[var(--accent)] transition-colors"
            >
              Storefront
            </Link>
            <Link href="/admin" className="fp-pill-button">
              <span className="h-[1px] w-4 bg-[var(--accent-subtle)]" />
              <span>Admin</span>
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="fp-main">
        {/* Page Header */}
        <section className="fp-panel overflow-hidden">
          <div className="fp-panel-header px-6 py-5 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--foreground-muted)]">
                All Products
              </h2>
              <p className="mt-1 text-xs text-[var(--foreground-muted)]">
                Real-time pricing, inventory-aware discounts, and experiment-driven recommendations.
              </p>
            </div>
            <div className="flex gap-6">
              <div className="fp-kpi">
                <span className="fp-kpi-label">Refresh</span>
                <span className="fp-kpi-value">30s</span>
              </div>
              <div className="fp-kpi">
                <span className="fp-kpi-label">Mode</span>
                <span className="fp-kpi-value">Live</span>
              </div>
            </div>
          </div>
          <div className="fp-panel-body px-6 py-5 text-xs">
            Prices are recalculated automatically based on inventory, demand, and
            configured discount rules. Use the Admin console to inspect experiments
            and tweak strategies.
          </div>
        </section>

        {/* Product Grid */}
        <section className="mt-8">
          <ProductGrid />
        </section>
      </main>
    </div>
  );
}
