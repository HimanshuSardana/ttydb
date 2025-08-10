"use client"
import { motion } from "framer-motion";
import QueryInput from "@/components/query-input"
import { AppSidebar } from "@/components/app-sidebar"
import { Button } from "@/components/ui/button"
import {
	Breadcrumb,
	BreadcrumbItem,
	BreadcrumbLink,
	BreadcrumbList,
	BreadcrumbPage,
	BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
	SidebarInset,
	SidebarProvider,
	SidebarTrigger,
} from "@/components/ui/sidebar"
import { useState } from "react"
import { useParams } from "next/navigation"
import {
	Dialog,
	DialogTrigger,
	DialogContent,
	DialogTitle,
	DialogDescription,
} from "@/components/ui/dialog"
import Dropzone from "@/components/dropzone"

export default function NotebookPage() {
	const { notebookId } = useParams<{ notebookId: string }>()

	type QueryReply = {
		attempts: number
		explanation: string
		rows: any[]
		sql: string
		success: boolean
	}

	const [queries, setQueries] = useState<{ query: string; reply: QueryReply }[]>(
		[]
	)

	const handleNewQuery = (query: string, reply: string) => {
		const parsedReply =
			typeof reply === "string" ? JSON.parse(reply) : reply
		setQueries((prev) => [{ query, reply: parsedReply }, ...prev])
	}

	return (
		<SidebarProvider>
			<AppSidebar />
			<SidebarInset>
				{/* HEADER */}
				<header className="flex h-16 shrink-0 items-center gap-2">
					<div className="flex items-center gap-2 px-4">
						<SidebarTrigger className="-ml-1" />
						<Separator orientation="vertical" className="mr-2 h-4" />
						<Breadcrumb>
							<BreadcrumbList>
								<BreadcrumbItem className="hidden md:block">
									<BreadcrumbLink href="#">Dashboard</BreadcrumbLink>
								</BreadcrumbItem>
								<BreadcrumbSeparator className="hidden md:block" />
								<BreadcrumbItem>
									<BreadcrumbLink href="#">Notebooks</BreadcrumbLink>
								</BreadcrumbItem>
								<BreadcrumbSeparator className="hidden md:block" />
								<BreadcrumbItem>
									<BreadcrumbPage>
										Notebook {notebookId}
									</BreadcrumbPage>
								</BreadcrumbItem>
							</BreadcrumbList>
						</Breadcrumb>
					</div>
				</header>

				{/* MAIN CONTENT */}
				<div className="flex flex-1 flex-col gap-4 p-8 pt-0 pr-[5%]">
					{/* Notebook title */}
					<div className="flex flex-row gap-1 justify-between items-center">
						<div className="flex flex-col mt-3 gap-1">
							<h3 className="text-3xl font-black">Notebook {notebookId}</h3>
							<p className="text-muted-foreground">
								Manage your notebooks and queries here.
							</p>
						</div>

						<Dialog>
							<DialogTrigger>
								<Button className="font-bold">Add Data Source</Button>
							</DialogTrigger>
							<DialogContent className="w-1/3">
								<DialogTitle>Add New Data Source</DialogTitle>
								<DialogDescription className="-mt-2">
									Add a new data source that you can query in natural language.
								</DialogDescription>
								<Dropzone />
							</DialogContent>
						</Dialog>
					</div>

					{/* Scrollable queries list */}
					<motion.div layout className="flex-1 flex flex-col-reverse overflow-y-auto gap-4 mt-5">
						{queries.map((q, index) => (
							<motion.div
								key={index}
								className="p-4 border rounded-lg bg-card shadow-sm hover:shadow-md transition-shadow"
							>
								{/* Header with query and status */}
								<div className="flex items-center justify-between">
									<h3 className="text-lg font-semibold">{q.query}</h3>
									<span
										className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${q.reply.success
											? "bg-emerald-800/20 text-emerald-800"
											: "bg-red-800/20 text-red-500"
											}`}
									>
										{q.reply.success
											? "Query Succeeded"
											: "Query Failed"}
									</span>
								</div>

								{/* Explanation */}
								<p className="mt-2 text-sm text-muted-foreground leading-relaxed">
									{q.reply.explanation}
								</p>

								{/* SQL */}
								<div className="mt-3 bg-muted/90 p-3 rounded-md overflow-x-auto">
									<code className="text-sm font-mono text-foreground">
										{q.reply.sql}
									</code>
								</div>

								{/* Results Table */}
								{q.reply.rows && q.reply.rows.length > 1 && (
									<div className="mt-4 overflow-x-auto">
										<table className="min-w-full border border-border rounded-md">
											<thead className="bg-muted/60 rounded-md">
												<tr className="rounded-md">
													{q.reply.rows[0].map(
														(col: string, i: number) => (
															<th
																key={i}
																className="px-3 py-3 text-left text-sm font-semibold bg-muted text-foreground border-b"
															>
																{col}
															</th>
														)
													)}
												</tr>
											</thead>
											<tbody>
												{q.reply.rows
													.slice(1)
													.map((row: any[], rIndex: number) => (
														<tr
															key={rIndex}
															className="hover:bg-muted/20"
														>
															{row.map(
																(cell, cIndex) => (
																	<td
																		key={cIndex}
																		className="px-3 py-3 text-sm border-b text-muted-foreground"
																	>
																		{cell}
																	</td>
																)
															)}
														</tr>
													))}
											</tbody>
										</table>
									</div>
								)}
							</motion.div>
						))}
					</motion.div>

					{/* Query input */}
					<div className="sticky bottom-0 bg-background pt-4 mt-1 w-full">
						<QueryInput
							onSubmit={(query, reply) =>
								handleNewQuery(query, reply)
							}
						/>
					</div>
				</div>
			</SidebarInset>
		</SidebarProvider>
	)
}

