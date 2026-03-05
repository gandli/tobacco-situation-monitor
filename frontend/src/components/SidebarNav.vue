<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', icon: 'dashboard', label: '态势总览' },
  { path: '/intels', icon: 'document', label: '情报列表' },
  { path: '/sources', icon: 'cloud', label: '数据源' },
]

const currentPath = computed(() => route.path)
</script>

<template>
  <aside class="w-16 md:w-64 bg-neutral border-r border-neutral-content/10 flex flex-col">
    <!-- Logo -->
    <div class="h-16 flex items-center justify-center md:justify-start md:px-4 border-b border-neutral-content/10">
      <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
        <svg class="w-5 h-5 text-primary-content" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <span class="hidden md:block ml-3 text-sm font-semibold text-neutral-content">态势监测</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-4">
      <ul class="menu menu-sm bg-transparent px-2 gap-1">
        <li v-for="item in navItems" :key="item.path">
          <router-link 
            :to="item.path"
            :class="{ 'active': currentPath === item.path }"
            class="flex items-center gap-3"
          >
            <!-- Dashboard Icon -->
            <svg v-if="item.icon === 'dashboard'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            <!-- Document Icon -->
            <svg v-else-if="item.icon === 'document'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <!-- Cloud Icon -->
            <svg v-else-if="item.icon === 'cloud'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            <span class="hidden md:inline">{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Footer -->
    <div class="p-4 border-t border-neutral-content/10">
      <div class="text-xs text-neutral-content/50 text-center md:text-left">
        <span class="hidden md:inline">TSM v0.1</span>
        <span class="md:hidden">v0.1</span>
      </div>
    </div>
  </aside>
</template>