"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { useTheme } from "next-themes"
import { motion, AnimatePresence } from "framer-motion"
import { Clipboard, Send, Trash2 } from "lucide-react"
import ReactMarkdown from "react-markdown"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import Loading from "@/components/loading"
import EmptyState from "@/components/empty-state"

interface QueryItem {
  query: string
  response: string
  timestamp: number
}

export default function Home() {
  const [query, setQuery] = useState("")
  const [response, setResponse] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<QueryItem[]>([])
  const [hasInteracted, setHasInteracted] = useState(false)
  const responseRef = useRef<HTMLDivElement>(null)
  const { theme } = useTheme()

  // Load history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem("queryHistory")
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory))
      } catch (e) {
        console.error("Failed to parse history from localStorage")
      }
    }
  }, [])

  // Save history to localStorage whenever it changes
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem("queryHistory", JSON.stringify(history))
    }
  }, [history])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate input
    if (!query.trim()) {
      setError("Please enter a question")
      return
    }

    setIsLoading(true)
    setError(null)
    setHasInteracted(true)

    try {
      const response = await fetch("https://pawait-production.up.railway.app/api/v1/queries/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query.trim() }),
      })

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error("Too many requests. Wait 1 minute")
        }
        throw new Error("Failed to fetch response. Try again later")
      }

      const data = await response.json()
      setResponse(data.response || "No response received")

      // Add to history
      const newHistoryItem = {
        query: query.trim(),
        response: data.response || "No response received",
        timestamp: Date.now(),
      }

      setHistory((prev) => [newHistoryItem, ...prev].slice(0, 10)) // Keep only last 10 queries
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  const handleHistoryItemClick = (item: QueryItem) => {
    setQuery(item.query)
    setResponse(item.response)
    setError(null)

    // Scroll to response
    if (responseRef.current) {
      responseRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard
      .writeText(response)
      .then(() => {
        // Could add a toast notification here
        console.log("Copied to clipboard")
      })
      .catch((err) => {
        console.error("Failed to copy: ", err)
      })
  }

  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem("queryHistory")
  }

  return (
    <div className="min-h-screen bg-background transition-colors duration-300">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-end mb-4">
          <ThemeToggle />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column - Input */}
          <div className="space-y-6">
            <Card className="border-emerald-300 dark:border-emerald-800">
              <CardHeader className="pb-4">
                <CardTitle className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                  AI Q&A Assistant
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <Textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about anything you want..."
                    className="min-h-[150px] border-emerald-200 dark:border-emerald-900 focus:ring-emerald-500"
                  />

                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm"
                    >
                      {error}
                    </motion.div>
                  )}

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-emerald-500 hover:bg-emerald-600 text-white transition-colors"
                  >
                    {isLoading ? <Loading className="mr-2" /> : <Send className="mr-2 h-4 w-4" />}
                    {isLoading ? "Processing..." : "Submit Question"}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* History Section */}
            {history.length > 0 && (
              <Card className="border-emerald-300 dark:border-emerald-800">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium text-emerald-700 dark:text-emerald-400">
                      Query History
                    </CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearHistory}
                      className="text-gray-500 hover:text-red-500"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    <AnimatePresence>
                      {history.map((item, index) => (
                        <motion.li
                          key={item.timestamp}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Button
                            variant="ghost"
                            className="w-full justify-start text-left truncate hover:bg-emerald-50 dark:hover:bg-emerald-950"
                            onClick={() => handleHistoryItemClick(item)}
                          >
                            <span className="truncate">{item.query}</span>
                          </Button>
                        </motion.li>
                      ))}
                    </AnimatePresence>
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Response */}
          <div>
            <Card className="border-emerald-300 dark:border-emerald-800 h-full" ref={responseRef}>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-xl font-medium text-emerald-700 dark:text-emerald-400">Response</CardTitle>
                  {response && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={copyToClipboard}
                      className="text-gray-500 hover:text-emerald-600"
                    >
                      <Clipboard className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="min-h-[300px]">
                {isLoading ? (
                  <div className="flex justify-center items-center h-[300px]">
                    <Loading size="lg" />
                  </div>
                ) : response ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="prose dark:prose-invert max-w-none"
                  >
                    <ReactMarkdown>{response}</ReactMarkdown>
                  </motion.div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-[300px] text-center">
                    {!hasInteracted ? (
                      <EmptyState />
                    ) : (
                      <p className="text-gray-500">Submit a question to see the response here</p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
