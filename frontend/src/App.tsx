import { NavLink, Route, Routes } from 'react-router-dom'
import { About } from './pages/About'
import { Home } from './pages/Home'

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
          <span className="font-semibold text-slate-900">SQMS</span>
          <div className="flex gap-4 text-sm font-medium">
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
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </div>
  )
}

export default App
