import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import Button from './ui/Button'
import Card from './ui/Card'

function pickFirst(response, keys) {
  for (const key of keys) {
    if (response?.[key] !== undefined) {
      return response[key]
    }
  }

  return null
}

function normalizeResources(resources) {
  if (!resources) {
    return []
  }

  if (Array.isArray(resources)) {
    return resources
      .map((item) => {
        if (typeof item === 'string') {
          return { label: item, url: item }
        }

        if (typeof item === 'object' && item !== null) {
          const label = item.label || item.title || item.name || item.url || ''
          const url = item.url || item.link || ''
          return { label: String(label), url: String(url) }
        }

        return null
      })
      .filter(Boolean)
      .filter((item) => item.label)
  }

  if (typeof resources === 'string') {
    return [{ label: resources, url: resources }]
  }

  return []
}

function normalizeRoadmap(roadmapData) {
  if (!roadmapData) {
    return []
  }

  if (Array.isArray(roadmapData)) {
    return roadmapData
      .map((item, index) => {
        if (typeof item === 'string') {
          return {
            step: index + 1,
            skill: item,
            reason: '',
            resources: [],
          }
        }

        if (typeof item === 'object' && item !== null) {
          const skill = item.skill || item.skill_name || item.topic || item.title || ''
          const reason = item.reason || item.why || item.explanation || item.rationale || ''
          return {
            step: item.step || item.order || index + 1,
            skill: String(skill),
            reason: String(reason),
            resources: normalizeResources(item.resources || item.links),
          }
        }

        return null
      })
      .filter(Boolean)
      .filter((item) => item.skill)
  }

  return []
}

function Roadmap({ response }) {
  const [expandedReasons, setExpandedReasons] = useState({})

  const roadmapRaw = pickFirst(response || {}, [
    'roadmap',
    'learning_roadmap',
    'learningPath',
    'learning_path',
    'adaptive_roadmap',
  ])

  const roadmap = useMemo(() => normalizeRoadmap(roadmapRaw), [roadmapRaw])

  if (roadmap.length === 0) {
    return (
      <div className="rounded-xl border border-[#d0d7de] bg-[#f6f8fa] p-4 text-sm text-[#57606a]">
        No learning path is needed right now. Upload another role to generate a new roadmap.
      </div>
    )
  }

  function isReasonExpanded(stepItem, index) {
    const key = `${stepItem.step}-${stepItem.skill}-${index}`
    if (expandedReasons[key] === undefined) {
      return true
    }

    return expandedReasons[key]
  }

  function toggleReason(stepItem, index) {
    const key = `${stepItem.step}-${stepItem.skill}-${index}`
    setExpandedReasons((prev) => ({
      ...prev,
      [key]: !isReasonExpanded(stepItem, index),
    }))
  }

  return (
    <ol className="space-y-1">
        {roadmap.map((stepItem, index) => {
          const expanded = isReasonExpanded(stepItem, index)
          const isLast = index === roadmap.length - 1
          const isCurrentStep = index === 0

          return (
            <motion.li
              key={`${stepItem.step}-${stepItem.skill}-${index}`}
              className="relative flex gap-4 pb-5"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut', delay: index * 0.08 }}
            >
              <div className="relative flex w-10 flex-col items-center pt-1">
                <span
                  className={`z-10 inline-flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold text-white transition-all duration-200 ${
                    isCurrentStep ? 'bg-[#238636]' : 'bg-[#30363d]'
                  }`}
                >
                  {stepItem.step}
                </span>
                {!isLast ? <span className="mt-1 w-0.5 flex-1 rounded-full bg-[#30363d]"></span> : null}
              </div>

              <motion.div whileHover={{ scale: 1.02 }} className="w-full">
                <Card
                  className={`w-full rounded-xl border bg-[#161b22] p-4 ${
                    isCurrentStep
                      ? 'border-[#238636] shadow-md'
                      : 'border-[#30363d] shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium uppercase tracking-wide text-[#8b949e]">
                        Step {stepItem.step}
                      </p>
                      <p className="mt-1 text-lg font-semibold text-[#f0f6fc]">
                        {stepItem.skill}
                      </p>
                      {isCurrentStep ? (
                        <p className="mt-1 text-sm font-medium text-[#238636]">Current step</p>
                      ) : null}
                    </div>

                    <Button
                      type="button"
                      onClick={() => toggleReason(stepItem, index)}
                      variant="secondary"
                      className="px-3 py-1.5 text-sm"
                    >
                      {expanded ? 'Hide Why' : 'Why?'}
                    </Button>
                  </div>

                  {expanded ? (
                    <div className="mt-3 rounded-lg border border-[#30363d] bg-[#161b22] p-3">
                      <p className="text-sm font-medium text-[#f0f6fc]">Reason</p>
                      <p className="mt-1 text-sm leading-relaxed text-[#8b949e]">
                        {stepItem.reason || 'No reason provided.'}
                      </p>
                    </div>
                  ) : null}

                  {stepItem.resources.length > 0 ? (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-[#f0f6fc]">Resources</p>
                      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-[#8b949e]">
                      {stepItem.resources.map((resource, resourceIndex) => (
                        <li key={`${stepItem.skill}-${resourceIndex}`}>
                          {resource.url ? (
                            <a
                              href={resource.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[#58a6ff] underline hover:text-[#58a6ff] hover:underline transition-all duration-200"
                            >
                              {resource.label}
                            </a>
                          ) : (
                            resource.label
                          )}
                        </li>
                      ))}
                      </ul>
                    </div>
                  ) : (
                    <p className="mt-3 text-sm text-[#8b949e]">No resources provided.</p>
                  )}

                  {!isLast ? <div className="mt-4 border-b border-[#21262c]"></div> : null}
                </Card>
              </motion.div>
            </motion.li>
          )
        })}
      </ol>
  )
}

export default Roadmap
