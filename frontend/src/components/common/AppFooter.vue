<!--
  公共组件 - 底部信息
-->

<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-info">
        <p>基于协同过滤的就业推荐系统</p>
        <p class="copyright">
          © 2026 就业推荐系统
        </p>
      </div>
      <div class="footer-links">
        <a href="#">关于我们</a>
        <a href="#">帮助中心</a>
        <a href="#">隐私政策</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  padding: 30px 20px;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info p {
  color: #909399;
  margin: 4px 0;
}

.footer-info .copyright {
  font-size: 13px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-links a {
  color: #909399;
  font-size: 14px;
}

.footer-links a:hover {
  color: #409eff;
}
</style>
