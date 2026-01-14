<template>
  <div class="wallpaper-page">
    <el-card class="wallpaper-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>壁纸页面</span>
        </div>
      </template>

      <div class="iframe-container">
        <iframe
          src="https://wallpaper.061129.xyz/desktop"
          frameborder="0"
          class="wallpaper-iframe"
          allowfullscreen
        ></iframe>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 无需任何逻辑
</script>

<style scoped>
.wallpaper-page {
  width: 100%;
  height: 100%;
}

.wallpaper-card {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  height: calc(100vh - 150px);
  display: flex;
  flex-direction: column;
}

.wallpaper-card:hover {
  box-shadow: 0 15px 60px rgba(102, 126, 234, 0.18);
}

.card-header {
  font-size: 26px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header::before {
  content: "🖼️";
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

.iframe-container {
  width: 100%;
  height: 100%;
  flex: 1;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
}

.wallpaper-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 12px;
}

:deep(.el-card__body) {
  padding: 20px;
  height: calc(100% - 70px);
  display: flex;
  flex-direction: column;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .wallpaper-card {
    height: calc(100vh - 120px);
  }

  .card-header {
    font-size: 20px;
  }

  .card-header::before {
    font-size: 22px;
  }

  :deep(.el-card__body) {
    padding: 15px;
  }
}

@media screen and (max-width: 480px) {
  .wallpaper-card {
    height: calc(100vh - 100px);
  }

  .card-header {
    font-size: 18px;
  }

  .card-header::before {
    font-size: 20px;
  }

  :deep(.el-card__body) {
    padding: 10px;
  }
}
</style>
