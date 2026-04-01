import './globals.css'
import { Inter } from 'next/font/google'
import { ClientProviders } from '@/components/providers/ClientProviders'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Sereno - AI-Driven Digital Well-Being Platform',
  description: 'A positive, supportive digital space for reflection, insights, and community connection',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientProviders>
          <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {children}
          </div>
        </ClientProviders>
      </body>
    </html>
  )
}
