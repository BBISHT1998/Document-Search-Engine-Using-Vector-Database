import axios from 'axios'

const API_BASE ='https://docsearch-baegbbcsenhcfrg8.centralindia-01.azurewebsites.net' ///api/v1

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

// Attach JWT token to every request if present
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
client.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client
