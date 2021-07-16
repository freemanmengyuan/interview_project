1. 查看某个端口号是否被占用

   - 按端口号查找

     netstat  -anp |grep 3306  

     lsof -i:21

   - 查看当前系统端口的使用情况

     netstat  -tunlp

   参考

   [linux查看端口被那个进程占用](https://www.cnblogs.com/fps2tao/p/10042553.html)



2. 查找nginx.log文件中访问频率最高得前十个IP [百度/懂球帝]

   ```
   cat /nginx.cn.log |awk '{print $1}' |sort |uniq -c|sort -n -k 1 -r |head -n 10
   ```

   1. 第一步: awk {print $1} 打印出第一列数据 $1就是第一列, $0是全部
   2. 第二步: sort 正常排序
   3. 第三步: uniq -c 去重, -c是统计重复出现的次数
   4. 第四步: sort 再排序, -n依照数值的大小排序；-k指定需要排序的栏位 -r倒序