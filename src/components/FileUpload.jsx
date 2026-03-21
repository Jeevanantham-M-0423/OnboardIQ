import { useEffect, useRef, useState } from 'react'
import { uploadFiles } from '../services/api'
import Button from './ui/Button'

const ACCEPTED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

const ACCEPTED_EXTENSIONS = ['.pdf', '.docx']

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

function hasValidExtension(fileName) {
  const lowerName = fileName.toLowerCase()
  return ACCEPTED_EXTENSIONS.some((extension) => lowerName.endsWith(extension))
}

function isValidFileType(file) {
  if (!file) {
    return false
  }

  if (ACCEPTED_MIME_TYPES.includes(file.type)) {
    return true
  }

  // Some browsers may not provide MIME type for dragged or local files.
  return hasValidExtension(file.name)
}

import { useNavigate } from 'react-router-dom'

function FileUpload({ onUploadSuccess, onResetResults }) {
  const navigate = useNavigate()
  const resumeInputRef = useRef(null)
  const jdInputRef = useRef(null)

  const [resumeFile, setResumeFile] = useState(null)
  const [jobDescriptionFile, setJobDescriptionFile] = useState(null)
  const [errors, setErrors] = useState({ resume: '', jobDescription: '' })
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [submitError, setSubmitError] = useState('')
  const [isSuccess, setIsSuccess] = useState(false)

  useEffect(() => {
    if (!isSuccess) {
      return undefined
    }

    const timeoutId = setTimeout(() => {
      setIsSuccess(false)
    }, 3500)

    return () => {
      clearTimeout(timeoutId)
    }
  }, [isSuccess])

  function handleReset() {
    setResumeFile(null)
    setJobDescriptionFile(null)
    setErrors({ resume: '', jobDescription: '' })
    setSubmitError('')
    setIsSuccess(false)

    if (resumeInputRef.current) {
      resumeInputRef.current.value = ''
    }

    if (jdInputRef.current) {
      jdInputRef.current.value = ''
    }

    if (onResetResults) {
      onResetResults()
    }
  }

  function handleFileChange(event, field) {
    const file = event.target.files?.[0] ?? null

    if (!file) {
      if (field === 'resume') {
        setResumeFile(null)
      } else {
        setJobDescriptionFile(null)
      }

      setSubmitError('')
      setIsSuccess(false)

      setErrors((prev) => ({ ...prev, [field]: '' }))
      return
    }

    if (!isValidFileType(file)) {
      event.target.value = ''
      setErrors((prev) => ({
        ...prev,
        [field]: 'Only PDF or DOCX files are allowed.',
      }))

      if (field === 'resume') {
        setResumeFile(null)
      } else {
        setJobDescriptionFile(null)
      }
      return
    }

    if (field === 'resume') {
      setResumeFile(file)
    } else {
      setJobDescriptionFile(file)
    }

    setSubmitError('')
    setIsSuccess(false)
    if (onResetResults) {
      onResetResults()
    }

    setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const nextErrors = { resume: '', jobDescription: '' }

    if (!resumeFile) {
      nextErrors.resume = 'Please select a resume file.'
    }

    if (!jobDescriptionFile) {
      nextErrors.jobDescription = 'Please select a job description file.'
    }

    if (nextErrors.resume || nextErrors.jobDescription) {
      setErrors(nextErrors)
      return
    }

    setSubmitError('')
    setIsSuccess(false)
    setIsLoading(true)
    setLoadingMessage('Uploading...')

    try {
      const dataPromise = uploadFiles(resumeFile, jobDescriptionFile)

      // Tiny staged delays make status updates feel smoother without blocking UI.
      await wait(300)
      setLoadingMessage('Analyzing...')

      await wait(300)
      setLoadingMessage('Generating roadmap...')

      const data = await dataPromise
      const safeData = {
        resume_skills: data?.resume_skills || [],
        jd_skills: data?.jd_skills || [],
        matched_skills: data?.matched_skills || [],
        missing_skills: data?.missing_skills || [],
        roadmap: data?.roadmap || [],
      }

      setIsSuccess(true)
      if (onUploadSuccess) {
        onUploadSuccess(safeData)
      }
    } catch (error) {
      setSubmitError('Something went wrong. Please try again.')
      setIsSuccess(false)
    } finally {
      setIsLoading(false)
      setLoadingMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="space-y-5">
        {submitError ? (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {submitError}
          </div>
        ) : null}

        {isSuccess ? (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 transition-all duration-200">
            <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-white">
              <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="none" aria-hidden="true">
                <path d="M4.5 10.5l3.2 3.2L15.5 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <span>Files uploaded successfully. Insights are ready below.</span>
          </div>
        ) : null}

        <div>
          <label
            htmlFor="resume-upload"
            className="mb-2 block text-sm font-medium text-[#f0f6fc]"
          >
            Upload Resume (PDF/DOCX)
          </label>
          <input
            ref={resumeInputRef}
            id="resume-upload"
            type="file"
            accept=".pdf,.docx"
            onChange={(event) => handleFileChange(event, 'resume')}
            className="block w-full cursor-pointer rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#c9d1d9] transition-all duration-200 focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff] file:mr-3 file:cursor-pointer file:rounded-lg file:border file:border-[#30363d] file:bg-[#161b22] file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-[#c9d1d9] hover:file:bg-[#21262c]"
          />
          {errors.resume ? (
            <p className="mt-2 text-sm text-red-500">{errors.resume}</p>
          ) : resumeFile ? (
            <p className="mt-2 text-sm text-[#8b949e]">Selected: {resumeFile.name}</p>
          ) : null}
        </div>

        <div>
          <label
            htmlFor="job-description-upload"
            className="mb-2 block text-sm font-medium text-[#f0f6fc]"
          >
            Upload Job Description (PDF/DOCX)
          </label>
          <input
            ref={jdInputRef}
            id="job-description-upload"
            type="file"
            accept=".pdf,.docx"
            onChange={(event) => handleFileChange(event, 'jobDescription')}
            className="block w-full cursor-pointer rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#c9d1d9] transition-all duration-200 focus:border-[#58a6ff] focus:outline-none focus:ring-2 focus:ring-[#58a6ff] file:mr-3 file:cursor-pointer file:rounded-lg file:border file:border-[#30363d] file:bg-[#161b22] file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-[#c9d1d9] hover:file:bg-[#21262c]"
          />
          {errors.jobDescription ? (
            <p className="mt-2 text-sm text-red-500">{errors.jobDescription}</p>
          ) : jobDescriptionFile ? (
            <p className="mt-2 text-sm text-[#8b949e]">
              Selected: {jobDescriptionFile.name}
            </p>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <Button
            type="submit"
            disabled={isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-30"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-90"
                    d="M22 12a10 10 0 00-10-10"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                  ></path>
                </svg>
                Processing...
              </>
            ) : (
              'Submit'
            )}
          </Button>

          <Button
            type="button"
            onClick={handleReset}
            disabled={isLoading}
            variant="secondary"
          >
            Reset and Upload New Files
          </Button>
        </div>

        {isLoading ? (
          <p className="inline-flex items-center gap-2 text-sm text-[#57606a]">
            <span>{loadingMessage}</span>
            <span className="inline-flex items-center gap-0.5" aria-hidden="true">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#2563eb]"></span>
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#2563eb] [animation-delay:120ms]"></span>
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#2563eb] [animation-delay:240ms]"></span>
            </span>
          </p>
        ) : null}
      </div>
    </form>
  )
}

export default FileUpload
