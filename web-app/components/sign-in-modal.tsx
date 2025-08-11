"use client"
import { LoadingButton } from "./loading-button"
import React from "react"
import { useId } from "react"
import { authClient } from "@/lib/auth-client"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function SignInModal() {
	const id = useId()
	const [loadingStatus, setLoadingStatus] = React.useState(false);

	const handleSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
		setLoadingStatus(true);
		e.preventDefault()
		const formData = new FormData(e.currentTarget)

		const email = formData.get("email") as string
		const password = formData.get("password") as string

		const { data, error } = await authClient.signIn.email({
			email,
			password,
			callbackURL: "/dashboard",
			rememberMe: false
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
		})
	}

	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button size={"sm"} className="text-xs font-bold">Sign in</Button>
			</DialogTrigger>
			<DialogContent className="w-1/4">
				<div className="flex flex-col items-start gap-2">
					<DialogHeader>
						<DialogTitle>Welcome back</DialogTitle>
						<DialogDescription className="sm:text-center">
							Enter your credentials to login to your account.
						</DialogDescription>
					</DialogHeader>
				</div>

				<form className="space-y-5" onSubmit={handleSignIn}>
					<div className="space-y-4">
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-email`}>Email</Label>
							<Input
								id={`${id}-email`}
								name="email"
								placeholder="hi@yourcompany.com"
								type="email"
								required
							/>
						</div>
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-password`}>Password</Label>
							<Input
								id={`${id}-password`}
								name="password"
								placeholder="Enter your password"
								type="password"
								required
							/>
						</div>
					</div>
					<LoadingButton loading={loadingStatus} type="submit" className="w-full">
						Sign in
					</LoadingButton>
				</form>

				<div className="before:bg-border after:bg-border flex items-center gap-3 before:h-px before:flex-1 after:h-px after:flex-1">
					<span className="text-muted-foreground text-xs">Or</span>
				</div>

				<Button variant="outline">Login with Google</Button>
			</DialogContent>
		</Dialog>
	)
}

