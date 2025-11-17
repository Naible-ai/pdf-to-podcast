import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Templates
  getTemplates: async () => {
    const { data } = await apiClient.get('/templates')
    return data
  },

  getTemplate: async (templateId: string) => {
    const { data } = await apiClient.get(`/templates/${templateId}`)
    return data
  },

  // Podcast Creation
  createPodcast: async (formData: FormData) => {
    const { data } = await axios.post('/process_pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  // Status
  getStatus: async (jobId: string, userId: string = 'demo-user') => {
    const { data } = await axios.get(`/status/${jobId}?userId=${userId}`)
    return data
  },

  // Export
  exportPodcast: async (jobId: string, format: string, userId: string = 'demo-user') => {
    const response = await apiClient.get(`/podcast/${jobId}/export/${format}?userId=${userId}`, {
      responseType: 'blob',
    })
    return response.data
  },

  getExportFormats: async (jobId: string) => {
    const { data } = await apiClient.get(`/podcast/${jobId}/export-formats`)
    return data
  },

  // Editing
  getVersions: async (jobId: string, userId: string = 'demo-user') => {
    const { data } = await apiClient.get(`/podcast/${jobId}/versions?userId=${userId}`)
    return data
  },

  getVersion: async (jobId: string, versionId: string, userId: string = 'demo-user') => {
    const { data } = await apiClient.get(`/podcast/${jobId}/version/${versionId}?userId=${userId}`)
    return data
  },

  applyEdit: async (jobId: string, edit: any, userId: string = 'demo-user') => {
    const { data} = await apiClient.post(`/podcast/${jobId}/edit?userId=${userId}`, edit)
    return data
  },

  // Saved Podcasts
  getSavedPodcasts: async (userId: string = 'demo-user') => {
    const { data } = await axios.get(`/saved_podcasts?userId=${userId}`)
    return data
  },

  getPodcastAudio: async (jobId: string, userId: string = 'demo-user') => {
    const { data } = await axios.get(`/output/${jobId}?userId=${userId}`, {
      responseType: 'blob',
    })
    return data
  },
}

export default api
