import { NavLink, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './auth/AuthProvider'
import { useAuth } from './auth/useAuth'
import { ProtectedRoute } from './components/ProtectedRoute'
import { About } from './pages/About'
import { Dashboard } from './pages/Dashboard'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { Register } from './pages/Register'

function Shell() {
  const { user, logout } = useAuth()

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
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}
