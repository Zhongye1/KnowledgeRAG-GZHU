-- 创建 ASF 数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ASF CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 创建用户 mmk（如果不存在）
CREATE USER IF NOT EXISTS 'mmk'@'%' IDENTIFIED BY 'Www028820';

-- 授予 mmk 用户对 ASF 数据库的所有权限
GRANT ALL PRIVILEGES ON ASF.* TO 'mmk'@'%';

-- 刷新权限使设置生效
FLUSH PRIVILEGES;
