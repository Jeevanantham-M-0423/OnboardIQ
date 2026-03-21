import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
})

export async function uploadFiles(resume, jobDescription) {
  const formData = new FormData()
  formData.append('resume', resume)
  formData.append('job_description', jobDescription)

  const response = await apiClient.post('/upload', formData)
  return response.data
}

export default apiClient
