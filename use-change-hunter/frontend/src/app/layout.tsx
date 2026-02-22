import React from "react";
import type { Metadata } from "next";
import "../globals.css";

export const metadata: Metadata = {
  title: "Use-Change Hunter",
  description:
    "Identify planning-based value-add opportunities for your properties",
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
      </head>
      <body className="bg-slate-50 text-slate-900">
        <div className="min-h-screen flex flex-col">
          {/* Navigation */}
          <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">H</span>
                </div>
                <span className="font-bold text-lg text-slate-900 hidden sm:inline">
                  Use-Change Hunter
                </span>
              </div>

              <div className="flex items-center gap-4">
                <button className="text-sm font-medium text-slate-700 hover:text-slate-900">
                  About
                </button>
                <button className="text-sm font-medium text-slate-700 hover:text-slate-900">
                  Pricing
                </button>
                <button className="px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 transition-colors">
                  Sign In
                </button>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="bg-slate-900 text-slate-300 mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                <div>
                  <h3 className="font-bold text-white mb-4">
                    Use-Change Hunter
                  </h3>
                  <p className="text-sm text-slate-400">
                    Find planning-based value-add opportunities
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-4">Product</h4>
                  <ul className="space-y-2 text-sm">
                    <li>
                      <a href="#" className="hover:text-white">
                        Features
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        Pricing
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        How it works
                      </a>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-4">Company</h4>
                  <ul className="space-y-2 text-sm">
                    <li>
                      <a href="#" className="hover:text-white">
                        About
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        Blog
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        Contact
                      </a>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-4">Legal</h4>
                  <ul className="space-y-2 text-sm">
                    <li>
                      <a href="#" className="hover:text-white">
                        Privacy
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        Terms
                      </a>
                    </li>
                    <li>
                      <a href="#" className="hover:text-white">
                        Cookies
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-slate-800 pt-8 flex justify-between items-center text-sm text-slate-400">
                <p>&copy; 2024 Use-Change Hunter. All rights reserved.</p>
                <p>Built with precision planning analysis</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
