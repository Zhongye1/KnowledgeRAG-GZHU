<template>
  <div class="file-management p-6 max-h-[95vh] overflow-auto">
    <t-card class="shadow-lg">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">文件管理</h1>
        <t-button theme="primary" @click="refreshData">
          <template #icon>
            <refresh-icon />
          </template>
          刷新
        </t-button>
      </div>

      <t-loading :loading="loading">
        <t-tabs v-model="activeTab" class="file-tabs" @change="handleTabChange">
          <t-tab-panel value="all" label="全部文档">
            <t-table :data="allDocuments" :columns="columns" row-key="id" :pagination="pagination"
              @page-change="onPageChange" @change="onTableChange" class="mt-4">
              <template #file_name="{ row }">
                <span class="font-medium">{{ row.file_name }}</span>
              </template>

              <template #file_type="{ row }">
                <t-tag variant="light" :theme="getFileTypeTheme(row.file_type)">
                  {{ row.file_type.toUpperCase() }}
                </t-tag>
              </template>

              <template #file_size="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>

              <template #upload_time="{ row }">
                {{ formatDateTime(row.upload_time) }}
              </template>

              <template #status="{ row }">
                <t-tag v-if="row.status === 'enabled'" variant="light" theme="success">启用</t-tag>
                <t-tag v-else variant="light" theme="danger">禁用</t-tag>
              </template>

              <template #action="{ row }">
                <t-space>
                  <t-button variant="text" theme="primary" @click="previewDocument(row)">
                    预览
                  </t-button>
                  <t-button variant="text" theme="danger" @click="deleteDocument(row)">
                    删除
                  </t-button>
                </t-space>
              </template>
            </t-table>
          </t-tab-panel>

          <t-tab-panel v-for="folder in folders" :key="folder.folder_path" :value="folder.folder_path"
            :label="`${folder.folder_name} (${folder.document_count})`">
            <div class="folder-info mb-4 p-4 bg-gray-50 rounded-lg">
              <p><span class="font-medium">文件夹:</span> {{ folder.folder_name }}</p>
              <p><span class="font-medium">文档数量:</span> {{ folder.document_count }}</p>
              <p><span class="font-medium">总大小:</span> {{ formatFileSize(folder.total_size) }}</p>
            </div>

            <t-table v-if="folder.document_count > 0" :data="folder.documents" :columns="folderColumns" row-key="id">
              <template #file_name="{ row }">
                <span class="font-medium">{{ row.file_name }}</span>
              </template>

              <template #file_type="{ row }">
                <t-tag variant="light" :theme="getFileTypeTheme(row.file_type)">
                  {{ row.file_type.toUpperCase() }}
                </t-tag>
              </template>

              <template #file_size="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>

              <template #upload_time="{ row }">
                {{ formatDateTime(row.upload_time) }}
              </template>

              <template #status="{ row }">
                <t-tag v-if="row.status === 'enabled'" variant="light" theme="success">启用</t-tag>
                <t-tag v-else variant="light" theme="danger">禁用</t-tag>
              </template>

              <template #action="{ row }">
                <t-space>
                  <t-button variant="text" theme="primary" @click="previewDocument(row)">
                    预览
                  </t-button>
                  <t-button variant="text" theme="danger" @click="deleteDocument(row)">
                    删除
                  </t-button>
                </t-space>
              </template>
            </t-table>

            <t-empty v-else description="该文件夹暂无文档" class="mt-8" />
          </t-tab-panel>
        </t-tabs>
      </t-loading>
    </t-card>

    <!-- 预览对话框 -->
    <t-dialog v-model:visible="previewDialogVisible" :header="previewDocumentData?.file_name" width="800px"
      :on-close="closePreviewDialog">
      <t-loading :loading="previewLoading">
        <div class="preview-content">
          <div v-if="previewDocumentDetail && previewDocumentDetail.file_type === 'txt'" class="txt-preview">
            <pre class="whitespace-pre-wrap">{{ previewDocumentDetail.content_preview }}</pre>
          </div>
          <div v-else-if="previewDocumentDetail && previewDocumentDetail.file_type === 'md'" class="md-preview">
            <div v-html="renderMarkdown(previewDocumentDetail.content_preview)"></div>
          </div>
          <div v-else-if="previewDocumentDetail && ['doc', 'docx', 'pdf'].includes(previewDocumentDetail.file_type)"
            class="doc-preview">
            <pre class="whitespace-pre-wrap">{{ previewDocumentDetail.content_preview }}</pre>
          </div>
          <div v-else-if="previewDocumentDetail && ['xls', 'xlsx'].includes(previewDocumentDetail.file_type)"
            class="file-preview">
            <t-alert theme="info" :message="`这是 ${previewDocumentDetail.file_type.toUpperCase()} 文件，无法直接预览内容。`" />
          </div>
          <div v-else-if="previewDocumentDetail">
            <t-alert theme="warning" message="该文件类型暂不支持预览" />
          </div>
          <div v-else>
            <t-empty description="暂无预览内容" />
          </div>
        </div>
      </t-loading>

      <template #footer>
        <t-button @click="closePreviewDialog">关闭</t-button>
      </template>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  RefreshIcon
} from 'tdesign-icons-vue-next';
import { MessagePlugin, DialogPlugin } from 'tdesign-vue-next';
import axios from 'axios';
import { marked } from 'marked';
import API_ENDPOINTS from '@/utils/apiConfig';



interface Document {
  id: number;
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  upload_time: string;
  status: string;
}

interface Folder {
  folder_path: string;
  folder_name: string;
  document_count: number;
  total_size: number;
  documents: Document[];
}

interface ApiResponse {
  folders: Folder[];
  total_folders: number;
  total_documents: number;
  total_size: number;
}

interface DocumentPreviewResponse {
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  upload_time: string;
  content_preview: string;
  status: string;
}

// 响应式数据
const loading = ref(false);
const previewLoading = ref(false);
const activeTab = ref('all');
const folders = ref<Folder[]>([]);
const allDocuments = ref<Document[]>([]);
const previewDialogVisible = ref(false);
const previewDocumentData = ref<Document | null>(null);
const previewDocumentDetail = ref<DocumentPreviewResponse | null>(null);

// 分页配置
const pagination = ref({
  defaultPageSize: 10,
  total: 0,
  defaultCurrent: 1,
});

// 表格列定义 - 全部文档
const columns = ref([
  { colKey: 'file_name', title: '文件名', width: '200px' },
  { colKey: 'file_type', title: '类型', width: '100px' },
  { colKey: 'file_size', title: '大小', width: '120px' },
  { colKey: 'upload_time', title: '上传时间', width: '200px' },
  { colKey: 'status', title: '状态', width: '100px' },
  { colKey: 'action', title: '操作', width: '150px', fixed: 'right' },
]);

// 表格列定义 - 文件夹内文档
const folderColumns = ref([
  { colKey: 'file_name', title: '文件名' },
  { colKey: 'file_type', title: '类型' },
  { colKey: 'file_size', title: '大小' },
  { colKey: 'upload_time', title: '上传时间' },
  { colKey: 'status', title: '状态' },
  { colKey: 'action', title: '操作', fixed: 'right' },
]);

// 格式化文件大小
const formatFileSize = (size: number): string => {
  if (size < 1024) {
    return size + ' B';
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB';
  } else if (size < 1024 * 1024 * 1024) {
    return (size / (1024 * 1024)).toFixed(2) + ' MB';
  } else {
    return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  }
};

// 根据文件类型返回主题色
const getFileTypeTheme = (fileType: string): string => {
  switch (fileType.toLowerCase()) {
    case 'pdf':
      return 'danger';
    case 'txt':
      return 'success';
    case 'doc':
    case 'docx':
      return 'primary';
    case 'xls':
    case 'xlsx':
      return 'warning';
    default:
      return 'default';
  }
};

// 格式化日期时间
const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString('zh-CN');
};

// 渲染Markdown
const renderMarkdown = (markdown: string) => {
  return marked(markdown);
};

// 刷新数据
const refreshData = () => {
  fetchData();
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    const response = await axios.get<ApiResponse>(API_ENDPOINTS.FILES.ALL_DOCUMENTS);
    folders.value = response.data.folders;

    // 合并所有文档到一个数组
    allDocuments.value = response.data.folders
      .flatMap(folder => folder.documents)
      .sort((a, b) => new Date(b.upload_time).getTime() - new Date(a.upload_time).getTime());

    pagination.value.total = allDocuments.value.length;
    MessagePlugin.success('数据加载成功');
  } catch (error) {
    console.error('获取文档数据失败:', error);
    MessagePlugin.error('获取文档数据失败');
  } finally {
    loading.value = false;
  }
};

// 处理标签页切换
const handleTabChange = () => {
  // 标签页切换逻辑
};

// 分页变化
const onPageChange = (pageInfo: { current: number; pageSize: number }) => {
  pagination.value = {
    ...pagination.value,
    ...pageInfo,
  };
};

// 表格变化
const onTableChange = (changeParams: any, triggerAndData: any) => {
  // 表格变化处理逻辑
};

// 预览文档
const previewDocument = async (document: Document) => {
  previewDocumentData.value = document;
  previewDialogVisible.value = true;
  previewLoading.value = true;

  try {
    const response = await axios.get<DocumentPreviewResponse>(
      API_ENDPOINTS.FILES.DOCUMENT_PREVIEW(document.file_path)
    );
    previewDocumentDetail.value = response.data;
  } catch (error) {
    console.error('预览文档失败:', error);
    MessagePlugin.error('预览文档失败');
    previewDocumentDetail.value = null;
  } finally {
    previewLoading.value = false;
  }
};

// 关闭预览对话框
const closePreviewDialog = () => {
  previewDialogVisible.value = false;
  setTimeout(() => {
    previewDocumentData.value = null;
    previewDocumentDetail.value = null;
  }, 300); // 延迟清除数据，确保关闭动画完成
};

// 删除文档
// 删除文档
const deleteDocument = (document: Document) => {
  const confirmDialog = DialogPlugin.confirm({
    header: '确认删除',
    body: `确定要删除文件 "${document.file_name}" 吗？此操作不可恢复。`,
    confirmBtn: {
      theme: 'danger',
      content: '删除'
    },
    cancelBtn: {
      theme: 'default',
      content: '取消'
    },
    onConfirm: () => {
      performDelete(document);
      confirmDialog.destroy();
    },
    onClose: () => {
      confirmDialog.destroy();
    },
    onCancel: () => {
      confirmDialog.destroy();
    }
  });
};

// 执行删除操作
const performDelete = async (document: Document) => {
  try {
    await axios.delete(
      API_ENDPOINTS.FILES.DELETE_DOCUMENT(document.file_path)
    );

    MessagePlugin.success(`文件 "${document.file_name}" 已删除`);
    // 重新加载数据
    fetchData();
  } catch (error) {
    console.error('删除文档失败:', error);
    MessagePlugin.error('删除文档失败');
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.file-management {
  height: 100%;
  background-color: #f5f7fa;
}

.folder-info {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.file-tabs .t-tabs__header) {
  background-color: #ffffff;
  padding: 0 16px;
  border-radius: 8px 8px 0 0;
}

:deep(.t-table) {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.t-table .t-table__content) {
  border-radius: 8px;
}

.preview-content {
  min-height: 300px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 16px;
}

.txt-preview,
.md-preview {
  white-space: pre-wrap;
  word-break: break-word;
}

.txt-preview {
  font-family: 'Courier New', Courier, monospace;
}
</style>