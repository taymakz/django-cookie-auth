import Link from 'next/link';
import { ArrowRightIcon, ShieldCheckIcon, KeyIcon, PhoneIcon, UserIcon } from 'lucide-react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Django Cookie Auth',
  
};
export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col pt-10">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center min-h-[80vh] text-center px-6">
        <div className="max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium bg-fd-muted/50 text-fd-muted-foreground mb-6">
            <ShieldCheckIcon className="mr-2 h-3 w-3" />
            Secure Authentication Backend
          </div>

          {/* Main Heading */}
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl mb-6">
            Django Cookie
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Auth</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg text-fd-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed">
            Complete authentication backend with JWT tokens, phone-based registration,
            and secure OTP verification. Built with Django REST Framework.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              href="/docs"
              className="inline-flex items-center justify-center rounded-lg bg-fd-primary text-fd-primary-foreground px-6 py-3 text-sm font-medium transition-colors hover:bg-fd-primary/90 focus:outline-none focus:ring-2 focus:ring-fd-primary focus:ring-offset-2"
            >
              Get Started
              <ArrowRightIcon className="ml-2 h-4 w-4" />
            </Link>

          </div>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2  gap-6 max-w-4xl mx-auto mb-8">
            <div className="flex flex-col items-center p-6 rounded-lg border bg-fd-card">
              <div className="rounded-full bg-blue-100 dark:bg-blue-900/20 p-3 mb-4">
                <KeyIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="font-semibold mb-2">JWT Authentication</h3>
              <p className="text-sm text-fd-muted-foreground text-center">
                Secure JWT tokens with HTTP-only cookies
              </p>
            </div>

            <div className="flex flex-col items-center p-6 rounded-lg border bg-fd-card">
              <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-3 mb-4">
                <PhoneIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="font-semibold mb-2">Phone Registration</h3>
              <p className="text-sm text-fd-muted-foreground text-center">
                OTP-based registration with SMS verification
              </p>
            </div>

            <div className="flex flex-col items-center p-6 rounded-lg border bg-fd-card">
              <div className="rounded-full bg-purple-100 dark:bg-purple-900/20 p-3 mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="font-semibold mb-2">Security First</h3>
              <p className="text-sm text-fd-muted-foreground text-center">
                Rate limiting, validation, and secure flows
              </p>
            </div>

            <div className="flex flex-col items-center p-6 rounded-lg border bg-fd-card">
              <div className="rounded-full bg-orange-100 dark:bg-orange-900/20 p-3 mb-4">
                <UserIcon className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="font-semibold mb-2">User Management</h3>
              <p className="text-sm text-fd-muted-foreground text-center">
                Complete profile and authentication management
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
