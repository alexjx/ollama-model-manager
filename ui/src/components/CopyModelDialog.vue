<template>
    <Dialog v-model:visible="visible" header="Copy Model" :modal="true" :style="{ width: '50vw', 'z-index': '1000' }">
        <div class="flex flex-col gap-4 p-fluid">
            <div class="field">
                <label for="targetName" class="block">New Model Name</label>
                <InputText id="targetName" v-model="targetName" placeholder="Enter new model name"
                    :class="['w-full', { 'p-invalid': !targetName }]" />
                <small v-if="!targetName" class="p-error">Model name is required</small>
            </div>
            <div class="field">
                <label for="parameters" class="block">Parameters</label>
                <Textarea id="parameters" v-model="parameters" :autoResize="true" rows="5"
                    placeholder="Enter one parameter per line in key=value format" :class="['w-full']" />
            </div>
            <div class="field">
                <label for="template" class="block">Template</label>
                <Textarea id="template" v-model="template" :autoResize="true" rows="5"
                    placeholder="Enter custom template" class="w-full" />
            </div>
        </div>
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" @click="visible = false" text />
            <Button label="Copy" icon="pi pi-check" @click="handleCopy" autofocus />
        </template>
    </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'

const emit = defineEmits(['copied'])

const toast = useToast()
const visible = ref(false)
const sourceName = ref('')
const targetName = ref('')
const parameters = ref('')
const template = ref('')

function parseParameters() {
    const params = {}
    const lines = parameters.value.split('\n')

    for (const line of lines) {
        const trimmedLine = line.trim()
        if (!trimmedLine) continue

        const firstEqual = trimmedLine.indexOf('=')
        // raise error if '=' is not found
        if (firstEqual < 0) {
            throw new Error(`Invalid parameter format in line ${trimmedLine}.`)
        }

        const key = trimmedLine.slice(0, firstEqual).trim()
        const value = trimmedLine.slice(firstEqual + 1).trim()
        params[key] = value
    }

    return Object.keys(params).length > 0 ? params : undefined
}

function open(modelName) {
    sourceName.value = modelName
    visible.value = true
    targetName.value = `${modelName}-copy`
    parameters.value = ''
    template.value = ''
}

function handleCopy() {
    try {
        const params = parseParameters()
        const templ = template.value || undefined

        axios.post('/api/models/copy', {
            model: targetName.value,
            base: sourceName.value,
            parameters: params,
            template: templ
        }).then(() => {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: `Model ${targetName.value} created`,
                life: 3000
            })
            emit('copied')
            visible.value = false
        })
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to copy model: ' + error.message,
            life: 3000
        })
    }
}

defineExpose({ open })
</script>
