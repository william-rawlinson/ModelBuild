import { Link, useLocation } from "react-router-dom";
import Container from "./ui/Container";

function NavTab({ to, isActive, children }) {
  return (
    <Link
      to={to}
      className={[
        "px-5 py-3 text-lg font-semibold rounded-xl transition-colors",
        isActive
          ? "bg-white text-slate-900 shadow-sm border"
          : "text-slate-600 hover:text-slate-900 hover:bg-white/60",
      ].join(" ")}
    >
      {children}
    </Link>
  );
}

export default function Layout({ children }) {
  const location = useLocation();

  const navItems = [
    { name: "Specify Model", path: "/" },
    { name: "View Model", path: "/view_model" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top bar */}
      <header className="border-b bg-white">
        <Container className="py-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="space-y-1">
              <div className="text-2xl md:text-3xl font-bold text-slate-900">
                Model Builder
              </div>
              <div className="text-sm md:text-base text-slate-500">
                Alpha v1.0
              </div>
            </div>

            {/* Tabs */}
            <nav className="rounded-2xl bg-slate-100 p-2 flex flex-wrap gap-2">
              {navItems.map((item) => (
                <NavTab
                  key={item.path}
                  to={item.path}
                  isActive={location.pathname === item.path}
                >
                  {item.name}
                </NavTab>
              ))}
            </nav>
          </div>
        </Container>
      </header>

      {/* Page content */}
      <main className="flex-1 py-8">
        <Container>
          {/* IMPORTANT: no global "content card" wrapper here.
              Each page/component (like ModelDesignForm) can decide if it uses Card. */}
          {children}
        </Container>
      </main>
    </div>
  );
}
