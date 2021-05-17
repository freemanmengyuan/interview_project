1. mvc模式的优缺点
    ```
    // 优点
    低耦合性
        分离视图、业务逻辑和数据访问使应用的处理流程更加清晰，
        每层各司其职，业务变动时，代码的修改更加高效
    高复用性
        允许各层之间相互调用，提高代码和业务逻辑的复用能力
    可维护性
    利于应用的工程化管理
    // 缺点
    增加了系统和实现的复杂度
        对于简单的界面，严格遵循MVC，使模型、视图与控制器分离，
        会增加结构的复杂性，并可能产生过多的更新操作，降低运行效率
    视图通过模型访问数据，过于低效
    视图与控制器的联系过于紧密
    ```

2. php的生命周期/php的执行原理
    ```
    // 第一步
    词法分析将PHP代码转换为有意义的标识Token。该步骤的词法分析器使用Re2c实现。
    // 第二步
    语法分析将Token和符合文法规则的代码生成抽象语法树。语法分析器基于Bison实现。语法分析使用了BNF（Backus-NaurForm，巴科斯范式）来表达文法规则，Bison借助状态机、状态转移表和压栈、出栈等一系列操作，生成抽象语法树(AST)。
    // 第三步
    上步的抽象语法树生成对应的opcode，并被虚拟机执行。opcode是PHP 7定义的一组指令标识，指令对应着相应的handler（处理函数）。当虚拟机调用opcode，会找到opcode背后的处理函数，执行真正的处理。
    ```
3. opcodes和opcache
    ```
    PHP工程优化措施中有一个比较常见的“开启opcache”
    指的就是这里的opcodes的缓存（opcodes cache）。通过省去从源码到opcode的阶段，引擎可以直接执行缓存的opcode，以此提升性能。
    ```
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
    ```
    // 自动加载
    https://segmentfault.com/a/1190000014948542
    ```

