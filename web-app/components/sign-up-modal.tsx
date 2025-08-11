"use client"
import { LoadingButton } from "./loading-button";
import { useId, useState } from "react"
import { authClient } from "@/lib/auth-client";

import { Button } from "@/components/ui/button"
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function SignUpModal() {
	const id = useId()

	const [loadingStatus, setLoadingStatus] = useState(false)

	const [name, setName] = useState("")
	const [email, setEmail] = useState("")
	const [password, setPassword] = useState("")

	const handleSignUp = async () => {
		setLoadingStatus(true)
		const { data, error } = await authClient.signUp.email({
			email,
			password,
			name,
			callbackURL: "/dashboard"
		}, {
			onRequest: (ctx) => {
				console.log("Signing up with email:");
			},
			onSuccess: (ctx) => {
				console.log("Sign up successful", ctx.data);
				setLoadingStatus(false);
			},
			onError: (ctx) => {
				alert(ctx.error.message);
				console.error("Sign up failed", ctx.error);
				setLoadingStatus(false);
			},
		});
	}

	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button variant="outline" className="text-xs">Sign up</Button>
			</DialogTrigger>
			<DialogContent className="w-1/4">
				<div className="flex flex-col items-start gap-2">
					<DialogHeader>
						<DialogTitle className="sm:text-left">
							Sign up
						</DialogTitle>
						<DialogDescription className="sm:text-center">
							We just need a few details to get you started.
						</DialogDescription>
					</DialogHeader>
				</div>

				<form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
					<div className="space-y-4">
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-name`}>Full name</Label>
							<Input
								id={`${id}-name`}
								placeholder="Himanshu Sardana"
								type="text"
								required
								value={name}
								onChange={(e) => setName(e.target.value)}
							/>
						</div>
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-email`}>Email</Label>
							<Input
								id={`${id}-email`}
								placeholder="hi@yourcompany.com"
								type="email"
								required
								value={email}
								onChange={(e) => setEmail(e.target.value)}
							/>
						</div>
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-password`}>Password</Label>
							<Input
								id={`${id}-password`}
								placeholder="Enter your password"
								type="password"
								autoComplete="false"
								required
								value={password}
								onChange={(e) => setPassword(e.target.value)}
							/>
						</div>
					</div>
					<LoadingButton
						type="button"
						className="w-full font-bold"
						onClick={handleSignUp}
						loading={loadingStatus}
					>
						{loadingStatus ? "Signing up..." : "Sign up"}
					</LoadingButton>
				</form>

				<div className="before:bg-border after:bg-border flex items-center gap-3 before:h-px before:flex-1 after:h-px after:flex-1">
					<span className="text-muted-foreground text-xs">Or</span>
				</div>

				<Button variant="outline">Continue with Google</Button>

				<p className="text-muted-foreground text-center text-xs">
					By signing up you agree to our{" "}
					<a className="underline hover:no-underline" href="#">
						Terms
					</a>
					.
				</p>
			</DialogContent>
		</Dialog>
	)
}

