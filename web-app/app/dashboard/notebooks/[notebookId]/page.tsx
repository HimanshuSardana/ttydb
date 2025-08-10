"use client"
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
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import Dropzone from "@/components/dropzone"

export default function NotebookPage() {
	const { notebookId } = useParams<{ notebookId: string }>()

	// State for storing queries
	const [queries, setQueries] = useState<
		{ query: string; reply: string }[]
	>([
		{
			query: "Show me all the users who signed up in the last 30 days",
			reply: "Here are the users who signed up in the last 30 days...",
		},
	])

	// Callback when a new query is submitted
	const handleNewQuery = (query: string, reply: string) => {
		setQueries(prev => [{ query, reply }, ...prev])
	}

	return (
		<SidebarProvider>
			<AppSidebar />
			<SidebarInset>
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
									<BreadcrumbPage>Notebook {notebookId}</BreadcrumbPage>
								</BreadcrumbItem>
							</BreadcrumbList>
						</Breadcrumb>
					</div>
				</header>

				{/* MAIN CONTENT */}
				<div className="flex flex-1 flex-col gap-4 p-4 pt-0 pr-[5%]">
					{/* Notebook title */}
					<div className="flex flex-row gap-1 justify-between items-center">
						<div className="flex flex-col">
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
								<DialogTitle>Add New Data Sourcee</DialogTitle>
								<DialogDescription className="-mt-2">Add a new data source that you can query in natural language.</DialogDescription>

								<Dropzone />
							</DialogContent>
						</Dialog>
					</div>

					{/* Scrollable area for queries */}
					<div className="flex-1 flex flex-col-reverse overflow-y-auto gap-4">
						{/* Query cells (newest first) */}
						{queries.map((q, index) => (
							<div
								key={index}
								className="p-4 border rounded-lg bg-background shadow-sm"
							>
								<h3 className="text-muted-foreground font-medium">{q.query}</h3>
								<p className="mt-2 text-sm">{q.reply}</p>
							</div>
						))}

						{/* Query input at bottom */}
					</div>
					<div className="sticky bottom-0 bg-background pt-4 border-t">
						<QueryInput
							onSubmit={(query, reply) => handleNewQuery(query, reply)}
						/>
					</div>

				</div>
			</SidebarInset>
		</SidebarProvider>
	)
}

