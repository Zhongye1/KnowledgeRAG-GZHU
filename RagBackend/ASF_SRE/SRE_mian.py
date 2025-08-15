import pymysql

try:
    # 连接配置
    connection = pymysql.connect(
        host='172.22.121.2',       # 本地连接
        port=3306,
        user='root',             # compose文件中定义的用户
        password='Www028820',   # compose文件中定义的密码
        database='mysql',         # compose文件中初始化的数据库
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print(">>> 数据库连接成功! <<<")
    
    # 测试查询
    with connection.cursor() as cursor:
        # 查询当前数据库版本
        cursor.execute("SELECT VERSION() AS version")
        result = cursor.fetchone()
        print(f"MySQL版本: {result['version']}")
        
        # 验证时区配置
        cursor.execute("SELECT @@global.time_zone, @@session.time_zone AS timezone")
        result = cursor.fetchone()
        print(f"服务器时区: {result['timezone']} (应为Asia/Shanghai)")
        
        # 验证初始化数据库
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
      
    
except pymysql.Error as e:
    print(f"数据库连接失败: {e}")