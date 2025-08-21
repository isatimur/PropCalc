'use client';

import { AdminGuard } from '@/components/auth/RoleGuard';
import AdminDashboard from '@/components/dashboards/AdminDashboard';

export default function AdminDashboardPage() {
  return (
    <AdminGuard>
      <AdminDashboard />
    </AdminGuard>
  );
} 