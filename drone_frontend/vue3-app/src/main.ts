import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import 'monaco-editor/esm/vs/editor/editor.worker.js'
import 'monaco-editor/esm/vs/language/json/json.worker.js'
import 'monaco-editor/esm/vs/language/css/css.worker.js'
import 'monaco-editor/esm/vs/language/html/html.worker.js'
import 'monaco-editor/esm/vs/language/typescript/ts.worker.js'

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.mount('#app');
