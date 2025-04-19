<template>
    <div class="flex flex-col justify-start">
        <div v-if="model" class="px-12">
            <div class="py-8 text-primary text-2xl">{{ model.name }}</div>
            <Card class="my-4">
                <template #title>Parameters</template>
                <template #content>
                    <div v-for="(param, index) in model.parameters" :key="index">
                        <div>{{ param }}</div>
                    </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()
const model = ref(null)

onMounted(async () => {
    try {
        const response = await axios.get(`/api/models/${route.params.name}`)
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
