import Hero from "@/components/hero";
import Features from "@/components/features";
import Image from "next/image";
import Navbar from "@/components/navbar";

export default function Home() {
	return (
		<div className="">
			<Navbar />
			<Hero />
			<Features />
		</div>
	);
}
