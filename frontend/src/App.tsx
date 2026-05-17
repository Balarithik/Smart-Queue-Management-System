import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './auth/AuthProvider'
import { useAuth } from './auth/useAuth'
import { ProtectedRoute } from './components/ProtectedRoute'
import { SplashScreen } from './components/SplashScreen'
import { About } from './pages/About'
import { Dashboard } from './pages/Dashboard'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { JoinQueue } from './pages/JoinQueue'
import { AdminDashboard } from './pages/AdminDashboard'
import { OrgDashboard } from './pages/OrgDashboard'
import { OrgReports } from './pages/OrgReports'
import { OrgLogin } from './pages/OrgLogin'
import { OrgRegister } from './pages/OrgRegister'
import { QueueCreate } from './pages/QueueCreate'
import { QueueOperatorDashboard } from './pages/QueueOperatorDashboard'
import { QueueQrPage } from './pages/QueueQrPage'
import { Register } from './pages/Register'

function Shell() {
  const { user, logout } = useAuth()
  const showAdminArea = user?.role === 'ADMIN'
  const showOrgArea = user?.role === 'ORGANIZATION' || user?.role === 'ADMIN'

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-6 px-6 py-4">
          <span className="font-semibold text-slate-900">SQMS</span>
          <div className="flex flex-wrap gap-4 text-sm font-medium">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/about"
              className={({ isActive }) =>
                isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
              }
            >
              About
            </NavLink>
            {user ? (
              <>
                <NavLink
                  to="/dashboard"
                  className={({ isActive }) =>
                    isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }
                >
                  Dashboard
                </NavLink>
                {showAdminArea ? (
                  <NavLink
                    to="/admin/dashboard"
                    className={({ isActive }) =>
                      isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                    }
                  >
                    Admin dashboard
                  </NavLink>
                ) : null}
                {showOrgArea ? (
                  <>
                    <NavLink
                      to="/org/dashboard"
                      className={({ isActive }) =>
                        isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                      }
                    >
                      Org dashboard
                    </NavLink>
                    <NavLink
                      to="/org/reports"
                      className={({ isActive }) =>
                        isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                      }
                    >
                      Analytics
                    </NavLink>
                    <NavLink
                      to="/queues/create"
                      className={({ isActive }) =>
                        isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                      }
                    >
                      Create queue
                    </NavLink>
                  </>
                ) : null}
                <button
                  type="button"
                  className="text-slate-600 hover:text-slate-900"
                  onClick={() => logout()}
                >
                  Sign out ({user.username})
                </button>
              </>
            ) : (
              <>
                <NavLink
                  to="/login"
                  className={({ isActive }) =>
                    isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }
                >
                  Sign in
                </NavLink>
                <NavLink
                  to="/register"
                  className={({ isActive }) =>
                    isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }
                >
                  Register
                </NavLink>
                <NavLink
                  to="/org/register"
                  className={({ isActive }) =>
                    isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }
                >
                  Org sign up
                </NavLink>
                <NavLink
                  to="/org/login"
                  className={({ isActive }) =>
                    isActive ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }
                >
                  Org sign in
                </NavLink>
              </>
            )}
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/org/register" element={<OrgRegister />} />
        <Route path="/org/login" element={<OrgLogin />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute roles={['ADMIN']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/org/dashboard"
          element={
            <ProtectedRoute roles={['ORGANIZATION', 'ADMIN']}>
              <OrgDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/org/reports"
          element={
            <ProtectedRoute roles={['ORGANIZATION', 'ADMIN']}>
              <OrgReports />
            </ProtectedRoute>
          }
        />
        <Route
          path="/queues/create"
          element={
            <ProtectedRoute roles={['ORGANIZATION', 'ADMIN']}>
              <QueueCreate />
            </ProtectedRoute>
          }
        />
        <Route
          path="/queues/:publicId/qr"
          element={
            <ProtectedRoute roles={['ORGANIZATION', 'ADMIN']}>
              <QueueQrPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/queues/:publicId/dashboard"
          element={
            <ProtectedRoute roles={['ORGANIZATION', 'ADMIN']}>
              <QueueOperatorDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/join/:publicId" element={<JoinQueue />} />
      </Routes>
    </div>
  )
}

function AppBootstrap() {
  const { loading } = useAuth()
  const [minSplashElapsed, setMinSplashElapsed] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setMinSplashElapsed(true), 1500)
    return () => window.clearTimeout(timer)
  }, [])

  if (loading || !minSplashElapsed) {
    return <SplashScreen />
  }

  return <Shell />
}

export default function App() {
  return (
    <AuthProvider>
      <AppBootstrap />
    </AuthProvider>
  )
}
