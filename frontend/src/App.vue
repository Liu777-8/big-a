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
            <el-tab-pane label="壁纸页面" name="test">
              <TestPage />
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
import TestPage from "./components/TestPage.vue";

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
  position: relative;
  background-image: url("./卧室氛围-女性魅力.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.container {
  min-height: 100vh;
  background: transparent;
}

.main {
  padding: 20px;
  width: 100%;
  background: transparent;
}

.tabs-container {
  width: 100%;
  height: 100%;
  background: transparent;
}

.main-tabs {
  height: 100%;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

:deep(.el-tabs__header) {
  background: transparent;
}

:deep(.el-tabs__nav) {
  background: transparent;
}

:deep(.el-tabs__content) {
  padding: 20px;
  background: transparent;
}

:deep(.el-tab-pane) {
  width: 100%;
  height: 100%;
  background: transparent;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .main {
    padding: 10px 5px;
  }

  .main-tabs {
    border-radius: 8px;
  }

  :deep(.el-tabs__content) {
    padding: 10px 5px;
  }

  :deep(.el-tabs__header) {
    margin: 0;
  }

  :deep(.el-tabs__item) {
    padding: 0 10px;
    font-size: 13px;
  }

  :deep(.el-tabs__nav-wrap) {
    padding: 5px;
  }
}

@media screen and (max-width: 480px) {
  .main {
    padding: 5px 2px;
  }

  :deep(.el-tabs__content) {
    padding: 8px 3px;
  }

  :deep(.el-tabs__item) {
    padding: 0 8px;
    font-size: 12px;
  }
}
</style>
