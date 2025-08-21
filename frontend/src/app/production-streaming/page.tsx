import ProductionDashboard from '@/components/ProductionDashboard';

export default function ProductionStreamingPage() {
  return (
    <div className="container mx-auto">
      <ProductionDashboard />
    </div>
  );
}

export const metadata = {
  title: 'Production DLD Streaming | PropCalc',
  description: 'Real-time Dubai Land Department data streaming and analytics dashboard',
};
