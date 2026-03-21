import SkillDisplay from '../components/SkillDisplay'
import Roadmap from '../components/Roadmap'
import Card from '../components/ui/Card'
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

  return (
    <main className="min-h-screen bg-[#0d1117] py-10 text-[#c9d1d9] sm:py-14">
      <div className="mx-auto max-w-5xl space-y-6 px-4">
        <motion.div
          initial={sectionMotion.initial}
          animate={sectionMotion.animate}
          transition={{ duration: 0.35, ease: 'easeOut' }}
        >
          <Card as="header" className="p-6 bg-gradient-to-r from-[#0d1117] to-[#161b22]">
            <div className="mb-4 h-1.5 w-40 rounded-full bg-gradient-to-r from-[#238636] to-[#58a6ff]"></div>
            <h1 className="mb-2 text-2xl font-semibold tracking-tight text-[#f0f6fc]">OnboardIQ Results</h1>
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
          <Card as="section" className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-[#f0f6fc]">Results</h2>
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-[#f0f6fc]">Skill Analysis</h3>
                <SkillDisplay response={resultData} />
              </div>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-[#f0f6fc]">Learning Roadmap</h3>
                <Roadmap response={resultData} />
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </main>
  )
}

export default ResultsPage
