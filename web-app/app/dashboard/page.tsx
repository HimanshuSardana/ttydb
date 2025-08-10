"use client"
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

export default function Page() {
	const [notebooks, setNotebooks] = useState([
		{ name: "My First Notebook", id: "1" },
		{ name: "Data Analysis Notebook", id: "2" },
		{ name: "Machine Learning Experiments", id: "3" },
		{ name: "Web Scraping Project", id: "4" },
		{ name: "Data Visualization Notebook", id: "5" },
		{ name: "Deep Learning Models", id: "6" },
		{ name: "Natural Language Processing", id: "7" },
		{ name: "Time Series Analysis", id: "8" },
		{ name: "Exploratory Data Analysis", id: "9" },

	])
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
									<BreadcrumbLink href="#">
										Dashboard
									</BreadcrumbLink>
								</BreadcrumbItem>
								<BreadcrumbSeparator className="hidden md:block" />
								<BreadcrumbItem>
									<BreadcrumbPage>Notebooks</BreadcrumbPage>
								</BreadcrumbItem>
							</BreadcrumbList>
						</Breadcrumb>
					</div>
				</header>
				{/* MAIN CONTENT */}
				<div className="flex flex-1 flex-col gap-1 p-4 pt-0 pr-[5%]">
					<div className="flex justify-between ">
						<div className="flex flex-col gap-1">
							<h3 className="text-3xl font-black">Your Notebooks</h3>
							<p className="text-muted-foreground">
								Manage your notebooks and queries here.
							</p>
						</div>

						<Button>Create Notebook</Button>
					</div>

					<div className="mt-5">
						<div className="grid md:grid-cols-4 gap-4 sm:grid-cols-1">
							{notebooks.map((notebook) => (
								<div
									key={notebook.id}
									className="rounded-lg p-4 hover:bg-muted bg-neutral-950/90  h-32"
								>
									<h4 className="text-xl font-semibold">
										{notebook.name}
									</h4>
									<p className="text-sm text-muted-foreground">
										This is a sample notebook.
									</p>
								</div>
							))}

						</div>
					</div>
				</div>
			</SidebarInset>
		</SidebarProvider>
	)
}
