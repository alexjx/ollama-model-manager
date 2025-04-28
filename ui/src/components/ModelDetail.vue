<template>
    <div class="flex flex-col justify-start">
        <div v-if="model" class="px-12">
            <div class="py-8 text-primary text-2xl">{{ model.name }}</div>
            <Card class="my-4">
                <template #title>Parameters</template>
                <template #content>
                    <DataTable :value="model.parameters" size="small" tableStyle="min-width: 50rem">
                        <Column field="key" header="Key" />
                        <Column field="value" header="Value" />
                    </DataTable>
                </template>
            </Card>
            <Card class="my-4">
                <template #title>Template</template>
                <template #content>
                    <pre>{{ model.template }}</pre>
                </template>
            </Card>
        </div>
        <div v-else>
            <ProgressSpinner />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const route = useRoute()
const router = useRouter()

function handleKeyDown(e) {
  if (e.key === 'Escape') {
    router.push('/')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
const toast = useToast()
const model = ref(null)

onMounted(async () => {
    try {
        const instance = getCurrentInstance()
        const modelName = decodeURIComponent(route.params.name)
        const encodedModelName = encodeURIComponent(modelName)
        const response = await instance.appContext.config.globalProperties.$api.get(`/models/${encodedModelName}`)
        model.value = response.data
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load model details',
            life: 3000
        })
    }
})
</script>

<style scoped>
pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: monospace;
}
</style>
