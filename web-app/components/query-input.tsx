"use client"
import { useId, useState } from "react"
import { Input } from "@/components/ui/input"
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table"

export default function QueryInput({ onSubmit }) {
	const id = useId()
	const [query, setQuery] = useState("")
	const [result, setResult] = useState(null)
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e) => {
		e.preventDefault()
		if (!query.trim()) return

		setLoading(true)
		setResult(null)

		try {
			const res = await fetch("http://localhost:5000/query", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ nl_query: query }),
			})

			if (!res.ok) {
				throw new Error(`HTTP error: ${res.status}`)
			}

			const data = await res.json()
			setResult(data)

			// ✅ Call parent handler so NotebookPage can store the query/reply
			if (onSubmit) {
				onSubmit(query, JSON.stringify(data)) // You can format reply better
			}

			// Clear input after submit
			setQuery("")
		} catch (err) {
			console.error("Error sending query:", err)
		} finally {
			setLoading(false)
		}
	}

	return (
		<div>
			<form onSubmit={handleSubmit} className="*:not-first:mt-2">
				<Input
					id={id}
					placeholder="Enter your query here"
					type="text"
					value={query}
					className="py-7 bg-secondary"
					onChange={(e) => setQuery(e.target.value)}
				/>
			</form>

			{/* Optional inline preview */}
			<div className="mt-4">
				{loading && <p>Running query...</p>}
			</div>
		</div>
	)
}

