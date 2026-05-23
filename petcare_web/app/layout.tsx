import './globals.css'
import { Nav } from '@/components/Nav'
import { Footer } from '@/components/Footer'
import { LangProvider } from '@/components/LangProvider'
import { DM_Sans, DM_Serif_Display } from 'next/font/google'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
})

const dmSerifDisplay = DM_Serif_Display({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-heading',
  display: 'swap',
})

export const metadata = {
  title: 'VetiCare — الرعاية البيطرية',
  description: 'Governed veterinary platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl" className={`${dmSans.variable} ${dmSerifDisplay.variable}`}>
      <body>
        <LangProvider>
          <Nav />
          {children}
          <Footer />
        </LangProvider>
      </body>
    </html>
  )
}
