import { motion } from 'framer-motion'
import FileUpload from '../components/FileUpload'
import Card from '../components/ui/Card'
import SectionContainer from '../components/ui/SectionContainer'
import { useNavigate } from 'react-router-dom'

function HomePage() {
  const navigate = useNavigate()

  function handleUploadSuccess(data) {
    navigate('/results', { state: { resultData: data } })
  }

  function handleResetResults() {}

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
            <h1 className="mb-2 text-2xl font-semibold tracking-tight text-[#f0f6fc]">OnboardIQ</h1>
            <p className="text-lg font-medium text-[#f0f6fc]">AI Adaptive Onboarding Engine</p>
            <p className="mt-2 text-sm text-[#8b949e]">
              Upload your resume and job description to generate adaptive skill insights.
            </p>
          </Card>
        </motion.div>


        <motion.div
          initial={sectionMotion.initial}
          animate={sectionMotion.animate}
          transition={{ duration: 0.35, ease: 'easeOut', delay: 0.1 }}
          whileHover={{ scale: 1.01 }}
        >
          <SectionContainer title="Upload Documents">
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onResetResults={handleResetResults}
            />
          </SectionContainer>
        </motion.div>

        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, ease: 'easeOut', delay: 0.15 }}
          className="pb-2 text-center text-sm text-[#8b949e]"
        >
          OnBoardIQ Adaptive Workflow
        </motion.footer>
      </div>
    </main>
  )
}

export default HomePage
