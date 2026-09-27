import './globals.css'
import './design-system.css'
import { Nav } from '@/components/Nav'
import { Footer } from '@/components/Footer'
import { LangProvider } from '@/components/LangProvider'
import { DM_Sans, DM_Serif_Display, IBM_Plex_Sans_Arabic } from 'next/font/google'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
})

// Arabic-first typography (G1): Arabic glyphs come from IBM Plex Sans Arabic; Latin falls through to DM Sans.
const plexArabic = IBM_Plex_Sans_Arabic({
  subsets: ['arabic'],
  weight: ['400', '600', '700'],
  variable: '--font-arabic',
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
    <html lang="ar" dir="rtl" className={`${plexArabic.variable} ${dmSans.variable} ${dmSerifDisplay.variable}`}>
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
