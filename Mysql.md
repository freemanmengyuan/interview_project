1. 主从复制的原理
    - 简述

      MySql主库在事务提交时会把数据变更作为事件记录在二进制日志Binlog中；
    
      主库推送二进制日志文件Binlog中的事件到从库的中继日志Relay Log中，之后从库根据中继日志做数据变更操作，通过逻辑复制来达到主库和从库的数据一致性；
    - 分述
    
      MySql通过三个线程来完成主从库间的数据复制，其中Binlog Dump线程跑在主库上，I/O线程和SQL线程跑着从库上。

      当在从库上启动复制时，首先创建I/O线程连接主库，主库随后创建Binlog Dump线程读取数据库事件并发送给I/O线程，I/O线程获取到事件数据后更新到从库的中继日志Relay Log中去，之后从库上的SQL线程读取中继日志Relay Log中更新的数据库事件并应用。

2. 事务

    - 操作

      ```sql
      SET AUTOCOMMIT=0;  //设置mysql的提交模式，默认是0，自动提交
      START TRANSACTION;
      SELECT @A:=SUM(salary) FROM table1 WHERE type=1;
      UPDATE table2 SET summary=@A WHERE type=1;
      COMMIT;
      ROLLBACK;
      ```

    - 事务的ACID特性 

      - 原子性：事务中的全部操作在数据库中是不可分割，要么全部执行，要么不执行。
      - 一致性：几个并行执行的事务，其执行结果必须和按照某一顺序串行执行的结果相一致。
      - 隔离型：事务的执行不受其他事务的干扰，当数据库被多个客户端并发访问时。隔离他们的操作，防止出现脏读、幻读、不可重复读。
      - 持久性：对于已经提交的事务，它对数据的变更是持久的，不会丢失的

    - 事务的隔离级别

      ```
      1.未提交读（read uncommitted）
      2.已提交读（read committed）
      3.可重复读（repeatable read）
      4.串行化（serializable）
      对于不同的事务，采用不同的隔离级别分别有不同的结果。不同的隔离级别有不同的现象。
      mysql 默认的事务隔离级别是 repeatable read
      SELECT @@GLOBAL.tx_isolation, @@tx_isolation;  //查看数据库的默认隔离级别
      SET TRANSACTION ISOLATION LEVEL
      ```

    - 使用时注意

      隔离性设置时要考虑多个线程操作同一资源造成的多线程并发安全问题

      加锁可以完美的保证隔离性，但是会造成数据库性能大大下降

      - 如果两个事务并发修改	必须隔离
      - 如果两个事务并发查询    完全不用隔离
      - 一个查询、一个修改    根据需求，看对不同现象的接受程度，使用不同的隔离级别

3. 一条sql的执行过程

    - Mysql 主要分为Server层和引擎层，Server层主要包括连接器、查询缓存、分析器、优化器、执行器，同时还有一个日志模块（binlog），这个日志模块所有执行引擎都可以共用。

    - 引擎层是插件式的，目前主要包括，MyISAM,InnoDB,Memory等。

    - 查询语句的执行流程如下：权限校验（如果命中缓存）---》查询缓存---》分析器---》优化器---》权限校验---》执行器---》引擎

    - 更新语句执行流程如下：分析器----》权限校验----》执行器---》引擎---redo log(prepare 状态---》binlog---》redo log(commit状态)

4. 如何做查询优化-定位和分析

   - 开启慢查询日志

   ```sql
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
   冗余数据，用空间来换取时间
   ```
   - 重写、拆分sql
   ```
   复杂的查询拆分成简单的查询，帮助优化器以更优的方式查询
   ```
   - 优化关联查询
   ```
   确定on或者using子句的列有索引
   确保group by 和order by 中只有一个表中的列，这样才能用到索引
   ```

6. 索引

   - 索引的基础知识

     Mysql的基本存储结构是**页**(记录都存在页里边)

     各个数据页可以组成一个双向链表，而每个数据页中的记录又可以组成一个单向链表

   - 索引是如何提高查询速度