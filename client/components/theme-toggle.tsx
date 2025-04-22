"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Moon, Sun } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="border-emerald-300 dark:border-emerald-800"
    >
      {theme === "dark" ? <Sun className="h-5 w-5 text-emerald-600" /> : <Moon className="h-5 w-5 text-emerald-600" />}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
