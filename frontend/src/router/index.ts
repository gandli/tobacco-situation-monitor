import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { title: '态势总览' }
    },
    {
      path: '/intels',
      name: 'intels',
      component: () => import('@/views/IntelsView.vue'),
      meta: { title: '情报列表' }
    },
    {
      path: '/intels/:id',
      name: 'intel-detail',
      component: () => import('@/views/IntelDetailView.vue'),
      meta: { title: '情报详情' }
    },
    {
      path: '/sources',
      name: 'sources',
      component: () => import('@/views/SourcesView.vue'),
      meta: { title: '数据源管理' }
    },
  ]
})

export default router