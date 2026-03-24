import SkillDisplay from '../components/SkillDisplay'
import Roadmap from '../components/Roadmap'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const resultData = location.state?.resultData

  if (!resultData) {
    // If no data, redirect to home
    navigate('/', { replace: true })
    return null
  }

  const sectionMotion = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
  }

  const handleExport = () => {
    window.print()
  }

  const handleBack = () => {
    navigate('/')
  }

  return (
    <main className="min-h-screen bg-[#0d1117] py-10 text-[#c9d1d9] sm:py-14 print-bg">
      <div className="mx-auto max-w-5xl space-y-6 px-4">
        <motion.div
          initial={sectionMotion.initial}
          animate={sectionMotion.animate}
          transition={{ duration: 0.35, ease: 'easeOut' }}
        >
          <Card as="header" className="p-6 bg-gradient-to-r from-[#0d1117] to-[#161b22] print-card">
            <div className="flex items-center justify-between mb-4">
              <div className="mb-4 h-1.5 w-40 rounded-full bg-gradient-to-r from-[#238636] to-[#58a6ff] print-hide"></div>
              <Button variant="secondary" onClick={handleBack} className="no-print">
                Back
              </Button>
            </div>
            <h1 className="mb-2 text-2xl font-semibold tracking-tight text-[#f0f6fc] print-title">OnboardIQ Results</h1>
            <p className="text-lg font-medium text-[#f0f6fc]">AI Adaptive Onboarding Engine</p>
            <p className="mt-2 text-sm text-[#8b949e]">
              Here are your skill insights and personalized roadmap.
            </p>
          </Card>
        </motion.div>

        <motion.div
          initial={sectionMotion.initial}
          animate={sectionMotion.animate}
          transition={{ duration: 0.35, ease: 'easeOut', delay: 0.1 }}
        >
          <Card as="section" className="p-6 print-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#f0f6fc] print-section-title">Results</h2>
              <Button variant="secondary" onClick={handleExport} className="ml-4 no-print">
                Export
              </Button>
            </div>
            <div id="results-content" className="print-grid">
              <div className="grid gap-6 lg:grid-cols-2 print-col">
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold text-[#f0f6fc] print-section-title">Skill Analysis</h3>
                  <SkillDisplay response={resultData} />
                </div>
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold text-[#f0f6fc] print-section-title">Learning Roadmap</h3>
                  <Roadmap response={resultData} />
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </main>
  )
}

export default ResultsPage
