<template>
  <div class="strong-stocks">
    <el-card class="board-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>强势股票池</span>
          <div class="header-controls">
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYYMMDD"
              size="small"
              style="width: 150px; margin-right: 10px"
              @change="fetchData"
            />
            <el-button
              type="primary"
              :icon="Refresh"
              @click="fetchData"
              :loading="loading"
              size="small"
            >
              刷新数据
            </el-button>
          </div>
        </div>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 数据统计 -->
      <div v-if="!loading && strongData.length > 0" class="stats-bar">
        <div class="stats-left">
          <el-tag type="warning" size="large">
            共 {{ filteredStrongData.length }} 只强势股票
          </el-tag>
          <el-checkbox
            v-model="filter30"
            label="过滤30开头股票"
            size="large"
            style="margin-left: 15px"
          />
        </div>
        <span class="update-time">更新时间：{{ updateTime }}</span>
      </div>

      <!-- 强势股票表格 -->
      <el-table
        v-if="!loading && strongData.length > 0"
        :data="filteredStrongData"
        stripe
        border
        height="600"
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column type="index" label="序号" width="60" fixed />
        <el-table-column prop="代码" label="股票代码" width="100" fixed />
        <el-table-column prop="名称" label="股票名称" width="100" fixed />
        <el-table-column prop="涨跌幅" label="涨跌幅(%)" width="100" sortable>
          <template #default="{ row }">
            <span :class="getPriceClass(row.涨跌幅)"> {{ row.涨跌幅 }}% </span>
          </template>
        </el-table-column>
        <el-table-column prop="最新价" label="最新价" width="100" />
        <el-table-column prop="涨停价" label="涨停价" width="100" />
        <el-table-column prop="成交额" label="成交额" width="120" />
        <el-table-column prop="流通市值" label="流通市值" width="120" />
        <el-table-column prop="总市值" label="总市值" width="120" />
        <el-table-column prop="换手率" label="换手率(%)" width="100" />
        <el-table-column prop="涨速" label="涨速(%)" width="100" />
        <el-table-column prop="5分钟涨速" label="5分钟涨速(%)" width="120" />
        <el-table-column prop="量比" label="量比" width="100" />
        <el-table-column prop="振幅" label="振幅(%)" width="100" />
        <el-table-column prop="所属行业" label="所属行业" width="120" />
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && strongData.length === 0"
        description="暂无强势股票数据"
        :image-size="150"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";
import axios from "axios";

const strongData = ref([]);
const loading = ref(false);
const updateTime = ref("");
const filter30 = ref(false); // 过滤30开头股票的开关

// 日期选择器，默认今天
const selectedDate = ref(
  new Date().toISOString().split("T")[0].replace(/-/g, "")
);

// 过滤后的数据
const filteredStrongData = computed(() => {
  if (!filter30.value) {
    return strongData.value;
  }
  // 过滤30开头的股票（创业板）
  return strongData.value.filter((item) => {
    const code = String(item.代码 || "");
    return !code.startsWith("30");
  });
});

// 获取强势股票数据
const fetchData = async () => {
  loading.value = true;

  try {
    const params = selectedDate.value ? { date: selectedDate.value } : {};
    const response = await axios.get("/api/stock/strong", { params });

    if (response.data.success) {
      strongData.value = response.data.data;
      updateTime.value = response.data.timestamp;
      ElMessage.success(`加载成功，共 ${response.data.count} 只强势股票`);
    } else {
      ElMessage.error(response.data.message || "加载失败");
    }
  } catch (error) {
    console.error("获取强势股票数据失败:", error);
    ElMessage.error(
      error.response?.data?.message || "获取数据失败，请稍后重试"
    );
  } finally {
    loading.value = false;
  }
};

// 判断涨跌颜色
const getPriceClass = (changePercent) => {
  if (!changePercent) return "";
  const value = parseFloat(changePercent);
  if (value > 0) return "price-up";
  if (value < 0) return "price-down";
  return "";
};

// 暴露fetchData方法给父组件调用
defineExpose({
  fetchData,
});
</script>

<style scoped>
.strong-stocks {
  width: 100%;
  max-width: 1600px;
}

.board-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(255, 255, 255, 0.95) 100%
  );
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.board-card:hover {
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-controls {
  display: flex;
  align-items: center;
}

.loading-container {
  padding: 20px;
}

.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  margin-bottom: 10px;
}

.stats-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.update-time {
  color: #909399;
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(230, 162, 60, 0.1);
  border-radius: 20px;
  color: #e6a23c;
}

.price-up {
  color: #f56c6c;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(245, 108, 108, 0.2);
}

.price-down {
  color: #67c23a;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(103, 194, 58, 0.2);
}

:deep(.el-table) {
  font-size: 14px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

:deep(.el-table th) {
  background: linear-gradient(
    135deg,
    rgba(230, 162, 60, 0.08) 0%,
    rgba(245, 108, 108, 0.08) 100%
  );
  font-weight: 700;
  font-size: 15px;
  color: #606266;
  border-bottom: 2px solid rgba(230, 162, 60, 0.1);
}

:deep(.el-table .cell) {
  padding: 10px 0;
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(230, 162, 60, 0.05) !important;
}

:deep(.el-tag) {
  font-weight: 700;
  padding: 8px 16px;
  font-size: 16px;
  border-radius: 20px;
}

:deep(.el-checkbox) {
  font-weight: 600;
}
</style>
