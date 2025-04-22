export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center space-y-4 text-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="120"
        height="120"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-emerald-300 dark:text-emerald-700"
      >
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
        <path d="M8 9h8" />
        <path d="M8 15h8" />
        <path d="M12 12h4" />
      </svg>
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-emerald-700 dark:text-emerald-400">No queries yet</h3>
        <p className="text-sm text-gray-500 max-w-xs">Ask a question about travel requirements to get started</p>
      </div>
    </div>
  )
}
