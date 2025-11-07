import { reactive } from 'vue'

export const userStore = reactive({
  user: JSON.parse(localStorage.getItem('user')) || null,

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },

  logout() {
    this.user = null
    localStorage.removeItem('user')
  }
})
