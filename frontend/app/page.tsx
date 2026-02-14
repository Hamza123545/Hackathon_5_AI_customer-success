'use client';

// Import from src/components since the component lives there
import SupportForm from '../src/components/SupportForm';
import { FadeIn, GlassCard } from '../src/components/ui-helpers';
import { Bot, Zap, ShieldCheck } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 relative z-10">

      {/* Hero Section */}
      <div className="w-full max-w-5xl text-center mb-16 mt-10">
        <FadeIn className="">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Live System Online
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
            Customer Success <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              Reimagined with AI
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Experience the future of support. Our 24/7 Digital Employee understands context,
            remembers you across channels, and solves problems instantly.
          </p>
        </FadeIn>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mb-16">
          <FadeIn delay={0.2} className="">
            <GlassCard className="h-full">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-4 text-blue-400">
                <Zap size={24} />
              </div>
              <h3 className="font-bold text-white text-lg mb-2">Instant Resolution</h3>
              <p className="text-sm text-gray-400">Powered by Gemini 1.5 Flash to provide milliseconds responses sourced from our verified knowledge base.</p>
            </GlassCard>
          </FadeIn>


          <FadeIn delay={0.3} className="">
            <GlassCard className="h-full">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4 text-purple-400">
                <Bot size={24} />
              </div>
              <h3 className="font-bold text-white text-lg mb-2">Cross-Channel Memory</h3>
              <p className="text-sm text-gray-400">Whether you email, WhatsApp, or chat here—we remember the conversation context perfectly.</p>
            </GlassCard>
          </FadeIn>

          <FadeIn delay={0.4} className="">
            <GlassCard className="h-full">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4 text-emerald-400">
                <ShieldCheck size={24} />
              </div>
              <h3 className="font-bold text-white text-lg mb-2">Enterprise Grade</h3>
              <p className="text-sm text-gray-400">Built on Kubernetes with auto-healing, circuit breakers, and 99.9% uptime SLA.</p>
            </GlassCard>
          </FadeIn>
        </div>
      </div>

      {/* Interactive Demo Section */}
      <FadeIn delay={0.5} className="w-full max-w-3xl">
        <GlassCard className="border-t-4 border-t-blue-500/50">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white">Try it yourself</h2>
            <p className="text-gray-400">Submit a ticket below to see the magic in action.</p>
          </div>
          <SupportForm />
        </GlassCard>
      </FadeIn>

      <footer className="mt-20 text-center text-gray-500 text-sm pb-8">
        <p>&copy; {new Date().getFullYear()} Customer Success FTE. Built for Panaversity Hackathon 5.</p>
      </footer>
    </main>
  );
}
