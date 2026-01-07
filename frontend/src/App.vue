<template>
  <div id="app">
    <el-container class="container">
      <el-main class="main">
        <div class="tabs-container">
          <el-tabs
            v-model="activeTab"
            type="border-card"
            class="main-tabs"
            @tab-change="handleTabChange"
          >
            <el-tab-pane label="个股信息搜索" name="stock">
              <StockQuery />
            </el-tab-pane>
            <el-tab-pane label="涨跌停板块" name="limitup">
              <LimitUpBoard ref="limitUpBoardRef" />
            </el-tab-pane>
            <el-tab-pane label="强势股票" name="strong">
              <StrongStocks ref="strongStocksRef" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import StockQuery from "./components/StockQuery.vue";
import LimitUpBoard from "./components/LimitUpBoard.vue";
import StrongStocks from "./components/StrongStocks.vue";

const activeTab = ref("stock");
const limitUpBoardRef = ref(null);
const strongStocksRef = ref(null);

// 记录已加载过的标签页
const loadedTabs = ref(new Set(["stock"])); // 首页默认已加载

// 处理标签切换
const handleTabChange = (tabName) => {
  // 如果该标签页未加载过，则加载数据
  if (!loadedTabs.value.has(tabName)) {
    loadedTabs.value.add(tabName);

    // 根据标签页调用对应的加载方法
    if (tabName === "limitup" && limitUpBoardRef.value) {
      limitUpBoardRef.value.fetchData();
    } else if (tabName === "strong" && strongStocksRef.value) {
      strongStocksRef.value.fetchData();
    }
  }
};

// 组件挂载后，如果默认不是首页，则加载当前页
onMounted(() => {
  if (activeTab.value !== "stock") {
    handleTabChange(activeTab.value);
  }
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, "Helvetica Neue", Arial, sans-serif;
  min-height: 100vh;
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.container {
  min-height: 100vh;
}

.main {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px;
}

.tabs-container {
  width: 100%;
  max-width: 1400px;
}

.main-tabs {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-tab-pane) {
  display: flex;
  justify-content: center;
}
</style>
