<template>
  <SettingsLayoutBase
    :title="__('Organizations')"
    :description="
      __(
        'Map client organizations to email domains. Tickets from matching domains are auto-classified and picked up by org-specific SLAs.'
      )
    "
  >
    <template #header-actions>
      <Button
        :label="__('New')"
        theme="gray"
        variant="solid"
        icon-left="plus"
        @click="openNewOrg"
      />
    </template>
    <template #content>
      <div v-if="!organizations.loading && organizations.data?.length">
        <div class="flex text-sm text-gray-600 px-2">
          <div class="flex-1">{{ __("Organization") }}</div>
          <div class="flex-1">{{ __("Email Domain") }}</div>
          <div class="flex-1">{{ __("Default SLA") }}</div>
          <div class="w-10"></div>
        </div>
        <hr class="mt-2" />
        <div
          v-for="org in organizations.data"
          :key="org.name"
          class="flex items-center hover:bg-gray-50 rounded py-2 px-2 cursor-pointer"
          @click="editOrg(org)"
        >
          <div class="flex-1 font-medium text-ink-gray-7">{{ org.name }}</div>
          <div class="flex-1 text-ink-gray-6">{{ org.email_domain || "—" }}</div>
          <div class="flex-1 text-ink-gray-6">{{ org.default_sla || "—" }}</div>
          <div class="w-10 flex justify-end">
            <Dropdown
              placement="right"
              :options="dropdownOptions(org)"
              @click.stop
            >
              <Button icon="more-horizontal" variant="ghost" />
            </Dropdown>
          </div>
        </div>
      </div>
      <div
        v-else-if="!organizations.loading"
        class="flex flex-col items-center justify-center gap-4 h-full"
      >
        <div class="text-base font-medium text-ink-gray-6">
          {{ __("No organizations yet") }}
        </div>
        <div class="text-p-sm text-ink-gray-5 max-w-sm text-center">
          {{
            __(
              "Create one and set its email domain (e.g. bmp.com) to auto-classify incoming tickets."
            )
          }}
        </div>
      </div>
    </template>
  </SettingsLayoutBase>

  <Dialog
    v-model="showForm"
    :options="{
      title: editing ? __('Edit organization') : __('New organization'),
      actions: [
        {
          label: __('Save'),
          variant: 'solid',
          onClick: saveOrg,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3">
        <FormControl
          :label="__('Organization Name')"
          v-model="form.organization_name"
          :disabled="editing"
          :placeholder="__('BMP')"
          required
        />
        <FormControl
          :label="__('Email Domain')"
          v-model="form.email_domain"
          :placeholder="__('bmp.com')"
        />
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1">
            {{ __("Default SLA") }}
          </label>
          <Link
            doctype="HD Service Level Agreement"
            :value="form.default_sla"
            @change="(val: string) => (form.default_sla = val)"
            :placeholder="__('Select SLA')"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, markRaw } from "vue";
import { createListResource, Dialog, Dropdown, FormControl, toast } from "frappe-ui";
import { Link } from "@/components";
import { __ } from "@/translation";
import { ConfirmDelete } from "@/utils";
import SettingsLayoutBase from "@/components/layouts/SettingsLayoutBase.vue";
import EditIcon from "@/components/icons/EditIcon.vue";

const organizations = createListResource({
  doctype: "HD Organization",
  cache: ["Organizations"],
  fields: ["name", "email_domain", "default_sla"],
  auto: true,
  orderBy: "modified desc",
  pageLength: 50,
});

const showForm = ref(false);
const editing = ref(false);
const form = ref({
  organization_name: "",
  email_domain: "",
  default_sla: "",
});
const isConfirmingDelete = ref(false);

function openNewOrg() {
  editing.value = false;
  form.value = { organization_name: "", email_domain: "", default_sla: "" };
  showForm.value = true;
}

function editOrg(org: any) {
  editing.value = true;
  form.value = {
    organization_name: org.name,
    email_domain: org.email_domain || "",
    default_sla: org.default_sla || "",
  };
  showForm.value = true;
}

function saveOrg() {
  if (!form.value.organization_name) {
    toast.error(__("Organization name is required"));
    return;
  }
  const action = editing.value
    ? organizations.setValue.submit({
        name: form.value.organization_name,
        email_domain: form.value.email_domain,
        default_sla: form.value.default_sla,
      })
    : organizations.insert.submit({
        organization_name: form.value.organization_name,
        email_domain: form.value.email_domain,
        default_sla: form.value.default_sla,
      });

  Promise.resolve(action).then(
    () => {
      showForm.value = false;
      organizations.reload();
      toast.success(
        editing.value
          ? __("Organization updated")
          : __("Organization created")
      );
    },
    (err: any) => {
      toast.error(err?.messages?.[0] || __("Failed to save"));
    }
  );
}

function dropdownOptions(org: any) {
  return [
    {
      label: __("Edit"),
      icon: markRaw(EditIcon),
      onClick: () => editOrg(org),
    },
    ...ConfirmDelete({
      onConfirmDelete: () => deleteOrg(org),
      isConfirmingDelete,
    }),
  ];
}

function deleteOrg(org: any) {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true;
    return;
  }
  organizations.delete.submit(org.name, {
    onSuccess: () => toast.success(__("Organization deleted")),
  });
}
</script>
