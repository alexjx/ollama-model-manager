<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="py-4 px-8 shadow-md">
      <div class="flex justify-start items-center">
        <Button text size="large" @click="goHome">Ollama Model Manager</Button>
      </div>
    </header>
    <main class="flex-1 p-8 bg-surface-ground">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Toast position="bottom-right" />
  </div>
</template>
