import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { useAuthStore } from "@/stores/authStore";
import { ImageIcon, LogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <ImageIcon className="h-5 w-5 text-primary" />
          <span>Image Pipeline</span>
        </Link>
        <nav className="flex items-center gap-4">
          <Link to="/editor">
            <Button variant="ghost" size="sm">Editor</Button>
          </Link>
          <Link to="/jobs">
            <Button variant="ghost" size="sm">History</Button>
          </Link>
          <ThemeToggle />
          {user && (
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
}
