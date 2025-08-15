<template>
    <div class="graph-container flex flex-col">
        <div class="self-start mb-4">
            <button @click="fetchGraphData"
                class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded transition duration-200 ease-in-out"
                :disabled="isLoading">
                <span v-if="isLoading" class="flex items-center">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg"
                        fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>
                    加载中...
                </span>
                <span v-else>生成知识图谱</span>
            </button>
        </div>
        <div v-if="errorMessage" class="text-red-500 mb-4 p-3 bg-red-50 border border-red-200 rounded self-start">{{
            errorMessage
            }}</div>
        <div id="sigma-container" class="w-[400px] h-[300px] bg-white rounded-lg border border-[#d9d9d9] shadow-md">
        </div>
    </div>
</template>

<script setup lang="ts">

import { useRoute } from 'vue-router';
import API_ENDPOINTS from '@/utils/apiConfig';


const route = useRoute();

// 定义props以接收知识库ID
const props = defineProps({
    kbId: {
        type: String,
        default: ''
    }
});


import { onMounted, ref } from 'vue';
import chroma from "chroma-js";
import Graph from "graphology";
import ForceSupervisor from "graphology-layout-force/worker";
import Sigma from "sigma";
import { v4 as uuid } from "uuid";

// 类型定义
interface GraphNode {
    id: string;
    label?: string;
    type?: string;
    x?: number;
    y?: number;
    size?: number;
    color?: string;
}

interface GraphEdge {
    source: string;
    target: string;
    label?: string;
}

interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

interface ApiResponse {
    message: string;
    graph_data: GraphData;
}

// 状态变量
let renderer: Sigma | null = null;
let layout: ForceSupervisor | null = null;
let graph = new Graph({ multi: true });

// 响应式状态
const isLoading = ref<boolean>(false);
const errorMessage = ref<string>('');

// 拖拽状态
let draggedNode: string | null = null;
let isDragging = false;

// 实现获取图数据的函数
const fetchGraphData = async (): Promise<void> => {
    isLoading.value = true;
    errorMessage.value = '';

    try {
        // 确保我们有有效的知识库ID
        const folderPath = props.kbId || route.params.id;

        // 检查folderPath是否有效
        if (!folderPath) {
            throw new Error('未提供有效的知识库ID');
        }

        // 使用新的API端点并传递知识库ID
        console.log('Fetching graph data for folder ID:', folderPath);
        const response = await fetch(API_ENDPOINTS.KNOWLEDGE_GRAPH.PROCESS_KNOWLEDGE_BASE, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                // 从props或路由参数获取知识库ID
                "folder_path": folderPath
            })
        });

        if (!response.ok) {
            throw new Error(`API请求失败：${response.statusText}`);
        }

        const data = await response.json() as ApiResponse[];

        if (data && data.length > 0 && data[0].graph_data) {
            updateGraph(data[0].graph_data);
        } else {
            errorMessage.value = '返回的数据格式不正确/知识库为空';
        }
    } catch (error) {
        console.error('获取图数据出错:', error);
        errorMessage.value = `获取图数据出错: ${error instanceof Error ? error.message : String(error)}`;
    } finally {
        isLoading.value = false;
    }
};


// 更新图谱的函数
const updateGraph = (graphData: GraphData): void => {
    if (!graphData || !graphData.nodes || !graphData.edges) {
        console.error('无效的图谱数据');
        return;
    }

    // 清空现有图谱
    graph.clear();

    // 为节点分配随机位置和颜色
    const nodeColors: Record<string, string> = {
        '人物': '#FF6B6B',
        '地点': '#4ECDC4',
        '组织': '#45B7D1',
        '概念': '#FFD166',
        '事件': '#06D6A0',
        '默认': '#90D8FF'
    };

    // 添加节点
    graphData.nodes.forEach((node, index) => {
        // 计算节点在圆形布局中的位置
        const angle = (index / graphData.nodes.length) * 2 * Math.PI;
        const radius = 10;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;

        const nodeType = node.type || '默认';
        const color = nodeColors[nodeType] || nodeColors['默认'];

        graph.addNode(node.id, {
            x: x,
            y: y,
            size: 20,
            color: color,
            label: node.label + "//" + node.id,
        });
    });

    // 添加边
    // 添加边
    graphData.edges.forEach((edge, index) => {
        if (graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
            try {
                graph.addEdge(edge.source, edge.target, {
                    label: edge.label || '',
                    size: 2,
                    forceLabel: true,
                    // 添加唯一标识，确保多重边可区分
                    edgeId: `${edge.source}-${edge.target}-${index}`
                });
            } catch (error) {
                console.warn(`添加边时出错 (${edge.source} -> ${edge.target}): `, error);
            }
        }
    });

    // 重新应用力导向布局
    if (layout) {
        layout.kill();
    }

    layout = new ForceSupervisor(graph, { isNodeFixed: (_, attr) => attr.highlighted });
    layout.start();

    // 如果已有渲染器，需要先销毁它
    if (renderer) {
        renderer.kill();
        renderer = null;
    }

    // 重新创建渲染器
    const container = document.getElementById("sigma-container");
    if (container) {
        renderer = new Sigma(graph, container, {
            minCameraRatio: 0.5,
            maxCameraRatio: 2,
            renderEdgeLabels: true,
            edgeLabelSize: 12,
            edgeLabelWeight: "bold"
        });

        // 重新绑定事件
        bindEvents();
    }
};

// 封装事件绑定函数
const bindEvents = (): void => {
    if (!renderer) return;

    // On mouse down on a node
    renderer.on("downNode", (e) => {
        isDragging = true;
        draggedNode = e.node;
        graph.setNodeAttribute(draggedNode, "highlighted", true);
        if (renderer && !renderer.getCustomBBox()) renderer.setCustomBBox(renderer.getBBox());
    });

    // On mouse move, if the drag mode is enabled, we change the position of the draggedNode
    renderer.on("moveBody", ({ event }) => {
        if (!isDragging || !draggedNode || !renderer) return;

        // Get new position of node
        const pos = renderer.viewportToGraph(event);

        graph.setNodeAttribute(draggedNode, "x", pos.x);
        graph.setNodeAttribute(draggedNode, "y", pos.y);

        // Prevent sigma to move camera:
        event.preventSigmaDefault();
        event.original.preventDefault();
        event.original.stopPropagation();
    });

    // On mouse up, we reset the dragging mode
    const handleUp = () => {
        if (draggedNode) {
            graph.removeNodeAttribute(draggedNode, "highlighted");
        }
        isDragging = false;
        draggedNode = null;
    };

    renderer.on("upNode", handleUp);
    renderer.on("upStage", handleUp);

    // When clicking on the stage, we add a new node and connect it to the closest node
    renderer.on("clickStage", ({ event }) => {
        if (!renderer) return;

        const coordForGraph = renderer.viewportToGraph({ x: event.x, y: event.y });

        // We create a new node
        const node = {
            ...coordForGraph,
            size: 10,
            color: chroma.random().hex(),
            label: "新节点"
        };

        // Searching the two closest nodes to auto-create an edge to it
        const closestNodes = graph
            .nodes()
            .map((nodeId) => {
                const attrs = graph.getNodeAttributes(nodeId);
                const distance = Math.pow(node.x - attrs.x, 2) + Math.pow(node.y - attrs.y, 2);
                return { nodeId, distance };
            })
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 2);

        // We register the new node into graphology instance
        const id = uuid();
        graph.addNode(id, node);

        // We create the edges
        closestNodes.forEach((e) => graph.addEdge(id, e.nodeId, { label: "关联" }));
    });
};

// 生命周期钩子
onMounted(() => {
    // 在DOM渲染后再获取容器元素
    const container = document.getElementById("sigma-container");

    if (!container) {
        console.error("Container element not found!");
        return;
    }

    // 初始化示例图谱数据
    const initialNodes: GraphNode[] = [
        { id: "示例节点", label: "点击上方按钮生成知识图谱", x: 0, y: 0, size: 15, color: "#4B96FF" }
    ];

    initialNodes.forEach(node => {
        graph.addNode(node.id, {
            x: node.x,
            y: node.y,
            size: node.size,
            color: node.color,
            label: node.label,
        });
    });

    // Create the spring layout and start it
    layout = new ForceSupervisor(graph, { isNodeFixed: (_, attr) => attr.highlighted });
    layout.start();

    // Create the sigma with settings to enable edge labels
    renderer = new Sigma(graph, container, {
        minCameraRatio: 0.5,
        maxCameraRatio: 2,
        renderEdgeLabels: true,
        edgeLabelSize: 12,
        edgeLabelWeight: "bold"
    });

    // 绑定事件
    bindEvents();
});
</script>

<style scoped>
.graph-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
}

button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
}

#sigma-container {
    position: relative;
    /* 为绝对定位的子元素提供定位上下文 */
    width: 100%;
    height: 600px;
    /* 固定高度 */
    overflow: hidden;
    /* 隐藏溢出的内容 */
}



#sigma-container :deep(canvas) {
    position: absolute !important;
    top: 0;
    left: 0;
}
</style>
