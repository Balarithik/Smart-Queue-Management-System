import { Suspense, lazy, type ComponentType } from "react";
import { createBrowserRouter } from "react-router-dom";

const LoginPage = lazy(() => import("../features/auth/LoginPage").then((m) => ({ default: m.LoginPage })));
const JoinQueuePage = lazy(() => import("../features/queue/JoinQueuePage").then((m) => ({ default: m.JoinQueuePage })));
const LiveQueuePage = lazy(() => import("../features/queue/LiveQueuePage").then((m) => ({ default: m.LiveQueuePage })));
const OrgDashboardPage = lazy(() =>
  import("../features/org/OrgDashboardPage").then((m) => ({ default: m.OrgDashboardPage }))
);
const AnalyticsPage = lazy(() => import("../features/analytics/AnalyticsPage").then((m) => ({ default: m.AnalyticsPage })));
const QRScannerPage = lazy(() => import("../features/qr/QRScannerPage").then((m) => ({ default: m.QRScannerPage })));
const NotificationSettingsPage = lazy(() =>
  import("../features/notifications/NotificationSettingsPage").then((m) => ({ default: m.NotificationSettingsPage }))
);

const RouteLoader = () => <div className="p-6 text-slate-700">Loading...</div>;
const withSuspense = (Component: ComponentType) => (
  <Suspense fallback={<RouteLoader />}>
    <Component />
  </Suspense>
);

export const router = createBrowserRouter([
  { path: "/", element: withSuspense(LoginPage) },
  { path: "/join", element: withSuspense(JoinQueuePage) },
  { path: "/live", element: withSuspense(LiveQueuePage) },
  { path: "/org", element: withSuspense(OrgDashboardPage) },
  { path: "/analytics", element: withSuspense(AnalyticsPage) },
  { path: "/scan", element: withSuspense(QRScannerPage) },
  { path: "/notifications", element: withSuspense(NotificationSettingsPage) }
]);
