1. mvc模式的优缺点

    - 优点

      ```
      低耦合性
          分离视图、业务逻辑和数据访问使应用的处理流程更加清晰，
          每层各司其职，业务变动时，代码的修改更加高效
      高复用性
          允许各层之间相互调用，提高代码和业务逻辑的复用能力
      可维护性
      		利于应用的工程化管理
      ```

    - 缺点

      ```
      增加了应用实现的复杂度
          对于简单的界面，严格遵循MVC，使模型、视图与控制器分离，
          会增加结构的复杂性，并可能产生过多的更新操作，降低运行效率
      视图通过模型访问数据，过于低效
      视图与控制器的联系过于紧密
      ```

2. php的生命周期/php的执行原理
   
    - 第一步
    
      词法分析将PHP代码转换为有意义的标识Token。该步骤的词法分析器使用Re2c实现。
    
    - 第二步
    
      语法分析将Token和符合文法规则的代码生成抽象语法树。语法分析器基于Bison实现。语法分析使用了BNF（Backus-NaurForm，巴科斯范式）来表达文法规则，Bison借助状态机、状态转移表和压栈、出栈等一系列操作，生成抽象语法树(AST)。

    - 第三步
    
      将上步的抽象语法树生成对应的opcode，并被虚拟机执行。opcode是PHP 7定义的一组指令标识，指令对应着相应的handler（处理函数）。当虚拟机调用opcode，会找到opcode背后的处理函数，执行真正的处理。
    
3. opcodes和opcache

    PHP工程优化措施中有一个比较常见的“开启opcache”
    指的就是这里的opcodes的缓存（opcodes cache）。通过省去从源码到opcode的阶段，引擎可以直接执行缓存的opcode，以此提升性能。

4. php-fpm
    - 进程模型
    ```
    PHP-FPM采用的是Master/Worker进程模型。当PHP-FPM启动时，会读取配置文件，然后创建一个Master进程和若干个Worker进程（具体是几个Worker进程是由php-fpm.conf中配置的个数决定）。Worker进程是由Master进程fork出来的。
    Master进程：负责管理Worker进程、监听端口、分发请求
    Worker进程：负责处理业务逻辑
    ```
    - 进程的管理方式
    ```
    // 动态
    PHP-FPM启动时会创建一定数量的Worker进程。当请求数逐渐增大时，会动态增加Worker进程的数量；
    当请求数降下来时，会销毁刚才动态创建出来的Worker进程。
    // 静态
    这种方式下，PHP-FPM启动时会创建配置文件中指定数量的Worker进程，不会根据请求数量的多少而增加减少。
    因为PHP-FPM开启的每个Worker进程同一时间只能处理一个请求，所以在这种方式下当请求增大的时候，
    将会出现等待的情形。
    // 按需
    在这种方式下，PHP-FPM启动时，不会创建Worker进程，当请求到达的时候Master进程才会fork出子进程。在这种模式下，如果请求量比较大，Master进程会非常繁忙，会占用大量CPU时间。所以这种模式不适合大流量的环境。
    ```
    - php-fpm和nginx如何通信
    ```
    PHP-FPM 支持两种通信模式：TCP socket和Unix socket
    首先Nginx启动，会载入ngx_http_fastcgi_module模块，初始化FastCGI执行环境，实现FastCGI协议请求代理，
    然后根据location配置，选择一个合适handler将请求翻译成fast-cgi请求，通过socket发送给php-fpm。
    参考：https://zhuanlan.zhihu.com/p/112720502
    ```

5. 自动加载    

    - include和require

      手动加载，最初的复用机制

    - 二者的区别

      - 当包含的文件不存在时

        include:代码继续往下执行,报一个warning,

        而require则是报fatal error, 停止执行.

      - 关于效率:

        加once需要检测已加载的文件,效率稍低,

        如果能确认不会多次包含,不必加once

    - __autoload()

      ```php
      <?php
      // 当我们在使用一个类时，如果发现这个类没有加载，就会自动运行 __autoload() 函数，实现Lazy loading (惰性加载)。
      function __autoload($classname) {
      	require_once ($classname . ".class.php");
      }
      ```

    - spl_autoload_register()

      ```php
      <?php
      // 我们可以向这个函数注册多个我们自己的 autoload() 函数，当 PHP 找不到类名时，就会调用这个堆栈，然后去调用自定义的 autoload() 函数，实现自动加载功能。
      
      function my_autoloader($class) {
          include 'classes/' . $class . '.class.php';
      }
      
      spl_autoload_register('my_autoloader');
      
      // 定义的 autoload 函数在 class 里
        
        // 静态方法
        class MyClass {
          public static function autoload($className) {
            // ...
          }
        }
        
        spl_autoload_register(array('MyClass', 'autoload'));
        
        // 非静态方法
        class MyClass {
          public function autoload($className) {
            // ...
          }
        }
        // 是的没错，可以注册多次
        $instance = new MyClass();
        spl_autoload_register(array($instance, 'autoload'));
        // 参考
        https://segmentfault.com/a/1190000014948542
      ```

6. 面向对象-多态

   - 定义

     ```
     多态就是把子类对象赋值给父类引用，然后调用父类的方法，去执行子类覆盖父类的那个方法
     ```

   - 教科书式的范例-go语言版

     ```
     type Code string
     
     type Programmer interface {
     	WriteHelloWorld() Code
     }
     
     type GoProgrammer struct {
     }
     
     func (p *GoProgrammer) WriteHelloWorld() Code {
     	return "go func is action"
     }
     
     type JavaProgrammer struct {
     }
     
     func (j *JavaProgrammer) WriteHelloWorld() Code {
     	return "java func is action"
     }
     
     func TestInit(t *testing.T) {
     	// 将子类对象赋值给父类引用 调用父类的方法 执行子类覆盖父类的方法
     	var p Programmer
     	//p = new(GoProgrammer)
     	p = new(JavaProgrammer)
     	t.Log(p.WriteHelloWorld())
     }
     ```

7. php多进程编程

    - pcntl_fork() 创建子进程，在父进程返回值是子进程的pid，在子进程返回值是0，-1表示创建进程失败，跟C非常相似。  会存在并行写入现象  出现僵尸进程

    - getmypid() 获取进程的id

    - pcntl_wait()  等待父进程结束在执行子进程  （非阻塞的方式）

      

8. 代码习惯方面的优化

   - echo比print的效率要高

   - foreach 比 for 的效率要高

   - 使用选择结构时 switch要比if快

   - 尽量不要使用@来屏蔽错误信息

   - global声明全部变量  使用后记得unset()掉

   - 变量尽量初始化 再操作

   - 需要变量递增时  使用 ++$i 比 $i++ 要快

   - 尽量使用php内置函数

   - 函数中尽量不要存在多余的变量

   - 尽量使用单引号来代替双引号 声明字符串 输出字符串时

   - 尽量避免用正则

   - 在包含文件时  尽量使用绝对路径

   - 使用$_SERVER['REQUEST_TIME'] 要好于time()

   - 引入php的缓存机制  zend加速器  

     

9. php cli模式下获取参数的方法

   - 使用argv数组

   - 使用getopt方法

   - 参考

     [php cli模式下获取参数的方法](https://blog.csdn.net/fdipzone/article/details/51945892)



10. 两数组合并的方法

    - \+

    向后合并 会保留最早出现的数据

    - array_merge()

    向前合并 会保留最后出现的数据

    

11. php数组底层的实现原理

    [php数组底层的实现原理](https://zhuanlan.zhihu.com/p/97762122)

    

12. 抽象类和接口的区别

    [php面向对象](https://www.cnblogs.com/xiaochaohuashengmi/archive/2010/09/10/1823042.html)

    

13. php接受json格式的数据

    - 两种接受方式

      file_get_contents('php://input')

      $GLOBALS['HTTP_RAW_POST_DATA']

    - Content-type的类型

      - 常见的格式

        text/plain：纯文本格式

        text/html：HTML格式

        text/xml：xml格式

      - application开头的格式

        application/x-www-form-urlencoded:

        ​	form表单默认的提交数据方式，form表单的数据会被编码为key-value格式发送到服务器

        ​	可以在服务端用$_POST全局数组进行接受

        application/json

        ​	以json数据的方式发送

        

    14. php的gc

    ​	

    

    

