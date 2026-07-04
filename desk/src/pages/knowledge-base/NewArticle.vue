<template>
  <div class="flex flex-col flex-1">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header> </template>
    </LayoutHeader>
    <div class="pt-6 mx-auto w-full max-w-4xl px-5">
      <div class="flex flex-col gap-3 rounded-lg border w-full p-4">
        <div class="flex justify-between items-center mb-3">
          <!-- Author Info -->
          <div class="flex gap-1 items-center flex-1 me-7 max-w-fit">
            <UserAvatar :name="user.name" :expand="true" />
            <span>{{ __("in") }}</span>
            <Link
              class="form-control"
              doctype="HD Article Category"
              :placeholder="__('Select Category')"
              v-model="categoryId"
              :pageLength="100"
              :hide-clear-button="true"
            />
          </div>
          <!-- Action Buttons -->
          <div class="flex gap-2">
            <Button :label="__('Discard')" @click="handleArticleDiscard" />
            <Button
              :label="__('Create')"
              variant="solid"
              @click="handleCreateArticle"
            />
          </div>
        </div>
        <!-- Visibility Controls -->
        <div class="flex flex-col gap-2 border rounded-lg p-3 bg-surface-gray-2">
          <div class="flex items-center gap-3">
            <span class="text-sm font-medium text-ink-gray-7 w-20">{{ __('Visibility') }}</span>
            <FormControl
              type="select"
              :options="[
                { label: __('Public'), value: 'Public' },
                { label: __('Restricted'), value: 'Restricted' },
              ]"
              v-model="visibility"
              size="sm"
              class="w-40"
            />
          </div>
          <div v-if="visibility === 'Restricted'" class="flex items-start gap-3">
            <span class="text-sm font-medium text-ink-gray-7 w-20 pt-1.5">{{ __('Visible To') }}</span>
            <div class="flex-1">
              <div class="flex flex-wrap gap-1.5 mb-2" v-if="selectedOrgs.length">
                <Badge
                  v-for="org in selectedOrgs"
                  :key="org"
                  :label="org"
                  variant="outline"
                  size="md"
                >
                  <template #suffix>
                    <button @click="removeOrg(org)" class="ml-1 text-ink-gray-5 hover:text-ink-gray-8">
                      <LucideX class="w-3 h-3" />
                    </button>
                  </template>
                </Badge>
              </div>
              <Link
                doctype="HD Organization"
                :placeholder="__('Add organization...')"
                :value="''"
                @change="(val: string) => addOrg(val)"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Title -->
        <textarea
          class="w-full resize-none border-0 bg-transparent text-3xl font-bold placeholder-ink-gray-3 p-0 pb-3 border-b border-outline-gray-modals focus:ring-0 focus:border-outline-gray-modals"
          v-model="title"
          :placeholder="__('Title')"
          rows="1"
          wrap="soft"
          maxlength="140"
          autofocus
          @input="
          (e: Event) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = `${target.scrollHeight}px`;
          }
          "
        />
        <!-- Article Content -->
        <TextEditor
          :content="content"
          @change="content = $event"
          :placeholder="__('Write your article here...')"
          editor-class="rounded-b-lg max-w-[unset] prose-sm h-[calc(100vh-340px)] sm:h-[calc(100vh-250px)] overflow-auto"
        >
          <template #bottom>
            <TextEditorFixedMenu
              class="-ms-1 overflow-x-auto w-full"
              :buttons="textEditorMenuButtons"
            />
          </template>
        </TextEditor>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Badge,
  Breadcrumbs,
  FormControl,
  TextEditor,
  TextEditorFixedMenu,
  toast,
  usePageMeta,
} from "frappe-ui";
import { useOnboarding, Link } from "frappe-ui/frappe";
import { computed, ref, watch } from "vue";
import { __ } from "@/translation";

import { LayoutHeader, UserAvatar } from "@/components";
import { useAuthStore } from "@/stores/auth";
import { globalStore } from "@/stores/globalStore";
import { newArticle } from "@/stores/knowledgeBase";
import { useUserStore } from "@/stores/user";
import { Article } from "@/types";
import { textEditorMenuButtons } from "@/utils";
import { useRoute, useRouter } from "vue-router";

const userStore = useUserStore();
const user = userStore.getUser();
const { $dialog } = globalStore();
const router = useRouter();
const route = useRoute();
const { updateOnboardingStep } = useOnboarding("helpdesk");
const { isManager } = useAuthStore();

const title = ref("");
const content = ref("");
const visibility = ref("Public");
const selectedOrgs = ref<string[]>([]);

function addOrg(org: string) {
  if (org && !selectedOrgs.value.includes(org)) {
    selectedOrgs.value.push(org);
  }
}

function removeOrg(org: string) {
  selectedOrgs.value = selectedOrgs.value.filter((o) => o !== org);
}

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
});

const categoryId = ref(props.id || null);
const categoryName = computed(() => (route.query.title as string) || "");

function handleCreateArticle() {
  newArticle.submit(
    {
      title: title.value,
      content: content.value,
      category: categoryId.value,
      visibility: visibility.value,
      visible_to: visibility.value === "Restricted" ? selectedOrgs.value : [],
    },
    {
      onSuccess: (article: Article) => {
        toast.success(__("Article created successfully."));
        if (isManager) {
          updateOnboardingStep("first_article");
        }
        resetState();
        router.push({
          name: "Article",
          params: {
            articleId: article.name,
          },
        });
      },
      onError: (error: string) => {
        toast.error(error);
      },
    }
  );
}
function handleArticleDiscard() {
  if (!title.value && !content.value) {
    router.push({
      name: "AgentKnowledgeBase",
    });
    return;
  }
  $dialog({
    title: __("Discard Article"),
    message: __("Are you sure you want to discard this article?"),
    actions: [
      {
        label: __("Confirm"),
        variant: "solid",
        onClick(close: Function) {
          router.push({
            name: "AgentKnowledgeBase",
          });
          resetState();
          close();
        },
      },
    ],
  });
}

function resetState() {
  title.value = "";
  content.value = "";
}

const breadcrumbs = computed(() => {
  const options: Array<{ label: string; route?: { name: string } }> = [
    {
      label: __("Knowledge Base"),
      route: { name: "AgentKnowledgeBase" },
    },
  ];
  options.push({
    label: __("New Article"),
  });
  return options;
});

usePageMeta(() => {
  return {
    title: __("New Article"),
  };
});
</script>
