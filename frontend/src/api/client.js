import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

/**
 * Upload file and start extraction.
 * @param {File}     file           - PDF, EPUB or TXT file
 * @param {string[]} selectedTasks  - list of task IDs
 * @param {boolean}  scientificMode - use Gemini Vision for formulas/matrices
 * Returns { job_id, status, file, scientific_mode }
 */
export async function createJob(file, selectedTasks, scientificMode = false) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('tasks', selectedTasks.join(','))
  formData.append('scientific_mode', scientificMode ? 'true' : 'false')

  const res = await api.post('/jobs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/** Poll job status. Returns the full job state object. */
export async function getJob(jobId) {
  const res = await api.get(`/jobs/${jobId}`)
  return res.data
}

/** Returns the download URL for a given asset type */
export function getDownloadUrl(jobId, type) {
  // type: 'markdown' | 'json' | 'transcript'
  return `/api/jobs/${jobId}/download/${type}`
}
