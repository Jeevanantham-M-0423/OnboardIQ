import { useMemo } from 'react'
import { motion } from 'framer-motion'
import Card from './ui/Card'

function toSkillList(value) {
  if (!value) {
    return []
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => (typeof item === 'string' ? item.trim() : String(item).trim()))
      .filter(Boolean)
  }

  if (typeof value === 'string') {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
  }

  return []
}

function pickFirst(response, keys) {
  for (const key of keys) {
    if (response?.[key] !== undefined) {
      return response[key]
    }
  }

  return null
}

function SkillSection({ title, skills }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      whileHover={{ scale: 1.02 }}
    >
      <Card as="section" className="p-4">
        <h3 className="mb-3 text-lg font-semibold text-[#f0f6fc]">{title}</h3>
        {skills.length > 0 ? (
          <ul className="list-disc space-y-1 pl-5 text-sm text-[#8b949e]">
            {skills.map((skill) => (
              <li key={`${title}-${skill}`}>{skill}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-[#8b949e]">No skills found.</p>
        )}
      </Card>
    </motion.div>
  )
}

function SkillDisplay({ response }) {
  const resumeSkills = useMemo(
    () =>
      toSkillList(pickFirst(response || {}, ['resume_skills', 'resumeSkills', 'skills_resume'])),
    [response]
  )

  const jdSkills = useMemo(
    () =>
      toSkillList(
        pickFirst(response || {}, ['jd_skills', 'jdSkills', 'job_description_skills', 'skills_jd'])
      ),
    [response]
  )

  const missingSkills = useMemo(
    () =>
      toSkillList(pickFirst(response || {}, ['missing_skills', 'missingSkills', 'skill_gaps'])),
    [response]
  )

  const hasAnySkills =
    resumeSkills.length > 0 || jdSkills.length > 0 || missingSkills.length > 0
  const hasNoMissingSkills = hasAnySkills && missingSkills.length === 0

  return (
    <div className="space-y-3">
      {!hasAnySkills ? (
        <div className="rounded-xl border border-[#30363d] bg-[#161b22] p-4 text-sm text-[#8b949e]">
          We could not detect skills yet. Upload both files to see a full comparison.
        </div>
      ) : null}

      {hasNoMissingSkills ? (
        <div className="rounded-md border border-[#238636] bg-[#161b22] p-4 text-sm text-[#238636]">
          Great match. You are already well-qualified for this role.
        </div>
      ) : null}

      <div className="grid gap-3 md:grid-cols-3">
        <SkillSection title="Resume Skills" skills={resumeSkills} />
        <SkillSection title="JD Skills" skills={jdSkills} />
        <SkillSection title="Missing Skills" skills={missingSkills} />
      </div>
    </div>
  )
}

export default SkillDisplay
