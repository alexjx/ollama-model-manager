import { createApp } from 'vue'
import './style.css'
import PrimeVue from 'primevue/config'
import App from './App.vue'
import router from './router'
import Aura from '@primeuix/themes/aura'
import axios from 'axios'

// Configure axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

// Create app instance
const app = createApp(App)

// Make axios instance available to all components
app.config.globalProperties.$api = apiClient

// PrimeVue Components
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'
import ProgressSpinner from 'primevue/progressspinner'

// PrimeVue setup
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  }
})

// Plugins
app.use(router)
app.use(ToastService)
app.use(ConfirmationService)

// Register components globally
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('InputText', InputText)
app.component('Button', Button)
app.component('Card', Card)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('ProgressSpinner', ProgressSpinner)

// Mount app
app.mount('#app')
