import React from 'react';

export default function LandingPage({ onTryItNow }) {
  return (
    <div className="bg-background text-on-background min-h-screen">
      {/* TopNavBar Execution */}
      <nav className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-6 h-16 bg-white border-b border-slate-200 max-w-[1440px] mx-auto right-0">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold tracking-tighter text-slate-900 uppercase">BiasLens</span>
          <div className="hidden md:flex items-center gap-6 h-16">
            <a className="text-primary border-b-2 border-primary font-semibold h-full flex items-center px-1 font-sans text-sm tracking-tight transition-all duration-150 ease-in-out" href="#">Dashboard</a>
            <a className="text-slate-500 hover:text-slate-800 transition-colors px-1 font-sans text-sm font-medium tracking-tight h-full flex items-center" href="#">History</a>
            <a className="text-slate-500 hover:text-slate-800 transition-colors px-1 font-sans text-sm font-medium tracking-tight h-full flex items-center" href="#">Reports</a>
            <a className="text-slate-500 hover:text-slate-800 transition-colors px-1 font-sans text-sm font-medium tracking-tight h-full flex items-center" href="#">Settings</a>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-slate-50 rounded-full transition-all duration-150 ease-in-out">
            <span className="material-symbols-outlined text-slate-600">notifications</span>
          </button>
          <button className="p-2 hover:bg-slate-50 rounded-full transition-all duration-150 ease-in-out">
            <span className="material-symbols-outlined text-slate-600">help</span>
          </button>
          <div className="w-8 h-8 rounded-full overflow-hidden border border-slate-200">
            <img alt="User profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAlth9CBWnRDvGiv7Snn3F4UsbwqYNsNLQ9ukgfOwtiHALckMOmO_NI5TGdLO3X1XR-yMkVofGy2KpvQPC2uQD8DMjbkxyJ9ZS-hOZ18ab2qLMXEZu0Ad3dFU10TF7AtRtzBEMdGV5tUyJK--rJZmHb4k39YYy7b0Z_9f2I7wdRcU1z-6HTGKD83i5-vUcO2tRaz6Kh5jxHdeW7sWqpbdGKgFKh72tqKcCvaEET88zDthkGNvaH6XhoMKI8OFW3rgTleVvecCB9BgU"/>
          </div>
        </div>
      </nav>

      <main className="pt-16 max-w-[1440px] mx-auto">
        {/* Hero Section */}
        <section className="px-gutter py-xl md:py-[120px] bento-grid items-center">
          <div className="col-span-12 md:col-span-6 flex flex-col gap-sm">
            <span className="text-primary font-label-md uppercase tracking-widest px-xs py-base bg-primary/10 w-fit rounded">Bias Analysis v2.0</span>
            <h1 className="font-headline-lg text-headline-lg text-on-background lg:text-[48px] lg:leading-[56px]">
              Objective lens for <br/><span className="text-primary">algorithmic transparency</span>
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg mt-base">
              Equip your data science and compliance teams with clinical precision tools to identify, measure, and mitigate bias across multi-source data environments.
            </p>
            <div className="flex items-center gap-sm mt-md">
              <button onClick={onTryItNow} className="bg-primary text-on-primary px-lg py-sm font-label-md uppercase tracking-wider hover:bg-on-primary-fixed-variant transition-all rounded shadow-sm">
                Try it Now
              </button>
              <button className="border border-outline text-on-surface px-lg py-sm font-label-md uppercase tracking-wider hover:bg-surface-container-low transition-all rounded">
                View Demo
              </button>
            </div>
          </div>
          <div className="col-span-12 md:col-span-6 relative">
            <div className="aspect-video bg-surface-container-high rounded-xl overflow-hidden border border-slate-200 shadow-sm relative group">
              <img className="w-full h-full object-cover mix-blend-multiply opacity-80" alt="abstract visualization" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAGnCX3zmrjy9coOE3qrQ0oOR__Sn4BD3gF5HiZDHUicdojGpfvplzevo4o5O7atTnKEWaToVRAM12We-j2-bibNSs9yX773IIGrQRFTrep1yEEmh4jpJnGLp7mgK-KEHYOyJe1cyC6LcngUPhPzEOh1ySqfan09SWoS1Lq0IUOu0cScj2FMtXtndMNJYzsn3G8V7mbf63WPes8t3Sr1kdQ9qF8OPaosolELs-RnL_oEBXLUbnW0685aKQmRUOJzaPSATkrkHqXfwQ"/>
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent"></div>
              {/* Analytical UI Elements Over Hero */}
              <div className="absolute top-sm left-sm bg-white/90 backdrop-blur border border-slate-200 p-sm rounded shadow-sm flex flex-col gap-base">
                <div className="flex items-center justify-between gap-xl">
                  <span className="font-label-md text-on-surface-variant">Parity Score</span>
                  <span className="font-code-sm text-primary">0.94</span>
                </div>
                <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                  <div className="bg-primary h-full w-[94%]"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Trusted By Section */}
        <section className="px-gutter py-md bg-white border-y border-slate-100">
          <div className="flex flex-col items-center gap-md">
            <p className="font-label-md text-slate-400 uppercase tracking-widest">Trusted by Enterprise Compliance Teams</p>
            <div className="flex flex-wrap justify-center items-center gap-xl opacity-40 grayscale hover:grayscale-0 transition-all">
              <span className="text-xl font-bold">ALPHANET</span>
              <span className="text-xl font-bold">QUANTUM DATA</span>
              <span className="text-xl font-bold">SECUREFLOW</span>
              <span className="text-xl font-bold">NEXUS AI</span>
              <span className="text-xl font-bold">SYNTHESIS</span>
            </div>
          </div>
        </section>

        {/* Key Features Section */}
        <section className="px-gutter py-xl">
          <div className="flex flex-col items-center mb-xl">
            <h2 className="font-headline-md text-headline-md text-on-background">Engineered for Precision</h2>
            <div className="w-16 h-1 bg-primary mt-sm"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <div className="bg-white p-lg border border-slate-200 flex flex-col gap-sm hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-surface-container-low flex items-center justify-center rounded">
                <span className="material-symbols-outlined text-primary">fact_check</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm">Objective Analysis</h3>
              <p className="font-body-md text-on-surface-variant">Remove subjective interpretation. Our framework uses 40+ mathematical parity metrics to audit decision engines automatically.</p>
            </div>
            <div className="bg-white p-lg border border-slate-200 flex flex-col gap-sm hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-surface-container-low flex items-center justify-center rounded">
                <span className="material-symbols-outlined text-primary">source</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm">Multi-source Support</h3>
              <p className="font-body-md text-on-surface-variant">Seamlessly ingest data from Snowflake, AWS, and localized SQL databases. Unified reporting across disparate silos.</p>
            </div>
            <div className="bg-white p-lg border border-slate-200 flex flex-col gap-sm hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-surface-container-low flex items-center justify-center rounded">
                <span className="material-symbols-outlined text-primary">summarize</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm">Detailed Reporting</h3>
              <p className="font-body-md text-on-surface-variant">Automated PDF/JSON audit logs tailored for regulatory scrutiny, specifically designed for EU AI Act compliance.</p>
            </div>
          </div>
        </section>

        {/* How it Works Section */}
        <section className="px-gutter py-xl bg-slate-50 border-y border-slate-200 overflow-hidden">
          <div className="bento-grid">
            <div className="col-span-12 md:col-span-5 flex flex-col justify-center">
              <h2 className="font-headline-md text-headline-md mb-md">Integration in <br/>Three Cycles</h2>
              <div className="flex flex-col gap-lg">
                <div className="flex gap-md">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold font-code-sm">01</div>
                    <div className="w-0.5 flex-1 bg-slate-200 my-xs"></div>
                  </div>
                  <div>
                    <h4 className="font-headline-sm text-sm font-bold uppercase tracking-tight">Connect Ingress</h4>
                    <p className="font-body-md text-on-surface-variant mt-xs">Establish secure read-only access to your training datasets or model prediction endpoints via BiasLens API.</p>
                  </div>
                </div>
                <div className="flex gap-md">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold font-code-sm">02</div>
                    <div className="w-0.5 flex-1 bg-slate-200 my-xs"></div>
                  </div>
                  <div>
                    <h4 className="font-headline-sm text-sm font-bold uppercase tracking-tight">Set Thresholds</h4>
                    <p className="font-body-md text-on-surface-variant mt-xs">Define fairness criteria based on demographic parity, equalized odds, or disparate impact ratios.</p>
                  </div>
                </div>
                <div className="flex gap-md">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold font-code-sm">03</div>
                  </div>
                  <div>
                    <h4 className="font-headline-sm text-sm font-bold uppercase tracking-tight">Continuous Audit</h4>
                    <p className="font-body-md text-on-surface-variant mt-xs">Monitor bias in real-time as your models drift. Receive alerts whenever thresholds are breached.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-span-12 md:col-span-7 flex items-center justify-center relative">
              <div className="w-full aspect-square max-w-[500px] bg-white border border-slate-200 rounded p-md shadow-sm relative overflow-hidden">
                <div className="flex justify-between items-center mb-lg">
                  <span className="font-label-md text-slate-400">AUDIT_LOG_STREAM</span>
                  <div className="flex gap-xs">
                    <div className="w-2 h-2 rounded-full bg-error"></div>
                    <div className="w-2 h-2 rounded-full bg-secondary"></div>
                  </div>
                </div>
                <div className="flex flex-col gap-md">
                  <div className="p-sm bg-slate-50 border border-slate-100 rounded">
                    <div className="flex justify-between font-code-sm mb-xs">
                      <span>Demographic Parity</span>
                      <span className="text-error">0.78</span>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-error w-[78%]"></div>
                    </div>
                  </div>
                  <div className="p-sm bg-slate-50 border border-slate-100 rounded">
                    <div className="flex justify-between font-code-sm mb-xs">
                      <span>Equal Opportunity</span>
                      <span className="text-secondary">0.99</span>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-secondary w-[99%]"></div>
                    </div>
                  </div>
                  <div className="mt-md">
                    <div className="border-t border-slate-200 py-xs flex justify-between font-label-md text-slate-500">
                      <span>ATTRIBUTE</span>
                      <span>IMPACT</span>
                    </div>
                    <div className="py-xs flex justify-between font-body-md border-t border-slate-100">
                      <span>Age Group (18-24)</span>
                      <span className="text-error">-12.4%</span>
                    </div>
                    <div className="py-xs flex justify-between font-body-md border-t border-slate-100">
                      <span>Location (Urban)</span>
                      <span className="text-secondary">+2.1%</span>
                    </div>
                  </div>
                </div>
                <div className="absolute -bottom-xl -right-xl w-[300px] h-[300px] bg-primary/5 rounded-full -z-10 blur-3xl"></div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="px-gutter py-xl bg-on-background text-on-primary">
          <div className="max-w-3xl mx-auto text-center flex flex-col items-center gap-md">
            <h2 className="font-headline-lg text-headline-lg text-white">Ready to ensure algorithmic integrity?</h2>
            <p className="font-body-lg text-slate-400">Join the waitlist for BiasLens Pro or schedule a consultation with our data ethics specialists today.</p>
            <div className="flex flex-col sm:flex-row gap-sm w-full sm:w-auto">
              <button onClick={onTryItNow} className="bg-primary text-white px-xl py-sm font-label-md uppercase tracking-widest rounded-full hover:bg-on-primary-fixed-variant transition-all">Get Enterprise Access</button>
              <button className="border border-slate-700 text-white px-xl py-sm font-label-md uppercase tracking-widest rounded-full hover:bg-slate-800 transition-all">Talk to Sales</button>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-gutter py-lg border-t border-slate-200 bg-white">
          <div className="flex flex-col md:flex-row justify-between items-center gap-md">
            <div className="flex flex-col items-center md:items-start">
              <span className="text-lg font-black text-slate-800 uppercase tracking-tighter">BiasLens</span>
              <p className="font-label-md text-slate-500 mt-base">Clinical precision in AI ethics.</p>
            </div>
            <div className="flex gap-lg">
              <a className="font-label-md text-slate-600 hover:text-primary" href="#">Privacy Policy</a>
              <a className="font-label-md text-slate-600 hover:text-primary" href="#">Terms of Service</a>
              <a className="font-label-md text-slate-600 hover:text-primary" href="#">Security Documentation</a>
            </div>
            <p className="font-label-md text-slate-400">© 2024 BiasLens AI. All rights reserved.</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
