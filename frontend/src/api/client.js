import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

/** Upload file and start extraction. Returns { job_id, status, file } */
export async function createJob(file, selectedTasks) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('tasks', selectedTasks.join(','))
  const res = await api.post('/jobs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/** Poll job status. Returns the job state object. */
export async function getJob(jobId) {
  const res = await api.get(`/jobs/${jobId}`)
  return res.data
}

/** Returns the download URL for markdown or json */
export function getDownloadUrl(jobId, type) {
  return `/api/jobs/${jobId}/download/${type}`
}
