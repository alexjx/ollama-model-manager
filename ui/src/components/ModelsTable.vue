<template>
  <div class="pt-2">
    <DataTable :value="models" :loading="loading" :pt="{ 'column': { 'bodyCell': { class: 'my-cell-padding' } } }">
      <Column field="name" header="Name" sortable>
        <template #body="{ data }">
          <router-link :to="`/models/${data.name}`" class="text-primary">
            {{ data.name }}
          </router-link>
        </template>
      </Column>
      <Column field="size" header="Size (GB)" sortable>
        <template #body="{ data }">
          {{ (data.size / (1024 * 1024 * 1024)).toFixed(2) }}
        </template>
      </Column>
      <Column field="modified_at" header="Modified" sortable>
        <template #body="{ data }">
          {{ new Date(data.modified_at).toLocaleString() }}
        </template>
      </Column>
      <Column header="Actions">
        <template #body="{ data }">
          <Button class="text-white" icon="pi pi-trash" severity="danger" @click="confirmDelete(data.name)"
            v-tooltip="'Delete model'" />
          <Button icon="pi pi-copy" severity="info" @click="showCopyDialog(data.name)" v-tooltip="'Copy model'"
            class="ml-2 text-white" />
        </template>
      </Column>
    </DataTable>

    <ConfirmPopup />
    <Toast />
    <CopyModelDialog ref="copyDialog" @copied="fetchModels" />
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import CopyModelDialog from './CopyModelDialog.vue'
import ConfirmPopup from 'primevue/confirmpopup'

const models = ref([])
const loading = ref(false)
const toast = useToast()
const deleteConfirm = useConfirm()


onMounted(async () => {
  await fetchModels()
})

const instance = getCurrentInstance()

async function fetchModels() {
  try {
    loading.value = true
    const response = await instance.appContext.config.globalProperties.$api.get('/models')
    models.value = response.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch models',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

function confirmDelete(modelName) {
  deleteConfirm.require({
    message: `Are you sure you want to delete ${modelName}?`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteModel(modelName)
  })
}

async function deleteModel(modelName) {
  try {
    // model name might contain '/', we need to encode it
    const encodedModelName = encodeURIComponent(modelName)
    await instance.appContext.config.globalProperties.$api.delete(`/models/${encodedModelName}`)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Model ${modelName} deleted`,
      life: 3000
    })
    await fetchModels()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete model',
      life: 3000
    })
  }
}

const copyDialog = ref()

function showCopyDialog(modelName) {
  copyDialog.value.open(modelName)
}
</script>

<style>
.my-cell-padding {
  padding: 0.25rem !important;
}
</style>
