import { createRouter, createWebHistory } from 'vue-router'
import ModelsTable from '../components/ModelsTable.vue'
import ModelDetail from '../components/ModelDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Models',
    component: ModelsTable
  },
  {
    path: '/models/:name',
    name: 'ModelDetail',
    component: ModelDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
