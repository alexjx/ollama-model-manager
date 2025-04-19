<template>
    <Dialog v-model:visible="visible" header="Copy Model" :modal="true" :style="{ width: '50vw', 'z-index': '1000' }">
        <div class="flex flex-col gap-4 p-fluid">
            <div class="field">
                <label for="targetName" class="block">New Model Name</label>
                <InputText id="targetName" v-model="targetName"
                    placeholder="Enter new model name"
                    :class="['w-full', { 'p-invalid': !validation.targetNameValid }]" />
                <small v-if="!validation.targetNameValid" class="p-error">Model name is required</small>
            </div>
            <div class="field">
                <label for="parameters" class="block">Parameters</label>
                <Textarea id="parameters" v-model="parameters" :autoResize="true" rows="5"
                    placeholder="Enter one parameter per line in key=value format"
                    :class="['w-full', { 'p-invalid': !validation.parametersValid }]" />
                <small v-if="validation.error" class="p-error">{{ validation.error }}</small>
            </div>
            <div class="field">
                <label for="template" class="block">Template</label>
                <Textarea id="template" v-model="template" :autoResize="true" rows="5"
                    placeholder="Enter custom template" class="w-full" />
            </div>
        </div>
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" @click="visible = false" text />
            <Button label="Copy" icon="pi pi-check" @click="handleCopy" autofocus :disabled="!validation.isValid" />
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch, reactive } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'

const emit = defineEmits(['copied'])

const toast = useToast()
const visible = ref(false)
const sourceName = ref('')
const targetName = ref('')
const parameters = ref('')
const template = ref('')

const validation = reactive({
    error: '',
    isValid: false,
    targetNameValid: false,
    parametersValid: true
})

const validateForm = () => {
    // Validate target name
    validation.targetNameValid = targetName.value.trim().length > 0

    // Validate parameters
    validation.error = ''
    validation.parametersValid = true

    const text = parameters.value.trim()
    if (!text) {
        validation.parametersValid = true
    } else {
        const lines = text.split('\n')
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim()
            if (!line) continue

            const firstEqual = line.indexOf('=')
            if (firstEqual <= 0) {
                validation.error = `Line ${i+1}: Missing key before '='`
                validation.parametersValid = false
                break
            }
            if (firstEqual === line.length - 1) {
                validation.error = `Line ${i+1}: Missing value after '='`
                validation.parametersValid = false
                break
            }
            const key = line.slice(0, firstEqual).trim()
            if (!key) {
                validation.error = `Line ${i+1}: Key cannot be empty`
                validation.parametersValid = false
                break
            }
            const value = line.slice(firstEqual + 1).trim()
            if (!value) {
                validation.error = `Line ${i+1}: Value cannot be empty`
                validation.parametersValid = false
                break
            }
        }
    }

    // Overall form validity
    validation.isValid = validation.targetNameValid && validation.parametersValid
}

watch([parameters, targetName], validateForm, { immediate: true })

function parseParameters() {
    if (!parameters.value.trim() || !validation.parametersValid) return undefined

    const params = {}
    const lines = parameters.value.split('\n')

    for (const line of lines) {
        const trimmedLine = line.trim()
        if (!trimmedLine) continue

        const firstEqual = trimmedLine.indexOf('=')
        const key = trimmedLine.slice(0, firstEqual).trim()
        const value = trimmedLine.slice(firstEqual + 1).trim()

        // Only add parameters that pass validation
        if (firstEqual > 0 && key && value) {
            params[key] = value
        }
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
            detail: error.response?.data?.detail || 'Failed to copy model',
            life: 3000
        })
    }
}

defineExpose({ open })
</script>
