1. 主从复制的原理
    - 简述
    ```
    MySql主库在事务提交时会把数据变更作为事件记录在二进制日志Binlog中；
    主库推送二进制日志文件Binlog中的事件到从库的中继日志Relay Log中，之后从库根据中继日志做数据变更操作，通过逻辑复制来达到主库和从库的数据一致性；
    ```
    - 分述
    ```
    MySql通过三个线程来完成主从库间的数据复制，其中Binlog Dump线程跑在主库上，I/O线程和SQL线程跑着从库上；
    当在从库上启动复制时，首先创建I/O线程连接主库，主库随后创建Binlog Dump线程读取数据库事件并发送给I/O线程，
    I/O线程获取到事件数据后更新到从库的中继日志Relay Log中去，之后从库上的SQL线程读取中继日志Relay Log中更新的数据库事件并应用
    ```

2. 事务的隔离级别

3. 一条sql的执行过程

4. 如何做查询优化-定位和分析

   - 开启慢查询日志

   ```
   Show status like ‘slow_queries’;
   Show variables like ‘long_query_time’;
   //更改慢查询设置
   Set long_query_time=1;
   //到bin目录下 执行 
   \mysql.exe --safe -mode --slow-query-log
   注意：
       不要直接打开慢查询日志进行分析 使用pt-query-digest工具进行分析
   ```
   - show profile
   ```
   set profiling=1开启 会把所有的语句和对应的消耗时间存到临时表中
   show profiles
   show profile for query 临时表id
   ```
   - show processlist
   ```
   观察是否有连接（线程）处于不正常状态
   ```
   - explain
   ```
   explain + sql //检查sql查询索引的使用情况 
   
   EXPLAIN列的解释
   table 查询所涉及到的表
   type  使用何种方式连接表  查询类型  const  all  ref
   possible_keys  可能用到的索引
   key  实际用到的索引
   key_len 索引的长度
   extra  额外的信息
   rows   检查返回数据的记录数
   //type 查询类型（官方术语是 连接类型）
   参考: https://blog.csdn.net/dennis211/article/details/78170079
   ```

5. 如何做查询优化-优化

   - 更改数据表范式

   ```
   冗余数据 用空间来换取时间
   ```
   - 重写、拆分sql
   ```
   复杂的查询拆分成简单的查询 帮助优化器以更优的方式查询
   ```
   - 优化关联查询
   ```
   确定on或者using子句的列有索引
   确保group by 和order by 中只有一个表中的列，这样才能用到索引
   ```