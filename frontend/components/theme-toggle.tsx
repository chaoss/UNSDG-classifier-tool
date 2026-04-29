"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-9 w-[72px] rounded-full bg-muted/60 animate-pulse" />;
  }

  const isDark = theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="group relative flex h-9 w-[72px] cursor-pointer items-center justify-between rounded-full border border-border bg-muted/60 p-1 shadow-inner transition-all duration-300 hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      aria-label="Toggle theme"
      title={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      {/* Sliding Thumb */}
      <div
        className={`absolute left-1 h-7 w-7 rounded-full bg-background shadow-md ring-1 ring-border/50 transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${
          isDark ? "translate-x-9" : "translate-x-0"
        }`}
      />
      
      {/* Sun Icon */}
      <div className="z-10 flex h-full w-1/2 items-center justify-center">
        <Sun 
          className={`h-4 w-4 transition-all duration-500 ${
            isDark 
              ? "text-muted-foreground/60 rotate-90 scale-75" 
              : "text-amber-500 rotate-0 scale-100"
          }`} 
        />
      </div>
      
      {/* Moon Icon */}
      <div className="z-10 flex h-full w-1/2 items-center justify-center">
        <Moon 
          className={`h-4 w-4 transition-all duration-500 ${
            isDark 
              ? "text-indigo-400 rotate-0 scale-100" 
              : "text-muted-foreground/60 -rotate-90 scale-75"
          }`} 
        />
      </div>
    </button>
  );
}

