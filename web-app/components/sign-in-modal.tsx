import { useId } from "react"

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

export default function SignInModal() {
	const id = useId()
	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button variant="outline">Sign up</Button>
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

				<form className="space-y-5">
					<div className="space-y-4">
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-name`}>Full name</Label>
							<Input
								id={`${id}-name`}
								placeholder="Himanshu Sardana"
								type="text"
								required
							/>
						</div>
						<div className="*:not-first:mt-2">
							<Label htmlFor={`${id}-email`}>Email</Label>
							<Input
								id={`${id}-email`}
								placeholder="hi@yourcompany.com"
								type="email"
								required
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
							/>
						</div>
					</div>
					<Button type="button" className="w-full font-bold">
						Sign up
					</Button>
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
