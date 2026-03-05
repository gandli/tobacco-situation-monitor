<script setup lang="ts">
import SidebarNav from '@/components/SidebarNav.vue'
import HeaderBar from '@/components/HeaderBar.vue'
</script>

<template>
  <div class="flex h-screen bg-base-100 overflow-hidden">
    <!-- Sidebar -->
    <SidebarNav />
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <HeaderBar />
      <main class="flex-1 overflow-auto p-4 md:p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>