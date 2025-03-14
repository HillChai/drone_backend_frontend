import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import DatasetView from '../views/DatasetView.vue';
import AlgorithmView from '../views/AlgorithmView.vue';
import HistoryView from '../views/HistoryView.vue';
import EditAlgorithmView from "@/views/EditAlgorithmView.vue";
import ConfirmTrainView from "@/views/ConfirmTrainView.vue";
import ConfirmTestView from "@/views/ConfirmTestView.vue";

const routes = [
    { path: '/', redirect: '/home' },  // 默认跳转到主页
    { path: '/home', component: HomeView },
    { path: '/edit-algorithm', name: "EditAlgorithmView", component: EditAlgorithmView },
    { path: '/dataset', component: DatasetView },
    { path: '/algorithm', component: AlgorithmView },
    { path: '/history', component: HistoryView },
    { path: '/confirmTrain', component: ConfirmTrainView },
    { path: '/confirmTest', component: ConfirmTestView },
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
