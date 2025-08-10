"use client"

import { AlertCircleIcon, PaperclipIcon, UploadIcon, XIcon } from "lucide-react"
import { formatBytes, useFileUpload } from "@/hooks/use-file-upload"
import { Button } from "@/components/ui/button"

const initialFiles: any = []

export default function Dropzone() {
	const maxSize = 10 * 1024 * 1024 // 10MB

	const [
		{ files, isDragging, errors },
		{
			handleDragEnter,
			handleDragLeave,
			handleDragOver,
			handleDrop,
			openFileDialog,
			removeFile,
			getInputProps,
		},
	] = useFileUpload({
		maxSize,
		initialFiles,
	})

	const file = files[0]

	const sendToBackend = async () => {
		if (!file) return

		const formData = new FormData()
		formData.append("file", file.file) // file.file is the real File object

		try {
			const res = await fetch("http://localhost:5000/upload", {
				method: "POST",
				body: formData,
			})

			if (!res.ok) throw new Error("Upload failed")

			const data = await res.json()
			alert("Success: " + JSON.stringify(data))
		} catch (err) {
			console.error(err)
			alert("Error uploading file")
		}
	}

	return (
		<div className="flex flex-col gap-2">
			{/* Drop area */}
			<div
				role="button"
				onClick={openFileDialog}
				onDragEnter={handleDragEnter}
				onDragLeave={handleDragLeave}
				onDragOver={handleDragOver}
				onDrop={handleDrop}
				data-dragging={isDragging || undefined}
				className="border-input hover:bg-accent/50 data-[dragging=true]:bg-accent/50 has-[input:focus]:border-ring has-[input:focus]:ring-ring/50 flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed p-4 transition-colors"
			>
				<input
					{...getInputProps()}
					className="sr-only"
					aria-label="Upload file"
					disabled={Boolean(file)}
				/>

				<div className="flex flex-col items-center justify-center text-center">
					<div
						className="bg-background mb-2 flex size-11 shrink-0 items-center justify-center rounded-full border"
						aria-hidden="true"
					>
						<UploadIcon className="size-4 opacity-60" />
					</div>
					<p className="mb-1.5 text-sm font-medium">Upload file</p>
					<p className="text-muted-foreground text-xs">
						Drag & drop or click to browse (max. {formatBytes(maxSize)})
					</p>
				</div>
			</div>

			{errors.length > 0 && (
				<div
					className="text-destructive flex items-center gap-1 text-xs"
					role="alert"
				>
					<AlertCircleIcon className="size-3 shrink-0" />
					<span>{errors[0]}</span>
				</div>
			)}

			{/* File list */}
			{file && (
				<div className="space-y-2">
					<div
						key={file.id}
						className="flex items-center justify-between gap-2 rounded-xl border px-4 py-2"
					>
						<div className="flex items-center gap-3 overflow-hidden">
							<PaperclipIcon className="size-4 shrink-0 opacity-60" />
							<div className="min-w-0">
								<p className="truncate text-[13px] font-medium">
									{file.file.name}
								</p>
							</div>
						</div>

						<Button
							size="icon"
							variant="ghost"
							className="text-muted-foreground/80 hover:text-foreground -me-2 size-8 hover:bg-transparent"
							onClick={() => removeFile(files[0]?.id)}
							aria-label="Remove file"
						>
							<XIcon className="size-4" aria-hidden="true" />
						</Button>
					</div>

					<Button onClick={sendToBackend} className="w-full">
						Send to backend
					</Button>
				</div>
			)}
		</div>
	)
}

