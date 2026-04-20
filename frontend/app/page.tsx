import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm flex flex-col gap-8">
        {/* Logo / Brand */}
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2.5 mb-1">
            <Image src="/logo.png" alt="Car Parkho" width={32} height={32} className="rounded-lg" />
            <span className="text-coral text-sm font-bold tracking-widest uppercase">Car Parkho</span>
          </div>
          <h1 className="text-charcoal text-3xl font-bold leading-tight">
            Find your right car
          </h1>
          <p className="text-secondary text-base leading-relaxed mt-1">
            Answer 7 quick questions. We&apos;ll shortlist the 3 cars that actually fit your life — with plain-language reasons why.
          </p>
        </div>

        {/* Stats / Trust signals */}
        <div className="grid grid-cols-3 gap-4 border border-border rounded-[8px] p-4 bg-white">
          <div className="text-center">
            <p className="text-charcoal text-lg font-bold">102</p>
            <p className="text-secondary text-xs mt-0.5">Cars</p>
          </div>
          <div className="text-center border-x border-border">
            <p className="text-charcoal text-lg font-bold">7</p>
            <p className="text-secondary text-xs mt-0.5">Questions</p>
          </div>
          <div className="text-center">
            <p className="text-charcoal text-lg font-bold">&lt;2 min</p>
            <p className="text-secondary text-xs mt-0.5">To shortlist</p>
          </div>
        </div>

        {/* CTA */}
        <Link
          href="/quiz"
          className="w-full py-4 bg-coral text-white text-base font-bold text-center rounded-[8px] hover:bg-orange-600 transition-colors"
        >
          Help me find a car →
        </Link>

        <p className="text-secondary text-xs text-center">
          No sign-up. No spam. Just a shortlist.
        </p>
      </div>
    </main>
  );
}
