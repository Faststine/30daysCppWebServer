# day01-从一个最简单的socket开始

如果读者之前有计算机网络的基础知识那就更好了，没有也没关系，socket编程非常容易上手。但本教程主要偏向实践，不会详细讲述计算机网络协议、网络编程原理等。想快速入门可以看以下博客，讲解比较清楚、错误较少：
- [计算机网络基础知识总结](https://www.runoob.com/w3cnote/summary-of-network.html)

要想打好基础，抄近道是不可的，有时间一定要认真学一遍谢希仁的《计算机网络》，要想精通服务器开发，这必不可少。

首先在服务器，我们需要建立一个socket套接字，对外提供一个网络通信接口，在Linux系统中这个套接字竟然仅仅是一个文件描述符，也就是一个`int`类型的值！这个对套接字的所有操作（包括创建）都是最底层的系统调用。
> 在这里读者务必先了解什么是Linux系统调用和文件描述符，《现代操作系统》第四版第一章有详细的讨论。如果你想抄近道看博客，C语言中文网的这篇文章讲了一部分：[socket是什么？套接字是什么？](http://c.biancheng.net/view/2123.html)

> Unix哲学KISS：keep it simple, stupid。在Linux系统里，一切看上去十分复杂的逻辑功能，都用简单到不可思议的方式实现，甚至有些时候看上去很愚蠢。但仔细推敲，人们将会赞叹Linux的精巧设计，或许这就是大智若愚。
```cpp
#include <sys/socket.h>
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
```
- 第一个参数：IP地址类型，AF_INET表示使用IPv4，如果使用IPv6请使用AF_INET6。
- 第二个参数：数据传输方式，SOCK_STREAM表示流格式、面向连接，多用于TCP。SOCK_DGRAM表示数据报格式、无连接，多用于UDP。
- 第三个参数：协议，0表示根据前面的两个参数自动推导协议类型。设置为IPPROTO_TCP和IPPTOTO_UDP，分别表示TCP和UDP。

对于客户端，服务器存在的唯一标识是一个IP地址和端口，这时候我们需要将这个套接字绑定到一个IP地址和端口上。首先创建一个sockaddr_in结构体
```cpp
#include <arpa/inet.h>  //这个头文件包含了<netinet/in.h>，不用再次包含了
struct sockaddr_in serv_addr;
bzero(&serv_addr, sizeof(serv_addr));
```
然后使用`bzero`初始化这个结构体，这个函数在头文件`<string.h>`或`<cstring>`中。这里用到了两条《Effective C++》的准则：
> 条款04: 确定对象被使用前已先被初始化。如果不清空，使用gdb调试器查看addr内的变量，会是一些随机值，未来可能会导致意想不到的问题。

> 条款01: 视C++为一个语言联邦。把C和C++看作两种语言，写代码时需要清楚地知道自己在写C还是C++。如果在写C，请包含头文件`<string.h>`。如果在写C++，请包含`<cstring>`。

设置地址族、IP地址和端口：
```cpp
serv_addr.sin_family = AF_INET;
serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
serv_addr.sin_port = htons(8888);
```
然后将socket地址与文件描述符绑定：
```cpp
bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr));
```
> 为什么定义的时候使用专用socket地址（sockaddr_in）而绑定的时候要转化为通用socket地址（sockaddr），以及转化IP地址和端口号为网络字节序的`inet_addr`和`htons`等函数及其必要性，在游双《Linux高性能服务器编程》第五章第一节：socket地址API中有详细讨论。

最后我们需要使用`listen`函数监听这个socket端口，这个函数的第二个参数是listen函数的最大监听队列长度，系统建议的最大值`SOMAXCONN`被定义为128。
```cpp
listen(sockfd, SOMAXCONN);
```
要接受一个客户端连接，需要使用`accept`函数。对于每一个客户端，我们在接受连接时也需要保存客户端的socket地址信息，于是有以下代码：
```cpp
struct sockaddr_in clnt_addr;
socklen_t clnt_addr_len = sizeof(clnt_addr);
bzero(&clnt_addr, sizeof(clnt_addr));
int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
printf("new client fd %d! IP: %s Port: %d\n", clnt_sockfd, inet_ntoa(clnt_addr.sin_addr), ntohs(clnt_addr.sin_port));
```
要注意和`accept`和`bind`的第三个参数有一点区别，对于`bind`只需要传入serv_addr的大小即可，而`accept`需要写入客户端socket长度，所以需要定义一个类型为`socklen_t`的变量，并传入这个变量的地址。另外，`accept`函数会阻塞当前程序，直到有一个客户端socket被接受后程序才会往下运行。

到现在，客户端已经可以通过IP地址和端口号连接到这个socket端口了，让我们写一个测试客户端连接试试：
```cpp
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in serv_addr;
bzero(&serv_addr, sizeof(serv_addr));
serv_addr.sin_family = AF_INET;
serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
serv_addr.sin_port = htons(8888);
connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr));  
```
代码和服务器代码几乎一样：创建一个socket文件描述符，与一个IP地址和端口绑定，最后并不是监听这个端口，而是使用`connect`函数尝试连接这个服务器。

至此，day01的教程已经结束了，进入`code/day01`文件夹，使用make命令编译，将会得到`server`和`client`。输入命令`./server`开始运行，直到`accept`函数，程序阻塞、等待客户端连接。然后在一个新终端输入命令`./client`运行客户端，可以看到服务器接收到了客户端的连接请求，并成功连接。
```
new client fd 3! IP: 127.0.0.1 Port: 53505
```
但如果我们先运行客户端、后运行服务器，在客户端一侧无任何区别，却并没有连接服务器成功，因为我们day01的程序没有任何的错误处理。

事实上对于如`socket`,`bind`,`listen`,`accept`,`connect`等函数，通过返回值以及`errno`可以确定程序运行的状态、是否发生错误。在day02的教程中，我们会进一步完善整个服务器，处理所有可能的错误，并实现一个echo服务器（客户端发送给服务器一个字符串，服务器收到后返回相同的内容）。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day01](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day01)
## client.cpp
```cpp
/*
 * @Author: your name
 * @Date: 2022-01-04 20:03:45
 * @LastEditTime: 2022-01-05 19:08:58
 * @LastEditors: your name
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \30dayMakeCppServer\code\day01\client.cpp
 */
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    //bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)); 客户端不进行bind操作

    connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr));    
    
    return 0;
}

```

## server.cpp
```cpp
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr));

    listen(sockfd, SOMAXCONN);
    
    struct sockaddr_in clnt_addr;
    socklen_t clnt_addr_len = sizeof(clnt_addr);
    bzero(&clnt_addr, sizeof(clnt_addr));

    int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);

    printf("new client fd %d! IP: %s Port: %d\n", clnt_sockfd, inet_ntoa(clnt_addr.sin_addr), ntohs(clnt_addr.sin_port));
    return 0;
}

```

## Makefile
```makefile
server:
	g++ server.cpp -o server && g++ client.cpp -o client
```

---

# day02-不要放过任何一个错误
在上一天，我们写了一个客户端发起socket连接和一个服务器接受socket连接。然而对于`socket`,`bind`,`listen`,`accept`,`connect`等函数，我们都设想程序完美地、没有任何异常地运行，而这显然是不可能的，不管写代码水平多高，就算你是林纳斯，也会在程序里写出bug。

在《Effective C++》中条款08讲到，别让异常逃离析构函数。在这里我拓展一下，我们不应该放过每一个异常，否则在大型项目开发中一定会遇到很难定位的bug！
> 具体信息可以参考《Effective C++》原书条款08，这里不再赘述。

对于Linux系统调用，常见的错误提示方式是使用返回值和设置errno来说明错误类型。
> 详细的C++语言异常处理请参考《C++ Primer》第五版第五章第六节

通常来讲，当一个系统调用返回-1，说明有error发生。我们来看看socket编程最常见的错误处理模版：
```cpp
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
if(sockfd == -1)
{
    print("socket create error");
    exit(-1);
}
```
为了处理一个错误，需要至少占用五行代码，这使编程十分繁琐，程序也不好看，异常处理所占篇幅比程序本身都多。

为了方便编码以及代码的可读性，可以封装一个错误处理函数：
```cpp
void errif(bool condition, const char *errmsg){
    if(condition){
        perror(errmsg);
        exit(EXIT_FAILURE);
    }
}
```
第一个参数是是否发生错误，如果为真，则表示有错误发生，会调用`<stdio.h>`头文件中的`perror`，这个函数会打印出`errno`的实际意义，还会打印出我们传入的字符串，也就是第函数第二个参数，让我们很方便定位到程序出现错误的地方。然后使用`<stdlib.h>`中的`exit`函数让程序退出并返回一个预定义常量`EXIT_FAILURE`。

在使用的时候:
```cpp
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
errif(sockfd == -1, "socket create error");
```
这样我们只需要使用一行进行错误处理，写起来方便简单，也输出了自定义信息，用于定位bug。

对于所有的函数，我们都使用这种方式处理错误：
```cpp
errif(bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket bind error");
errif(listen(sockfd, SOMAXCONN) == -1, "socket listen error");
int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
errif(clnt_sockfd == -1, "socket accept error");
errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
```
到现在最简单的错误处理函数已经封装好了，但这仅仅用于本教程的开发，在真实的服务器开发中，错误绝不是一个如此简单的话题。

当我们建立一个socket连接后，就可以使用`<unistd.h>`头文件中`read`和`write`来进行网络接口的数据读写操作了。
> 这两个函数用于TCP连接。如果是UDP，需要使用`sendto`和`recvfrom`，这些函数的详细用法可以参考游双《Linux高性能服务器编程》第五章第八节。

接下来的教程用注释的形式写在代码中，先来看服务器代码：
```cpp
while (true) {
    char buf[1024];     //定义缓冲区
    bzero(&buf, sizeof(buf));       //清空缓冲区
    ssize_t read_bytes = read(clnt_sockfd, buf, sizeof(buf)); //从客户端socket读到缓冲区，返回已读数据大小
    if(read_bytes > 0){
        printf("message from client fd %d: %s\n", clnt_sockfd, buf);  
        write(clnt_sockfd, buf, sizeof(buf));           //将相同的数据写回到客户端
    } else if(read_bytes == 0){             //read返回0，表示EOF
        printf("client fd %d disconnected\n", clnt_sockfd);
        close(clnt_sockfd);
        break;
    } else if(read_bytes == -1){        //read返回-1，表示发生错误，按照上文方法进行错误处理
        close(clnt_sockfd);
        errif(true, "socket read error");
    }
}
```
客户端代码逻辑是一样的：
```cpp
while(true){
    char buf[1024];     //定义缓冲区
    bzero(&buf, sizeof(buf));       //清空缓冲区
    scanf("%s", buf);             //从键盘输入要传到服务器的数据
    ssize_t write_bytes = write(sockfd, buf, sizeof(buf));      //发送缓冲区中的数据到服务器socket，返回已发送数据大小
    if(write_bytes == -1){          //write返回-1，表示发生错误
        printf("socket already disconnected, can't write any more!\n");
        break;
    }
    bzero(&buf, sizeof(buf));       //清空缓冲区 
    ssize_t read_bytes = read(sockfd, buf, sizeof(buf));    //从服务器socket读到缓冲区，返回已读数据大小
    if(read_bytes > 0){
        printf("message from server: %s\n", buf);
    }else if(read_bytes == 0){      //read返回0，表示EOF，通常是服务器断开链接，等会儿进行测试
        printf("server socket disconnected!\n");
        break;
    }else if(read_bytes == -1){     //read返回-1，表示发生错误，按照上文方法进行错误处理
        close(sockfd);
        errif(true, "socket read error");
    }
}
```
> 一个小细节，Linux系统的文件描述符理论上是有限的，在使用完一个fd之后，需要使用头文件`<unistd.h>`中的`close`函数关闭。更多内核相关知识可以参考Robert Love《Linux内核设计与实现》的第三版。

至此，day02的主要教程已经结束了，完整源代码请在`code/day02`文件夹，接下来看看今天的学习成果以及测试我们的服务器！

进入`code/day02`文件夹，使用make命令编译，将会得到`server`和`client`。输入命令`./server`开始运行，直到`accept`函数，程序阻塞、等待客户端连接。然后在一个新终端输入命令`./client`运行客户端，可以看到服务器接收到了客户端的连接请求，并成功连接。现在客户端阻塞在`scanf`函数，等待我们键盘输入，我们可以输入一句话，然后回车。在服务器终端，我们可以看到:
```
message from client fd 4: Hello!
```
然后在客户端，也能接受到服务器的消息：
```
message from server: Hello!
```
> 由于是一个`while(true)`循环，客户端可以一直输入，服务器也会一直echo我们的消息。由于`scanf`函数的特性，输入的语句遇到空格时，会当成多行进行处理，我们可以试试。

接下来在客户端使用`control+c`终止程序，可以看到服务器也退出了程序并显示：
```
client fd 4 disconnected
```
再次运行两个程序，这次我们使用`control+c`终止掉服务器，再试图从客户端发送信息，可以看到客户端输出：
```
server socket disconnected!
```
至此，我们已经完整地开发了一个echo服务器，并且有最基本的错误处理！

但现在，我们的服务器只能处理一个客户端，我们可以试试两个客户端同时连接服务器，看程序将会如何运行。在day03的教程里，我们将会讲解Linux系统高并发的基石--epoll，并编程实现一个可以支持无数客户端同时连接的echo服务器！

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day02](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day02)

## util.cpp
```cpp
#include "util.h"
#include <stdio.h>
#include <stdlib.h>

void errif(bool condition, const char *errmsg){
    if(condition){
        perror(errmsg);
        exit(EXIT_FAILURE);
    }
}
```

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "util.h"


int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[1024];
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## server.cpp
```cpp
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "util.h"

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket bind error");

    errif(listen(sockfd, SOMAXCONN) == -1, "socket listen error");
    
    struct sockaddr_in clnt_addr;
    socklen_t clnt_addr_len = sizeof(clnt_addr);
    bzero(&clnt_addr, sizeof(clnt_addr));

    int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
    errif(clnt_sockfd == -1, "socket accept error");

    printf("new client fd %d! IP: %s Port: %d\n", clnt_sockfd, inet_ntoa(clnt_addr.sin_addr), ntohs(clnt_addr.sin_port));
    while (true) {
        char buf[1024];
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(clnt_sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from client fd %d: %s\n", clnt_sockfd, buf);
            write(clnt_sockfd, buf, sizeof(buf));
        } else if(read_bytes == 0){
            printf("client fd %d disconnected\n", clnt_sockfd);
            close(clnt_sockfd);
            break;
        } else if(read_bytes == -1){
            close(clnt_sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## Makefile
```makefile
server:
	g++ util.cpp client.cpp -o client && \
	g++ util.cpp server.cpp -o server
clean:
	rm server && rm client
```

---

# day03-高并发还得用epoll

在上一天，我们写了一个简单的echo服务器，但只能同时处理一个客户端的连接。但在这个连接的生命周期中，绝大部分时间都是空闲的，活跃时间（发送数据和接收数据的时间）占比极少，这样独占一个服务器是严重的资源浪费。事实上所有的服务器都是高并发的，可以同时为成千上万个客户端提供服务，这一技术又被称为IO复用。
> IO复用和多线程有相似之处，但绝不是一个概念。IO复用是针对IO接口，而多线程是针对CPU。

IO复用的基本思想是事件驱动，服务器同时保持多个客户端IO连接，当这个IO上有可读或可写事件发生时，表示这个IO对应的客户端在请求服务器的某项服务，此时服务器响应该服务。在Linux系统中，IO复用使用select, poll和epoll来实现。epoll改进了前两者，更加高效、性能更好，是目前几乎所有高并发服务器的基石。请读者务必先掌握epoll的原理再进行编码开发。
> select, poll与epoll的详细原理和区别请参考《UNIX网络编程：卷1》第二部分第六章，游双《Linux高性能服务器编程》第九章

epoll主要由三个系统调用组成：
```cpp
//int epfd = epoll_create(1024);  //参数表示监听事件的大小，如超过内核会自动调整，已经被舍弃，无实际意义，传入一个大于0的数即可
int epfd = epoll_create1(0);       //参数是一个flag，一般设为0，详细参考man epoll
```
创建一个epoll文件描述符并返回，失败则返回-1。

epoll监听事件的描述符会放在一颗红黑树上，我们将要监听的IO口放入epoll红黑树中，就可以监听该IO上的事件。
```cpp
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);    //添加事件到epoll
epoll_ctl(epfd, EPOLL_CTL_MOD, sockfd, &ev);    //修改epoll红黑树上的事件
epoll_ctl(epfd, EPOLL_CTL_DEL, sockfd, NULL);   //删除事件
```
其中sockfd表示我们要添加的IO文件描述符，ev是一个epoll_event结构体，其中的events表示事件，如EPOLLIN等，data是一个用户数据union:
```cpp
typedef union epoll_data {
  void *ptr;
  int fd;
  uint32_t u32;
  uint64_t u64;
} epoll_data_t;
struct epoll_event {
  uint32_t events;	/* Epoll events */
  epoll_data_t data;	/* User data variable */
} __EPOLL_PACKED;
```
epoll默认采用LT触发模式，即水平触发，只要fd上有事件，就会一直通知内核。这样可以保证所有事件都得到处理、不容易丢失，但可能发生的大量重复通知也会影响epoll的性能。如使用ET模式，即边缘触法，fd从无事件到有事件的变化会通知内核一次，之后就不会再次通知内核。这种方式十分高效，可以大大提高支持的并发度，但程序逻辑必须一次性很好地处理该fd上的事件，编程比LT更繁琐。注意ET模式必须搭配非阻塞式socket使用。
> 非阻塞式socket和阻塞式有很大的不同，请参考《UNIX网络编程：卷1》第三部分第16章。

我们可以随时使用`epoll_wait`获取有事件发生的fd：
```cpp
int nfds = epoll_wait(epfd, events, maxevents, timeout);
```
其中events是一个epoll_event结构体数组，maxevents是可供返回的最大事件大小，一般是events的大小，timeout表示最大等待时间，设置为-1表示一直等待。

接下来将day02的服务器改写成epoll版本，基本思想为：在创建了服务器socket fd后，将这个fd添加到epoll，只要这个fd上发生可读事件，表示有一个新的客户端连接。然后accept这个客户端并将客户端的socket fd添加到epoll，epoll会监听客户端socket fd是否有事件发生，如果发生则处理事件。

接下来的教程在伪代码中：
```cpp
int sockfd = socket(...);   //创建服务器socket fd
bind(sockfd...);
listen(sockfd...);
int epfd = epoll_create1(0);
struct epoll_event events[MAX_EVENTS], ev;
ev.events = EPOLLIN;    //在代码中使用了ET模式，且未处理错误，在day12进行了修复，实际上接受连接最好不要用ET模式
ev.data.fd = sockfd;    //该IO口为服务器socket fd
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);    //将服务器socket fd添加到epoll
while(true){    // 不断监听epoll上的事件并处理
    int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);   //有nfds个fd发生事件
    for(int i = 0; i < nfds; ++i){  //处理这nfds个事件
        if(events[i].data.fd == sockfd){    //发生事件的fd是服务器socket fd，表示有新客户端连接
            int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
            ev.data.fd = clnt_sockfd;   
            ev.events = EPOLLIN | EPOLLET;  //对于客户端连接，使用ET模式，可以让epoll更加高效，支持更多并发
            setnonblocking(clnt_sockfd);    //ET需要搭配非阻塞式socket使用
            epoll_ctl(epfd, EPOLL_CTL_ADD, clnt_sockfd, &ev);   //将该客户端的socket fd添加到epoll
        } else if(events[i].events & EPOLLIN){      //发生事件的是客户端，并且是可读事件（EPOLLIN）
            handleEvent(events[i].data.fd);         //处理该fd上发生的事件
        }
    }
}
```
从一个非阻塞式socket fd上读取数据时：
```cpp
while(true){    //由于使用非阻塞IO，需要不断读取，直到全部读取完毕
    ssize_t bytes_read = read(events[i].data.fd, buf, sizeof(buf));
    if(bytes_read > 0){
      //保存读取到的bytes_read大小的数据
    } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
        continue;
    } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
        //该fd上数据读取完毕
        break;
    } else if(bytes_read == 0){  //EOF事件，一般表示客户端断开连接
        close(events[i].data.fd);   //关闭socket会自动将文件描述符从epoll树上移除
        break;
    } //剩下的bytes_read == -1的情况表示其他错误，这里没有处理
}
```
至此，day03的主要教程已经结束了，完整源代码请在`code/day03`文件夹，接下来看看今天的学习成果以及测试我们的服务器！

进入`code/day03`文件夹，使用make命令编译，将会得到`server`和`client`，输入命令`./server`开始运行服务器。然后在一个新终端输入命令`./client`运行客户端，可以看到服务器接收到了客户端的连接请求，并成功连接。再新开一个或多个终端，运行client，可以看到这些客户端也同时连接到了服务器。此时我们在任意一个client输入一条信息，服务器都显示并发送到该客户端。如使用`control+c`终止掉某个client，服务器回显示这个client已经断开连接，但其他client并不受影响。

至此，我们已经完整地开发了一个echo服务器，并且支持多个客户端同时连接，为他们提供服务！

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day03](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day03)

## util.cpp
```cpp
#include "util.h"
#include <stdio.h>
#include <stdlib.h>

void errif(bool condition, const char *errmsg){
    if(condition){
        perror(errmsg);
        exit(EXIT_FAILURE);
    }
}
```

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## server.cpp
```cpp
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <errno.h>
#include "util.h"

#define MAX_EVENTS 1024
#define READ_BUFFER 1024

void setnonblocking(int fd){
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK);
}

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket bind error");

    errif(listen(sockfd, SOMAXCONN) == -1, "socket listen error");
    
    int epfd = epoll_create1(0);
    errif(epfd == -1, "epoll create error");

    struct epoll_event events[MAX_EVENTS], ev;
    bzero(&events, sizeof(events));

    bzero(&ev, sizeof(ev));
    ev.data.fd = sockfd;
    ev.events = EPOLLIN | EPOLLET;
    setnonblocking(sockfd);
    epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);

    while(true){
        int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
        errif(nfds == -1, "epoll wait error");
        for(int i = 0; i < nfds; ++i){
            if(events[i].data.fd == sockfd){        //新客户端连接
                struct sockaddr_in clnt_addr;
                bzero(&clnt_addr, sizeof(clnt_addr));
                socklen_t clnt_addr_len = sizeof(clnt_addr);

                int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
                errif(clnt_sockfd == -1, "socket accept error");
                printf("new client fd %d! IP: %s Port: %d\n", clnt_sockfd, inet_ntoa(clnt_addr.sin_addr), ntohs(clnt_addr.sin_port));

                bzero(&ev, sizeof(ev));
                ev.data.fd = clnt_sockfd;
                ev.events = EPOLLIN | EPOLLET;
                setnonblocking(clnt_sockfd);
                epoll_ctl(epfd, EPOLL_CTL_ADD, clnt_sockfd, &ev);
            } else if(events[i].events & EPOLLIN){      //可读事件
                char buf[READ_BUFFER];
                while(true){    //由于使用非阻塞IO，读取客户端buffer，一次读取buf大小数据，直到全部读取完毕
                    bzero(&buf, sizeof(buf));
                    ssize_t bytes_read = read(events[i].data.fd, buf, sizeof(buf));
                    if(bytes_read > 0){
                        printf("message from client fd %d: %s\n", events[i].data.fd, buf);
                        write(events[i].data.fd, buf, sizeof(buf));
                    } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
                        printf("continue reading");
                        continue;
                    } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
                        printf("finish reading once, errno: %d\n", errno);
                        break;
                    } else if(bytes_read == 0){  //EOF，客户端断开连接
                        printf("EOF, client fd %d disconnected\n", events[i].data.fd);
                        close(events[i].data.fd);   //关闭socket会自动将文件描述符从epoll树上移除
                        break;
                    }
                }
            } else{         //其他事件，之后的版本实现
                printf("something else happened\n");
            }
        }
    }
    close(sockfd);
    return 0;
}

```

## Makefile
```makefile
server:
	g++ util.cpp client.cpp -o client && \
	g++ util.cpp server.cpp -o server
clean:
	rm server && rm client
```

---

# day04-来看看我们的第一个类

在上一天，我们开发了一个支持多个客户端连接的服务器，但到目前为止，虽然我们的程序以`.cpp`结尾，本质上我们写的仍然是C语言程序。虽然C++语言完全兼容C语言并且大部分程序中都是混用，但一个很好的习惯是把C和C++看作两种语言，写代码时需要清楚地知道自己在写C还是C++。

另一点是我们的程序会变得越来越长、越来越庞大，虽然现在才不到100行代码，但把所有逻辑放在一个程序里显然是一种错误的做法，我们需要对程序进行模块化，每一个模块专门处理一个任务，这样可以增加程序的可读性，也可以写出更大庞大、功能更加复杂的程序。不仅如此，还可以很方便地进行代码复用，也就是造轮子。

C++是一门面向对象的语言，最低级的模块化的方式就是构建一个类。举个例子，我们的程序有新建服务器socket、绑定IP地址、监听、接受客户端连接等任务，代码如下：
```cpp
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
errif(sockfd == -1, "socket create error");

struct sockaddr_in serv_addr;
bzero(&serv_addr, sizeof(serv_addr));
serv_addr.sin_family = AF_INET;
serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
serv_addr.sin_port = htons(8888);

errif(bind(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket bind error");

errif(listen(sockfd, SOMAXCONN) == -1, "socket listen error");

struct sockaddr_in clnt_addr;
bzero(&clnt_addr, sizeof(clnt_addr));
socklen_t clnt_addr_len = sizeof(clnt_addr);

int clnt_sockfd = accept(sockfd, (sockaddr*)&clnt_addr, &clnt_addr_len);
errif(clnt_sockfd == -1, "socket accept error");
```
可以看到代码有19行，这已经是使用socket最精简的代码。在服务器开发中，我们或许会建立多个socket口，或许会处理多个客户端连接，但我们并不希望每次都重复编写这么多行代码，我们希望这样使用：
```cpp
Socket *serv_sock = new Socket();
InetAddress *serv_addr = new InetAddress("127.0.0.1", 8888);
serv_sock->bind(serv_addr);
serv_sock->listen();   
InetAddress *clnt_addr = new InetAddress();  
Socket *clnt_sock = new Socket(serv_sock->accept(clnt_addr));    
```
仅仅六行代码就可以实现和之前一样的功能，这样的使用方式忽略了底层的语言细节，不用在程序中考虑错误处理，更简单、更加专注于程序的自然逻辑，大家毫无疑问也肯定希望以这样简单的方式使用socket。

类似的还有epoll，最精简的使用方式为：
```cpp
int epfd = epoll_create1(0);
errif(epfd == -1, "epoll create error");

struct epoll_event events[MAX_EVENTS], ev;
bzero(&events, sizeof(events) * MAX_EVENTS);

bzero(&ev, sizeof(ev));
ev.data.fd = sockfd;
ev.events = EPOLLIN | EPOLLET;

epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);

while(true){
    int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
    errif(nfds == -1, "epoll wait error");
    for(int i = 0; i < nfds; ++i){
        // handle event
    }
}
```
而我们更希望这样来使用：
```cpp
Epoll *ep = new Epoll();
ep->addFd(serv_sock->getFd(), EPOLLIN | EPOLLET);
while(true){
    vector<epoll_event> events = ep->poll();
    for(int i = 0; i < events.size(); ++i){
        // handle event
    }
}
```
同样完全忽略了如错误处理之类的底层细节，大大简化了编程，增加了程序的可读性。

在今天的代码中，程序的功能和昨天一样，仅仅将`Socket`、`InetAddress`和`Epoll`封装成类，这也是面向对象编程的最核心、最基本的思想。现在我们的目录结构为：
```
client.cpp
Epoll.cpp
Epoll.h
InetAddress.cpp
InetAddress.h
Makefile
server.cpp
Socket.cpp
Socket.h
util.cpp
util.h
```
注意在编译程序的使用，需要编译`Socket`、`InetAddress`和`Epoll`类的`.cpp`文件，然后进行链接，因为`.h`文件里只是类的定义，并未实现。
> C/C++程序编译、链接是一个很复杂的事情，具体原理请参考《深入理解计算机系统（第三版）》第七章。

至此，day04的主要教程已经结束了，完整源代码请在`code/day04`文件夹，服务器的功能和昨天一样。

进入`code/day04`文件夹，使用make命令编译，将会得到`server`和`client`，输入命令`./server`开始运行服务器。然后在一个新终端输入命令`./client`运行客户端，可以看到服务器接收到了客户端的连接请求，并成功连接。再新开一个或多个终端，运行client，可以看到这些客户端也同时连接到了服务器。此时我们在任意一个client输入一条信息，服务器都显示并发送到该客户端。如使用`control+c`终止掉某个client，服务器回显示这个client已经断开连接，但其他client并不受影响。

至此，我们已经完整地开发了一个echo服务器，并且引入面向对象编程的思想，初步封装了`Socket`、`InetAddress`和`Epoll`，大大精简了主程序，隐藏了底层语言实现细节、增加了可读性。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day04](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day04)

## util.cpp
```cpp
#include "util.h"
#include <stdio.h>
#include <stdlib.h>

void errif(bool condition, const char *errmsg){
    if(condition){
        perror(errmsg);
        exit(EXIT_FAILURE);
    }
}
```

## Epoll.cpp
```cpp
#include "Epoll.h"
#include "util.h"
#include <unistd.h>
#include <string.h>

#define MAX_EVENTS 1000

Epoll::Epoll() : epfd(-1), events(nullptr){
    epfd = epoll_create1(0);
    errif(epfd == -1, "epoll create error");
    events = new epoll_event[MAX_EVENTS];
    bzero(events, sizeof(*events) * MAX_EVENTS);
}

Epoll::~Epoll(){
    if(epfd != -1){
        close(epfd);
        epfd = -1;
    }
    delete [] events;
}

void Epoll::addFd(int fd, uint32_t op){
    struct epoll_event ev;
    bzero(&ev, sizeof(ev));
    ev.data.fd = fd;
    ev.events = op;
    errif(epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1, "epoll add event error");
}

std::vector<epoll_event> Epoll::poll(int timeout){
    std::vector<epoll_event> activeEvents;
    int nfds = epoll_wait(epfd, events, MAX_EVENTS, timeout);
    errif(nfds == -1, "epoll wait error");
    for(int i = 0; i < nfds; ++i){
        activeEvents.push_back(events[i]);
    }
    return activeEvents;
}
```

## Socket.cpp
```cpp
#include "Socket.h"
#include "InetAddress.h"
#include "util.h"
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>

Socket::Socket() : fd(-1){
    fd = socket(AF_INET, SOCK_STREAM, 0);
    errif(fd == -1, "socket create error");
}
Socket::Socket(int _fd) : fd(_fd){
    errif(fd == -1, "socket create error");
}

Socket::~Socket(){
    if(fd != -1){
        close(fd);
        fd = -1;
    }
}

void Socket::bind(InetAddress *addr){
    errif(::bind(fd, (sockaddr*)&addr->addr, addr->addr_len) == -1, "socket bind error");
}

void Socket::listen(){
    errif(::listen(fd, SOMAXCONN) == -1, "socket listen error");
}
void Socket::setnonblocking(){
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK);
}

int Socket::accept(InetAddress *addr){
    int clnt_sockfd = ::accept(fd, (sockaddr*)&addr->addr, &addr->addr_len);
    errif(clnt_sockfd == -1, "socket accept error");
    return clnt_sockfd;
}

int Socket::getFd(){
    return fd;
}
```

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## InetAddress.cpp
```cpp
#include "InetAddress.h"
#include <string.h>
InetAddress::InetAddress() : addr_len(sizeof(addr)){
    bzero(&addr, sizeof(addr));
}
InetAddress::InetAddress(const char* ip, uint16_t port) : addr_len(sizeof(addr)){
    bzero(&addr, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr(ip);
    addr.sin_port = htons(port);
    addr_len = sizeof(addr);
}

InetAddress::~InetAddress(){
}

```

## server.cpp
```cpp
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <vector>
#include "util.h"
#include "Epoll.h"
#include "InetAddress.h"
#include "Socket.h"

#define MAX_EVENTS 1024
#define READ_BUFFER 1024

void setnonblocking(int fd){
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK);
}
void handleReadEvent(int);

int main() {
    Socket *serv_sock = new Socket();
    InetAddress *serv_addr = new InetAddress("127.0.0.1", 8888);
    serv_sock->bind(serv_addr);
    serv_sock->listen();    
    Epoll *ep = new Epoll();
    serv_sock->setnonblocking();
    ep->addFd(serv_sock->getFd(), EPOLLIN | EPOLLET);
    while(true){
        std::vector<epoll_event> events = ep->poll();
        int nfds = events.size();
        for(int i = 0; i < nfds; ++i){
            if(events[i].data.fd == serv_sock->getFd()){        //新客户端连接
                InetAddress *clnt_addr = new InetAddress();      //会发生内存泄露！没有delete
                Socket *clnt_sock = new Socket(serv_sock->accept(clnt_addr));       //会发生内存泄露！没有delete
                printf("new client fd %d! IP: %s Port: %d\n", clnt_sock->getFd(), inet_ntoa(clnt_addr->addr.sin_addr), ntohs(clnt_addr->addr.sin_port));
                clnt_sock->setnonblocking();
                ep->addFd(clnt_sock->getFd(), EPOLLIN | EPOLLET);
            } else if(events[i].events & EPOLLIN){      //可读事件
                handleReadEvent(events[i].data.fd);
            } else{         //其他事件，之后的版本实现
                printf("something else happened\n");
            }
        }
    }
    delete serv_sock;
    delete serv_addr;
    return 0;
}

void handleReadEvent(int sockfd){
    char buf[READ_BUFFER];
    while(true){    //由于使用非阻塞IO，读取客户端buffer，一次读取buf大小数据，直到全部读取完毕
        bzero(&buf, sizeof(buf));
        ssize_t bytes_read = read(sockfd, buf, sizeof(buf));
        if(bytes_read > 0){
            printf("message from client fd %d: %s\n", sockfd, buf);
            write(sockfd, buf, sizeof(buf));
        } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
            printf("continue reading");
            continue;
        } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
            printf("finish reading once, errno: %d\n", errno);
            break;
        } else if(bytes_read == 0){  //EOF，客户端断开连接
            printf("EOF, client fd %d disconnected\n", sockfd);
            close(sockfd);   //关闭socket会自动将文件描述符从epoll树上移除
            break;
        }
    }
}

```

## Makefile
```makefile
server:
	g++ util.cpp client.cpp -o client && \
	g++ util.cpp server.cpp Epoll.cpp InetAddress.cpp Socket.cpp -o server
clean:
	rm server && rm client
```

---

# day05-epoll高级用法-Channel登场

在上一天，我们已经完整地开发了一个echo服务器，并且引入面向对象编程的思想，初步封装了`Socket`、`InetAddress`和`Epoll`，大大精简了主程序，隐藏了底层语言实现细节、增加了可读性。

让我们来回顾一下我们是如何使用`epoll`：将一个文件描述符添加到`epoll`红黑树，当该文件描述符上有事件发生时，拿到它、处理事件，这样我们每次只能拿到一个文件描述符，也就是一个`int`类型的整型值。试想，如果一个服务器同时提供不同的服务，如HTTP、FTP等，那么就算文件描述符上发生的事件都是可读事件，不同的连接类型也将决定不同的处理逻辑，仅仅通过一个文件描述符来区分显然会很麻烦，我们更加希望拿到关于这个文件描述符更多的信息。

在day03介绍`epoll`时，曾讲过`epoll_event`结构体：
```cpp
typedef union epoll_data {
  void *ptr;
  int fd;
  uint32_t u32;
  uint64_t u64;
} epoll_data_t;
struct epoll_event {
  uint32_t events;	/* Epoll events */
  epoll_data_t data;	/* User data variable */
} __EPOLL_PACKED;
```
可以看到，epoll中的`data`其实是一个union类型，可以储存一个指针。而通过指针，理论上我们可以指向任何一个地址块的内容，可以是一个类的对象，这样就可以将一个文件描述符封装成一个`Channel`类，一个Channel类自始至终只负责一个文件描述符，对不同的服务、不同的事件类型，都可以在类中进行不同的处理，而不是仅仅拿到一个`int`类型的文件描述符。
> 这里读者务必先了解C++中的union类型，在《C++ Primer（第五版）》第十九章第六节有详细说明。

`Channel`类的核心成员如下：
```cpp
class Channel{
private:
    Epoll *ep;
    int fd;
    uint32_t events;
    uint32_t revents;
    bool inEpoll;
};
```
显然每个文件描述符会被分发到一个`Epoll`类，用一个`ep`指针来指向。类中还有这个`Channel`负责的文件描述符。另外是两个事件变量，`events`表示希望监听这个文件描述符的哪些事件，因为不同事件的处理方式不一样。`revents`表示在`epoll`返回该`Channel`时文件描述符正在发生的事件。`inEpoll`表示当前`Channel`是否已经在`epoll`红黑树中，为了注册`Channel`的时候方便区分使用`EPOLL_CTL_ADD`还是`EPOLL_CTL_MOD`。

接下来以`Channel`的方式使用epoll：
新建一个`Channel`时，必须说明该`Channel`与哪个`epoll`和`fd`绑定：
```cpp
Channel *servChannel = new Channel(ep, serv_sock->getFd());
```
这时该`Channel`还没有被添加到epoll红黑树，因为`events`没有被设置，不会监听该`Channel`上的任何事件发生。如果我们希望监听该`Channel`上发生的读事件，需要调用一个`enableReading`函数：
```cpp
servChannel->enableReading();
```
调用这个函数后，如`Channel`不在epoll红黑树中，则添加，否则直接更新`Channel`、打开允许读事件。`enableReading`函数如下：
```cpp
void Channel::enableReading(){
    events = EPOLLIN | EPOLLET;
    ep->updateChannel(this);
}
```
可以看到该函数做了两件事，将要监听的事件`events`设置为读事件并采用ET模式，然后在ep指针指向的Epoll红黑树中更新该`Channel`，`updateChannel`函数的实现如下：
```cpp
void Epoll::updateChannel(Channel *channel){
    int fd = channel->getFd();  //拿到Channel的文件描述符
    struct epoll_event ev;
    bzero(&ev, sizeof(ev));
    ev.data.ptr = channel;
    ev.events = channel->getEvents();   //拿到Channel希望监听的事件
    if(!channel->getInEpoll()){
        errif(epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1, "epoll add error");//添加Channel中的fd到epoll
        channel->setInEpoll();
    } else{
        errif(epoll_ctl(epfd, EPOLL_CTL_MOD, fd, &ev) == -1, "epoll modify error");//已存在，则修改
    }
}
```
在使用时，我们可以通过`Epoll`类中的`poll()`函数获取当前有事件发生的`Channel`：
```cpp
while(true){
    vector<Channel*> activeChannels = ep->poll();
    // activeChannels是所有有事件发生的Channel
}
```
注：在今天教程的源代码中，并没有将事件处理改为使用`Channel`回调函数的方式，仍然使用了之前对文件描述符进行处理的方法，这是错误的，将在明天的教程中进行改写。

至此，day05的主要教程已经结束了，完整源代码请在`code/day05`文件夹。服务器的功能和昨天一样，添加了`Channel`类，可以让我们更加方便简单、多样化地处理epoll中发生的事件。同时脱离了底层，将epoll、文件描述符和事件进行了抽象，形成了事件分发的模型，这也是Reactor模式的核心，将在明天的教程进行讲解。

进入`code/day05`文件夹，使用make命令编译，将会得到`server`和`client`，输入命令`./server`开始运行服务器。然后在一个新终端输入命令`./client`运行客户端，可以看到服务器接收到了客户端的连接请求，并成功连接。再新开一个或多个终端，运行client，可以看到这些客户端也同时连接到了服务器。此时我们在任意一个client输入一条信息，服务器都显示并发送到该客户端。如使用`control+c`终止掉某个client，服务器回显示这个client已经断开连接，但其他client并不受影响。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day05](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day05)

## util.cpp
```cpp
#include "util.h"
#include <stdio.h>
#include <stdlib.h>

void errif(bool condition, const char *errmsg){
    if(condition){
        perror(errmsg);
        exit(EXIT_FAILURE);
    }
}
```

## Epoll.cpp
```cpp
#include "Epoll.h"
#include "util.h"
#include "Channel.h"
#include <unistd.h>
#include <string.h>

#define MAX_EVENTS 1000

Epoll::Epoll() : epfd(-1), events(nullptr){
    epfd = epoll_create1(0);
    errif(epfd == -1, "epoll create error");
    events = new epoll_event[MAX_EVENTS];
    bzero(events, sizeof(*events) * MAX_EVENTS);
}

Epoll::~Epoll(){
    if(epfd != -1){
        close(epfd);
        epfd = -1;
    }
    delete [] events;
}

void Epoll::addFd(int fd, uint32_t op){
    struct epoll_event ev;
    bzero(&ev, sizeof(ev));
    ev.data.fd = fd;
    ev.events = op;
    errif(epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1, "epoll add event error");
}

// std::vector<epoll_event> Epoll::poll(int timeout){
//     std::vector<epoll_event> activeEvents;
//     int nfds = epoll_wait(epfd, events, MAX_EVENTS, timeout);
//     errif(nfds == -1, "epoll wait error");
//     for(int i = 0; i < nfds; ++i){
//         activeEvents.push_back(events[i]);
//     }
//     return activeEvents;
// }

std::vector<Channel*> Epoll::poll(int timeout){
    std::vector<Channel*> activeChannels;
    int nfds = epoll_wait(epfd, events, MAX_EVENTS, timeout);
    errif(nfds == -1, "epoll wait error");
    for(int i = 0; i < nfds; ++i){
        Channel *ch = (Channel*)events[i].data.ptr;
        ch->setRevents(events[i].events);
        activeChannels.push_back(ch);
    }
    return activeChannels;
}

void Epoll::updateChannel(Channel *channel){
    int fd = channel->getFd();
    struct epoll_event ev;
    bzero(&ev, sizeof(ev));
    ev.data.ptr = channel;
    ev.events = channel->getEvents();
    if(!channel->getInEpoll()){
        errif(epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1, "epoll add error");
        channel->setInEpoll();
        // debug("Epoll: add Channel to epoll tree success, the Channel's fd is: ", fd);
    } else{
        errif(epoll_ctl(epfd, EPOLL_CTL_MOD, fd, &ev) == -1, "epoll modify error");
        // debug("Epoll: modify Channel in epoll tree success, the Channel's fd is: ", fd);
    }
}
```

## Socket.cpp
```cpp
#include "Socket.h"
#include "InetAddress.h"
#include "util.h"
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>

Socket::Socket() : fd(-1){
    fd = socket(AF_INET, SOCK_STREAM, 0);
    errif(fd == -1, "socket create error");
}
Socket::Socket(int _fd) : fd(_fd){
    errif(fd == -1, "socket create error");
}

Socket::~Socket(){
    if(fd != -1){
        close(fd);
        fd = -1;
    }
}

void Socket::bind(InetAddress *addr){
    errif(::bind(fd, (sockaddr*)&addr->addr, addr->addr_len) == -1, "socket bind error");
}

void Socket::listen(){
    errif(::listen(fd, SOMAXCONN) == -1, "socket listen error");
}
void Socket::setnonblocking(){
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK);
}

int Socket::accept(InetAddress *addr){
    int clnt_sockfd = ::accept(fd, (sockaddr*)&addr->addr, &addr->addr_len);
    errif(clnt_sockfd == -1, "socket accept error");
    return clnt_sockfd;
}

int Socket::getFd(){
    return fd;
}
```

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## InetAddress.cpp
```cpp
#include "InetAddress.h"
#include <string.h>
InetAddress::InetAddress() : addr_len(sizeof(addr)){
    bzero(&addr, sizeof(addr));
}
InetAddress::InetAddress(const char* ip, uint16_t port) : addr_len(sizeof(addr)){
    bzero(&addr, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr(ip);
    addr.sin_port = htons(port);
    addr_len = sizeof(addr);
}

InetAddress::~InetAddress(){
}

```

## server.cpp
```cpp
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <vector>
#include "util.h"
#include "Epoll.h"
#include "InetAddress.h"
#include "Socket.h"
#include "Channel.h"

#define MAX_EVENTS 1024
#define READ_BUFFER 1024

void setnonblocking(int fd){
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK);
}
void handleReadEvent(int);

int main() {
    Socket *serv_sock = new Socket();
    InetAddress *serv_addr = new InetAddress("127.0.0.1", 8888);
    serv_sock->bind(serv_addr);
    serv_sock->listen();    
    Epoll *ep = new Epoll();
    serv_sock->setnonblocking();
    Channel *servChannel = new Channel(ep, serv_sock->getFd());
    servChannel->enableReading();
    while(true){
        std::vector<Channel*> activeChannels = ep->poll();
        int nfds = activeChannels.size();
        for(int i = 0; i < nfds; ++i){
            int chfd = activeChannels[i]->getFd();
            if(chfd == serv_sock->getFd()){        //新客户端连接
                InetAddress *clnt_addr = new InetAddress();      //会发生内存泄露！没有delete
                Socket *clnt_sock = new Socket(serv_sock->accept(clnt_addr));       //会发生内存泄露！没有delete
                printf("new client fd %d! IP: %s Port: %d\n", clnt_sock->getFd(), inet_ntoa(clnt_addr->addr.sin_addr), ntohs(clnt_addr->addr.sin_port));
                clnt_sock->setnonblocking();
                Channel *clntChannel = new Channel(ep, clnt_sock->getFd());
                clntChannel->enableReading();
            } else if(activeChannels[i]->getRevents() & EPOLLIN){      //可读事件
                handleReadEvent(activeChannels[i]->getFd());
            } else{         //其他事件，之后的版本实现
                printf("something else happened\n");
            }
        }
    }
    delete serv_sock;
    delete serv_addr;
    return 0;
}

void handleReadEvent(int sockfd){
    char buf[READ_BUFFER];
    while(true){    //由于使用非阻塞IO，读取客户端buffer，一次读取buf大小数据，直到全部读取完毕
        bzero(&buf, sizeof(buf));
        ssize_t bytes_read = read(sockfd, buf, sizeof(buf));
        if(bytes_read > 0){
            printf("message from client fd %d: %s\n", sockfd, buf);
            write(sockfd, buf, sizeof(buf));
        } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
            printf("continue reading");
            continue;
        } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
            printf("finish reading once, errno: %d\n", errno);
            break;
        } else if(bytes_read == 0){  //EOF，客户端断开连接
            printf("EOF, client fd %d disconnected\n", sockfd);
            close(sockfd);   //关闭socket会自动将文件描述符从epoll树上移除
            break;
        }
    }
}

```

## Channel.cpp
```cpp
#include "Channel.h"
#include "Epoll.h"

Channel::Channel(Epoll *_ep, int _fd) : ep(_ep), fd(_fd), events(0), revents(0), inEpoll(false){

}

Channel::~Channel()
{
}

void Channel::enableReading(){
    events = EPOLLIN | EPOLLET;
    ep->updateChannel(this);
}

int Channel::getFd(){
    return fd;
}

uint32_t Channel::getEvents(){
    return events;
}
uint32_t Channel::getRevents(){
    return revents;
}

bool Channel::getInEpoll(){
    return inEpoll;
}

void Channel::setInEpoll(){
    inEpoll = true;
}

// void Channel::setEvents(uint32_t _ev){
//     events = _ev;
// }

void Channel::setRevents(uint32_t _ev){
    revents = _ev;
}
```

## Makefile
```makefile
server:
	g++ util.cpp client.cpp -o client && \
	g++ util.cpp server.cpp Epoll.cpp InetAddress.cpp Socket.cpp Channel.cpp -o server
clean:
	rm server && rm client
```

---

# day06-服务器与事件驱动核心类登场

在上一天，我们为每一个添加到epoll的文件描述符都添加了一个`Channel`，用户可以自由注册各种事件、很方便地根据不同事件类型设置不同回调函数（在当前的源代码中只支持了目前所需的可读事件，将在之后逐渐进行完善）。我们的服务器已经基本成型，但目前从新建socket、接受客户端连接到处理客户端事件，整个程序结构是顺序化、流程化的，我们甚至可以使用一个单一的流程图来表示整个程序。而流程化程序设计的缺点之一是不够抽象，当我们的服务器结构越来越庞大、功能越来越复杂、模块越来越多，这种顺序程序设计的思想显然是不能满足需求的。

对于服务器开发，我们需要用到更抽象的设计模式。从代码中我们可以看到，不管是接受客户端连接还是处理客户端事件，都是围绕epoll来编程，可以说epoll是整个程序的核心，服务器做的事情就是监听epoll上的事件，然后对不同事件类型进行不同的处理。这种以事件为核心的模式又叫事件驱动，事实上几乎所有的现代服务器都是事件驱动的。和传统的请求驱动模型有很大不同，事件的捕获、通信、处理和持久保留是解决方案的核心结构。libevent就是一个著名的C语言事件驱动库。

需要注意的是，事件驱动不是服务器开发的专利。事件驱动是一种设计应用的思想、开发模式，而服务器是根据客户端的不同请求提供不同的服务的一个实体应用，服务器开发可以采用事件驱动模型、也可以不采用。事件驱动模型也可以在服务器之外的其他类型应用中出现，如进程通信、k8s调度、V8引擎、Node.js等。

理解了以上的概念，就能容易理解服务器开发的两种经典模式——Reactor和Proactor模式。详细请参考游双《Linux高性能服务器编程》第八章第四节、陈硕《Linux多线程服务器编程》第六章第六节。

> 如何深刻理解Reactor和Proactor？ - 小林coding的回答 - 知乎
https://www.zhihu.com/question/26943938/answer/1856426252

由于Linux内核系统调用的设计更加符合Reactor模式，所以绝大部分高性能服务器都采用Reactor模式进行开发，我们的服务器也使用这种模式。

接下来我们要将服务器改造成Reactor模式。首先我们将整个服务器抽象成一个`Server`类，这个类中有一个main-Reactor（在这个版本没有sub-Reactor），里面的核心是一个`EventLoop`（libevent中叫做EventBase），这是一个事件循环，我们添加需要监听的事务到这个事件循环内，每次有事件发生时就会通知（在程序中返回给我们`Channel`），然后根据不同的描述符、事件类型进行处理（以回调函数的方式）。
> 如果你不太清楚这个自然段在讲什么，请先看一看前面提到的两本书的具体章节。

EventLoop类的定义如下：
```cpp
class EventLoop {
private:
    Epoll *ep;
    bool quit;
public:
    EventLoop();
    ~EventLoop();
    void loop();
    void updateChannel(Channel*);
};
```
调用`loop()`函数可以开始事件驱动，实际上就是原来的程序中调用`epoll_wait()`函数的死循环：
```cpp
void EventLoop::loop(){
    while(!quit){
    std::vector<Channel*> chs;
        chs = ep->poll();
        for(auto it = chs.begin(); it != chs.end(); ++it){
            (*it)->handleEvent();
        }
    }
}
```
现在我们可以以这种方式来启动服务器，和muduo的代码已经很接近了：
```cpp
EventLoop *loop = new EventLoop();
Server *server = new Server(loop);
loop->loop();
```
服务器定义如下：
```cpp
class Server {
private:
    EventLoop *loop;
public:
    Server(EventLoop*);
    ~Server();
    void handleReadEvent(int);
    void newConnection(Socket *serv_sock);
};
```
这个版本服务器内只有一个`EventLoop`，当其中有可读事件发生时，我们可以拿到该描述符对应的`Channel`。在新建`Channel`时，根据`Channel`描述符的不同分别绑定了两个回调函数，`newConnection()`函数被绑定到服务器socket上，`handlrReadEvent()`被绑定到新接受的客户端socket上。这样如果服务器socket有可读事件，`Channel`里的`handleEvent()`函数实际上会调用`Server`类的`newConnection()`新建连接。如果客户端socket有可读事件，`Channel`里的`handleEvent()`函数实际上会调用`Server`类的`handlrReadEvent()`响应客户端请求。

至此，我们已经抽象出了`EventLoop`和`Channel`，构成了事件驱动模型。这两个类和服务器核心`Server`已经没有任何关系，经过完善后可以被任何程序复用，达到了事件驱动的设计思想，现在我们的服务器也可以看成一个最简易的Reactor模式服务器。

当然，这个Reactor模式并不是一个完整的Reactor模式，如处理事件请求仍然在事件驱动的线程里，这显然违背了Reactor的概念。我们还需要做很多工作，在接下来几天的教程里会进一步完善。


完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day06](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day06)

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "src/util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    return 0;
}
```

## Makefile
```makefile
server:
	g++ src/util.cpp client.cpp -o client && \
	g++ src/util.cpp server.cpp src/Epoll.cpp src/InetAddress.cpp src/Socket.cpp src/Channel.cpp src/EventLoop.cpp src/Server.cpp -o server
clean:
	rm server && rm client
```

---

# day07-为我们的服务器添加一个Acceptor

在上一天，我们分离了服务器类和事件驱动类，将服务器逐渐开发成Reactor模式。至此，所有服务器逻辑（目前只有接受新连接和echo客户端发来的数据）都写在`Server`类里。但很显然，`Server`作为一个服务器类，应该更抽象、更通用，我们应该对服务器进行进一步的模块化。

仔细分析可发现，对于每一个事件，不管提供什么样的服务，首先需要做的事都是调用`accept()`函数接受这个TCP连接，然后将socket文件描述符添加到epoll。当这个IO口有事件发生的时候，再对此TCP连接提供相应的服务。
> 在这里务必先理解TCP的面向连接这一特性，在谢希仁《计算机网络》里有详细的讨论。

因此我们可以分离接受连接这一模块，添加一个`Acceptor`类，这个类有以下几个特点：
- 类存在于事件驱动`EventLoop`类中，也就是Reactor模式的main-Reactor
- 类中的socket fd就是服务器监听的socket fd，每一个Acceptor对应一个socket fd
- 这个类也通过一个独有的`Channel`负责分发到epoll，该Channel的事件处理函数`handleEvent()`会调用Acceptor中的接受连接函数来新建一个TCP连接

根据分析，Acceptor类定义如下：
```cpp
class Acceptor{
private:
    EventLoop *loop;
    Socket *sock;
    InetAddress *addr;
    Channel *acceptChannel;
public:
    Acceptor(EventLoop *_loop);
    ~Acceptor();
    void acceptConnection();
};
```
这样一来，新建连接的逻辑就在`Acceptor`类中。但逻辑上新socket建立后就和之前监听的服务器socket没有任何关系了，TCP连接和`Acceptor`一样，拥有以上提到的三个特点，这两个类之间应该是平行关系。所以新的TCP连接应该由`Server`类来创建并管理生命周期，而不是`Acceptor`。并且将这一部分代码放在`Server`类里也并没有打破服务器的通用性，因为对于所有的服务，都要使用`Acceptor`来建立连接。

为了实现这一设计，我们可以用两种方式：
1. 使用传统的虚类、虚函数来设计一个接口
2. C++11的特性：std::function、std::bind、右值引用、std::move等实现函数回调

虚函数使用起来比较繁琐，程序的可读性也不够清晰明朗，而std::function、std::bind等新标准的出现可以完全替代虚函数，所以本教程采用第二种方式。
> 关于虚函数，在《C++ Primer》第十五章第三节有详细讨论，而C++11后的新标准可以参考欧长坤《现代 C++ 教程》

首先我们需要在Acceptor中定义一个新建连接的回调函数：
```cpp
std::function<void(Socket*)> newConnectionCallback;
```
在新建连接时，只需要调用这个回调函数：
```cpp
void Acceptor::acceptConnection(){
    newConnectionCallback(sock);
}
```
而这个回调函数本身的实现在`Server`类中：
```cpp
void Server::newConnection(Socket *serv_sock){
    // 接受serv_sock上的客户端连接
}
```
> 在今天的代码中，Acceptor的Channel使用了ET模式，事实上使用LT模式更合适，将在之后修复

新建Acceptor时通过std::bind进行绑定:
```cpp
acceptor = new Acceptor(loop);
std::function<void(Socket*)> cb = std::bind(&Server::newConnection, this, std::placeholders::_1);
acceptor->setNewConnectionCallback(cb);
```
这样一来，尽管我们抽象分离出了`Acceptor`，新建连接的工作任然由`Server`类来完成。
> 请确保清楚地知道为什么要这么做再进行之后的学习。

至此，今天的教程已经结束了。在今天，我们设计了服务器接受新连接的`Acceptor`类。测试方法和之前一样，使用`make`得到服务器和客户端程序并运行。虽然服务器功能已经好几天没有变化了，但每一天我们都在不断抽象、不断完善，从结构化、流程化的程序设计，到面向对象程序设计，再到面向设计模式的程序设计，逐渐学习服务器开发的思想与精髓。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day07](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day07)

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "src/util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(8888);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    return 0;
}
```

## Makefile
```makefile
server:
	g++ src/util.cpp client.cpp -o client && \
	g++ src/util.cpp server.cpp src/Epoll.cpp src/InetAddress.cpp src/Socket.cpp src/Channel.cpp src/EventLoop.cpp src/Server.cpp src/Acceptor.cpp -o server
clean:
	rm server && rm client
```

---

# day08-一切皆是类，连TCP连接也不例外

在上一天，我们分离了用于接受连接的`Acceptor`类，并把新建连接的逻辑放在了`Server`类中。在上一天我们还提到了`Acceptor`类最主要的三个特点：
- 类存在于事件驱动`EventLoop`类中，也就是Reactor模式的main-Reactor
- 类中的socket fd就是服务器监听的socket fd，每一个Acceptor对应一个socket fd
- 这个类也通过一个独有的`Channel`负责分发到epoll，该Channel的事件处理函数`handleEvent()`会调用Acceptor中的接受连接函数来新建一个TCP连接

对于TCP协议，三次握手新建连接后，这个连接将会一直存在，直到我们四次挥手断开连接。因此，我们也可以把TCP连接抽象成一个`Connection`类，这个类也有以下几个特点：
- 类存在于事件驱动`EventLoop`类中，也就是Reactor模式的main-Reactor
- 类中的socket fd就是客户端的socket fd，每一个Connection对应一个socket fd
- 每一个类的实例通过一个独有的`Channel`负责分发到epoll，该Channel的事件处理函数`handleEvent()`会调用Connection中的事件处理函数来响应客户端请求

可以看到，`Connection`类和`Acceptor`类是平行关系、十分相似，他们都直接由`Server`管理，由一个`Channel`分发到epoll，通过回调函数处理相应事件。唯一的不同在于，`Acceptor`类的处理事件函数（也就是新建连接功能）被放到了`Server`类中，具体原因在上一天的教程中已经详细说明。而`Connection`类则没有必要这么做，处理事件的逻辑应该由`Connection`类本身来完成。

另外，一个高并发服务器一般只会有一个`Acceptor`用于接受连接（也可以有多个），但可能会同时拥有成千上万个TCP连接，也就是成千上万个`Connection`类的实例，我们需要把这些TCP连接都保存起来。现在我们可以改写服务器核心`Server`类，定义如下：
```cpp
class Server {
private:
    EventLoop *loop;    //事件循环
    Acceptor *acceptor; //用于接受TCP连接
    std::map<int, Connection*> connections; //所有TCP连接
public:
    Server(EventLoop*);
    ~Server();

    void handleReadEvent(int);  //处理客户端请求
    void newConnection(Socket *sock);   //新建TCP连接
    void deleteConnection(Socket *sock);   //断开TCP连接
};
```
在接受连接后，服务器把该TCP连接保存在一个`map`中，键为该连接客户端的socket fd，值为指向该连接的指针。该连接客户端的socket fd通过一个`Channel`类分发到epoll，该`Channel`的事件处理回调函数`handleEvent()`绑定为`Connection`的业务处理函数，这样每当该连接的socket fd上发生事件，就会通过`Channel`调用具体连接类的业务处理函数，伪代码如下：
```cpp
void Connection::echo(int sockfd){
    // 回显sockfd发来的数据
}
Connection::Connection(EventLoop *_loop, Socket *_sock) : loop(_loop), sock(_sock), channel(nullptr){
    channel = new Channel(loop, sock->getFd()); //该连接的Channel
    std::function<void()> cb = std::bind(&Connection::echo, this, sock->getFd()); 
    channel->setCallback(cb); //绑定回调函数
    channel->enableReading(); //打开读事件监听
}
```
对于断开TCP连接操作，也就是销毁一个`Connection`类的实例。由于`Connection`的生命周期由`Server`进行管理，所以也应该由`Server`来删除连接。如果在`Connection`业务中需要断开连接操作，也应该和之前一样使用回调函数来实现，在`Server`新建每一个连接时绑定删除该连接的回调函数：
```cpp
Connection *conn = new Connection(loop, sock);
std::function<void(Socket*)> cb = std::bind(&Server::deleteConnection, this, std::placeholders::_1);
conn->setDeleteConnectionCallback(cb);  // 绑定删除连接的回调函数

void Server::deleteConnection(Socket * sock){
    // 删除连接
}
```
至此，今天的教程已经结束，我们将TCP连接抽象成一个类，服务器模型更加成型。测试方法和之前一样，使用`make`得到服务器和客户端程序并运行。

这个版本是一个比较重要的版本，服务器最核心的几个模块都已经抽象出来，Reactor事件驱动大体成型（除了线程池），各个类的生命周期也大体上合适了，一个完整的单线程服务器设计模式已经编码完成了，读者应该完全理解今天的服务器代码后再继续后面的学习。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day08](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day08)

## client.cpp
```cpp
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "src/util.h"

#define BUFFER_SIZE 1024 

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    errif(sockfd == -1, "socket create error");

    struct sockaddr_in serv_addr;
    bzero(&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(1234);

    errif(connect(sockfd, (sockaddr*)&serv_addr, sizeof(serv_addr)) == -1, "socket connect error");
    
    while(true){
        char buf[BUFFER_SIZE];  //在这个版本，buf大小必须大于或等于服务器端buf大小，不然会出错，想想为什么？
        bzero(&buf, sizeof(buf));
        scanf("%s", buf);
        ssize_t write_bytes = write(sockfd, buf, sizeof(buf));
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        bzero(&buf, sizeof(buf));
        ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
        if(read_bytes > 0){
            printf("message from server: %s\n", buf);
        }else if(read_bytes == 0){
            printf("server socket disconnected!\n");
            break;
        }else if(read_bytes == -1){
            close(sockfd);
            errif(true, "socket read error");
        }
    }
    close(sockfd);
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    return 0;
}

```

## Makefile
```makefile
server:
	g++ src/util.cpp client.cpp -o client && \
	g++ server.cpp \
	src/util.cpp src/Epoll.cpp src/InetAddress.cpp src/Socket.cpp src/Connection.cpp \
	src/Channel.cpp src/EventLoop.cpp src/Server.cpp src/Acceptor.cpp \
	-o server
clean:
	rm server && rm client
```

---

# day09-缓冲区-大作用

在之前的教程中，一个完整的单线程服务器设计模式已经编码完成了。在进入多线程编程之前，应该完全理解单线程服务器的工作原理，因为多线程更加复杂、更加困难，开发难度远大于之前的单线程模式。不仅如此，读者也应根据自己的理解进行二次开发，完善服务器，比如非阻塞式socket模块就值得细细研究。

今天的教程和之前几天的不同，引入了一个最简单、最基本的的缓冲区，可以看作一个完善、改进服务器的例子，更加偏向于细节而不是架构。除了这一细节，读者也可以按照自己的理解完善服务器。

同时，我们已经封装了socket、epoll等基础组件，这些组件都可以复用。现在我们完全可以使用这个网络库来改写客户端程序，让程序更加简单明了，读者可以自己尝试用这些组件写一个客户端，然后和源代码中的对照。

在没有缓冲区的时候，服务器回送客户端消息的代码如下：
```cpp
#define READ_BUFFER 1024
void Connection::echo(int sockfd){
    char buf[READ_BUFFER];
    while(true){    //由于使用非阻塞IO，读取客户端buffer，一次读取buf大小数据，直到全部读取完毕
        bzero(&buf, sizeof(buf));
        ssize_t bytes_read = read(sockfd, buf, sizeof(buf));
        if(bytes_read > 0){
            printf("message from client fd %d: %s\n", sockfd, buf);
            write(sockfd, buf, sizeof(buf));   // 发送给客户端
        } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
            printf("continue reading");
            continue;
        } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
            printf("finish reading once, errno: %d\n", errno);
            break;
        } else if(bytes_read == 0){  //EOF，客户端断开连接
            printf("EOF, client fd %d disconnected\n", sockfd);
            deleteConnectionCallback(sock);
            break;
        }
    }
}
```
这是非阻塞式socket IO的读取，可以看到使用的读缓冲区大小为1024，每次从TCP缓冲区读取1024大小的数据到读缓冲区，然后发送给客户端。这是最底层C语言的编码，在逻辑上有很多不合适的地方。比如我们不知道客户端信息的真正大小是多少，只能以1024的读缓冲区去读TCP缓冲区（就算TCP缓冲区的数据没有1024，也会把后面的用空值补满）；也不能一次性读取所有客户端数据，再统一发给客户端。
> 关于TCP缓冲区、socket IO读取的细节，在《UNIX网络编程》卷一中有详细说明，想要精通网络编程几乎是必看的

虽然以上提到的缺点以C语言编程的方式都可以解决，但我们仍然希望以一种更加优美的方式读写socket上的数据，和其他模块一样，脱离底层，让我们使用的时候不用在意太多底层细节。所以封装一个缓冲区是很有必要的，为每一个`Connection`类分配一个读缓冲区和写缓冲区，从客户端读取来的数据都存放在读缓冲区里，这样`Connection`类就不再直接使用`char buf[]`这种最笨的缓冲区来处理读写操作。

缓冲区类的定义如下：
```cpp
class Buffer {
private:
    std::string buf;
public:
    void append(const char* _str, int _size);
    ssize_t size();
    const char* c_str();
    void clear();
    ......
};
```
> 这个缓冲区类使用`std::string`来储存数据，也可以使用`std::vector<char>`，有兴趣可以比较一下这两者的性能。

为每一个TCP连接分配一个读缓冲区后，就可以把客户端的信息读取到这个缓冲区内，缓冲区大小就是客户端发送的报文真实大小，代码如下：
```cpp
void Connection::echo(int sockfd){
    char buf[1024];     //这个buf大小无所谓
    while(true){    //由于使用非阻塞IO，读取客户端buffer，一次读取buf大小数据，直到全部读取完毕
        bzero(&buf, sizeof(buf));
        ssize_t bytes_read = read(sockfd, buf, sizeof(buf));
        if(bytes_read > 0){
            readBuffer->append(buf, bytes_read);
        } else if(bytes_read == -1 && errno == EINTR){  //客户端正常中断、继续读取
            printf("continue reading");
            continue;
        } else if(bytes_read == -1 && ((errno == EAGAIN) || (errno == EWOULDBLOCK))){//非阻塞IO，这个条件表示数据全部读取完毕
            printf("message from client fd %d: %s\n", sockfd, readBuffer->c_str());
            errif(write(sockfd, readBuffer->c_str(), readBuffer->size()) == -1, "socket write error");
            readBuffer->clear();
            break;
        } else if(bytes_read == 0){  //EOF，客户端断开连接
            printf("EOF, client fd %d disconnected\n", sockfd);
            deleteConnectionCallback(sock);
            break;
        }
    }
}
```
在这里依然有一个`char buf[]`缓冲区，用于系统调用`read()`的读取，这个缓冲区大小无所谓，但太大或太小都可能对性能有影响（太小读取次数增多，太大资源浪费、单次读取速度慢），设置为1到设备TCP缓冲区的大小都可以。以上代码会把socket IO上的可读数据全部读取到缓冲区，缓冲区大小就等于客户端发送的数据大小。全部读取完成之后，可以构造一个写缓冲区、填好数据发送给客户端。由于是echo服务器，所以这里使用了相同的缓冲区。

至此，今天的教程已经结束，这个缓冲区只是为了满足当前的服务器功能而构造的一个最简单的`Buffer`类，还需要进一步完善，读者可以按照自己的方式构建缓冲区类，完善其他细节，为后续的多线程服务器做准备。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day09](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day09)

## client.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/InetAddress.h"
#include "src/Socket.h"

using namespace std;

int main() {
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();
    
    while(true){
        sendBuffer->getline();
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("message from server: %s\n", readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    delete server;
    delete loop;
    return 0;
}

```

## Makefile
```makefile
server:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp client.cpp -o client && \
	g++ server.cpp \
	src/util.cpp src/Epoll.cpp src/InetAddress.cpp src/Socket.cpp src/Connection.cpp \
	src/Channel.cpp src/EventLoop.cpp src/Server.cpp src/Acceptor.cpp src/Buffer.cpp \
	-o server
clean:
	rm server && rm client
```

---

# day10-加入线程池到服务器

今天是本教程的第十天，在之前，我们已经编码完成了一个完整的单线程服务器，最核心的几个模块都已经抽象出来，Reactor事件驱动大体成型（除了线程池），各个类的生命周期也大体上合适了，读者应该完全理解之前的服务器代码后再开始今天的学习。

观察当前的服务器架构，不难发现我们的Reactor模型少了最关键、最重要的一个模块：线程池。当发现socket fd有事件时，我们应该分发给一个工作线程，由这个工作线程处理fd上面的事件。而当前我们的代码是单线程模式，所有fd上的事件都由主线程（也就是EventLoop线程）处理，这是大错特错的，试想如果每一个事件相应需要1秒时间，那么当1000个事件同时到来，EventLoop线程将会至少花费1000秒来传输数据，还有函数调用等其他开销，服务器将直接宕机。

在之前的教程已经讲过，每一个Reactor只应该负责事件分发而不应该负责事件处理。今天我们将构建一个最简单的线程池，用于事件处理。

线程池有许多种实现方法，最容易想到的一种是每有一个新任务、就开一个新线程执行。这种方式最大的缺点是线程数不固定，试想如果在某一时刻有1000个并发请求，那么就需要开1000个线程，如果CPU只有8核或16核，物理上不能支持这么高的并发，那么线程切换会耗费大量的资源。为了避免服务器负载不稳定，这里采用了固定线程数的方法，即启动固定数量的工作线程，一般是CPU核数（物理支持的最大并发数），然后将任务添加到任务队列，工作线程不断主动取出任务队列的任务执行。

关于线程池，需要特别注意的有两点，一是在多线程环境下任务队列的读写操作都应该考虑互斥锁，二是当任务队列为空时CPU不应该不断轮询耗费CPU资源。为了解决第一点，这里使用`std::mutex`来对任务队列进行加锁解锁。为了解决第二个问题，使用了条件变量`std::condition_variable`。
> 关于`std::function`、`std::mutex`和`std::condition_variable`基本使用方法本教程不会涉及到，但读者应当先熟知，可以参考欧长坤《现代 C++ 教程》

线程池定义如下：
```cpp
class ThreadPool {
private:
    std::vector<std::thread> threads;
    std::queue<std::function<void()>> tasks;
    std::mutex tasks_mtx;
    std::condition_variable cv;
    bool stop;
public:
    ThreadPool(int size = 10);  // 默认size最好设置为std::thread::hardware_concurrency()
    ~ThreadPool();
    void add(std::function<void()>);
};
```
当线程池被构造时：
```cpp
ThreadPool::ThreadPool(int size) : stop(false){
    for(int i = 0; i < size; ++i){  //  启动size个线程
        threads.emplace_back(std::thread([this](){  //定义每个线程的工作函数
            while(true){    
                std::function<void()> task;
                {   //在这个{}作用域内对std::mutex加锁，出了作用域会自动解锁，不需要调用unlock()
                    std::unique_lock<std::mutex> lock(tasks_mtx);
                    cv.wait(lock, [this](){     //等待条件变量，条件为任务队列不为空或线程池停止
                        return stop || !tasks.empty();
                    });
                    if(stop && tasks.empty()) return;   //任务队列为空并且线程池停止，退出线程
                    task = tasks.front();   //从任务队列头取出一个任务
                    tasks.pop();
                }
                task();     //执行任务
            }
        }));
    }
}
```
当我们需要添加任务时，只需要将任务添加到任务队列：
```cpp
void ThreadPool::add(std::function<void()> func){
    { //在这个{}作用域内对std::mutex加锁，出了作用域会自动解锁，不需要调用unlock()
        std::unique_lock<std::mutex> lock(tasks_mtx);
        if(stop)
            throw std::runtime_error("ThreadPool already stop, can't add task any more");
        tasks.emplace(func);
    }
    cv.notify_one();    //通知一次条件变量
}
```
在线程池析构时，需要注意将已经添加的所有任务执行完，最好不采用外部的暴力kill、而是让每个线程从内部自动退出，具体实现参考源代码。

这样一个最简单的线程池就写好了，在源代码中，当`Channel`类有事件需要处理时，将这个事件处理添加到线程池，主线程`EventLoop`就可以继续进行事件循环，而不在乎某个socket fd上的事件处理。

至此，今天的教程已经结束，一个完整的Reactor模式才正式成型。这个线程池只是为了满足我们的需要构建出的最简单的线程池，存在很多问题。比如，由于任务队列的添加、取出都存在拷贝操作，线程池不会有太好的性能，只能用来学习，正确做法是使用右值移动、完美转发等阻止拷贝。另外线程池只能接受`std::function<void()>`类型的参数，所以函数参数需要事先使用`std::bind()`，并且无法得到返回值。针对这些缺点，将会在明天的教程进行修复。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day10](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day10)

## ThreadPoolTest.cpp
```cpp
#include <iostream>
#include <string>
#include "src/ThreadPool.h"

void print(int a, double b, const char *c, std::string d){
    std::cout << a << b << c << d << std::endl;
}

void test(){
    std::cout << "hellp" << std::endl;
}

int main(int argc, char const *argv[])
{
    ThreadPool *poll = new ThreadPool();
    std::function<void()> func = std::bind(print, 1, 3.14, "hello", std::string("world"));
    poll->add(func);
    func = test;
    poll->add(func);
    delete poll;
    return 0;
}

```

## client.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/InetAddress.h"
#include "src/Socket.h"

using namespace std;

int main() {
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();
    
    while(true){
        sendBuffer->getline();
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("message from server: %s\n", readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    delete server;
    delete loop;
    return 0;
}

```

## Makefile
```makefile
server:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp client.cpp -o client && \
	g++ server.cpp \
	-pthread \
	src/util.cpp src/Epoll.cpp src/InetAddress.cpp src/Socket.cpp src/Connection.cpp \
	src/Channel.cpp src/EventLoop.cpp src/Server.cpp src/Acceptor.cpp src/Buffer.cpp \
	src/ThreadPool.cpp \
	-o server
clean:
	rm server && rm client

threadTest:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest
```

---

# day11-完善线程池，加入一个简单的测试程序

在昨天的教程里，我们添加了一个最简单的线程池到服务器，一个完整的Reactor模式正式成型。这个线程池只是为了满足我们的需要构建出的最简单的线程池，存在很多问题。比如，由于任务队列的添加、取出都存在拷贝操作，线程池不会有太好的性能，只能用来学习，正确做法是使用右值移动、完美转发等阻止拷贝。另外线程池只能接受`std::function<void()>`类型的参数，所以函数参数需要事先使用`std::bind()`，并且无法得到返回值。

为了解决以上提到的问题，线程池的构造函数和析构函数都不会有太大变化，唯一需要改变的是将任务添加到任务队列的`add`函数。我们希望使用`add`函数前不需要手动绑定参数，而是直接传递，并且可以得到任务的返回值。新的实现代码如下：
```cpp
template<class F, class... Args>
auto ThreadPool::add(F&& f, Args&&... args) -> std::future<typename std::result_of<F(Args...)>::type> {
    using return_type = typename std::result_of<F(Args...)>::type;  //返回值类型

    auto task = std::make_shared< std::packaged_task<return_type()> >(  //使用智能指针
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)  //完美转发参数
        );  
        
    std::future<return_type> res = task->get_future();  // 使用期约
    {   //队列锁作用域
        std::unique_lock<std::mutex> lock(tasks_mtx);   //加锁

        if(stop)
            throw std::runtime_error("enqueue on stopped ThreadPool");

        tasks.emplace([task](){ (*task)(); });  //将任务添加到任务队列
    }
    cv.notify_one();    //通知一次条件变量
    return res;     //返回一个期约
}
```
这里使用了大量C++11之后的新标准，具体使用方法可以参考欧长坤《现代 C++ 教程》。另外这里使用了模版，所以不能放在cpp文件，因为C++编译器不支持模版的分离编译
> 这是一个复杂的问题，具体细节请参考《深入理解计算机系统》有关编译、链接的章节

此外，我们希望对现在的服务器进行多线程、高并发的测试，所以需要使用网络库写一个简单的多线程高并发测试程序，具体实现请参考源代码，使用方式如下：

```bash
./test -t 10000 -m 10 (-w 100)
# 10000个线程，每个线程回显10次，建立连接后等待100秒开始发送消息（可用于测试服务器能同时保持的最大连接数）。不指定w参数，则建立连接后开始马上发送消息。
```
注意Makefile文件也已重写，现在使用make只能编译服务器，客户端、测试程序的编译指令请参考Makefile文件，服务器程序编译后可以使用vscode调试。也可以使用gdb调试：
```bash
gdb server  #使用gdb调试
r           #执行
where / bt  #查看调用栈
```
今天还发现了之前版本的一个缺点：对于`Acceptor`，接受连接的处理时间较短、报文数据极小，并且一般不会有特别多的新连接在同一时间到达，所以`Acceptor`没有必要采用epoll ET模式，也没有必要用线程池。由于不会成为性能瓶颈，为了简单最好使用阻塞式socket，故今天的源代码中做了以下改变：
1. Acceptor socket fd（服务器监听socket）使用阻塞式
2. Acceptor使用LT模式，建立好连接后处理事件fd读写用ET模式
3. Acceptor建立连接不使用线程池，建立好连接后处理事件用线程池

至此，今天的教程已经结束了。使用测试程序来测试我们的服务器，可以发现并发轻松上万。这种设计架构最容易想到、也最容易实现，但有很多缺点，具体请参考陈硕《Linux多线程服务器编程》第三章，在明天的教程中将使用one loop per thread模式改写。

此外，多线程系统编程是一件极其复杂的事情，比此教程中的设计复杂得多，由于这是入门教程，故不会涉及到太多细节，作者也还没有水平讲好这个问题。但要想成为一名合格的C++程序员，高并发编程是必备技能，还需要年复一年地阅读大量书籍、进行大量实践。
> 路漫漫其修远兮，吾将上下而求索    ———屈原《离骚》

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day11](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day11)

## ThreadPoolTest.cpp
```cpp
#include <iostream>
#include <string>
#include "src/ThreadPool.h"

void print(int a, double b, const char *c, std::string d){
    std::cout << a << b << c << d << std::endl;
}

void test(){
    std::cout << "hellp" << std::endl;
}

int main(int argc, char const *argv[])
{
    ThreadPool *poll = new ThreadPool();
    std::function<void()> func = std::bind(print, 1, 3.14, "hello", std::string("world"));
    poll->add(func);
    func = test;
    poll->add(func);
    delete poll;
    return 0;
}

```

## client.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/InetAddress.h"
#include "src/Socket.h"

using namespace std;

int main() {
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();
    
    while(true){
        sendBuffer->getline();
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("message from server: %s\n", readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    return 0;
}

```

## test.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include <functional>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/InetAddress.h"
#include "src/Socket.h"
#include "src/ThreadPool.h"

using namespace std;

void oneClient(int msgs, int wait){
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();

    sleep(wait);
    int count = 0;
    while(count < msgs){
        sendBuffer->setBuf("I'm client!");
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("count: %d, message from server: %s\n", count++, readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
}

int main(int argc, char *argv[]) {
    int threads = 100;
    int msgs = 100;
    int wait = 0;
    int o;
    const char *optstring = "t:m:w:";
    while ((o = getopt(argc, argv, optstring)) != -1) {
        switch (o) {
            case 't':
                threads = stoi(optarg);
                break;
            case 'm':
                msgs = stoi(optarg);
                break;
            case 'w':
                wait = stoi(optarg);
                break;
            case '?':
                printf("error optopt: %c\n", optopt);
                printf("error opterr: %d\n", opterr);
                break;
        }
    }

    ThreadPool *poll = new ThreadPool(threads);
    std::function<void()> func = std::bind(oneClient, msgs, wait);
    for(int i = 0; i < threads; ++i){
        poll->add(func);
    }
    delete poll;
    return 0;
}

```

## Makefile
```makefile
src=$(wildcard src/*.cpp)

server:
	g++ -std=c++11 -pthread -g \
	$(src) \
	server.cpp \
	-o server
	
client:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp client.cpp -o client

th:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest

test:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp src/ThreadPool.cpp \
	-pthread \
	test.cpp -o test

clean:
	rm server && rm client && rm test
```

---

# day12-将服务器改写为主从Reactor多线程模式

在上一天的教程，我们实现了一种最容易想到的多线程Reactor模式，即将每一个Channel的任务分配给一个线程执行。这种模式有很多缺点，逻辑上也有不合理的地方。比如当前版本线程池对象被`EventLoop`所持有，这显然是不合理的，线程池显然应该由服务器类来管理，不应该和事件驱动产生任何关系。如果强行将线程池放进`Server`类中，由于`Channel`类只有`EventLoop`对象成员，使用线程池则需要注册回调函数，十分麻烦。
> 更多比较可以参考陈硕《Linux多线程服务器编程》第三章

今天我们将采用主从Reactor多线程模式，也是大多数高性能服务器采用的模式，即陈硕《Linux多线程服务器编程》书中的one loop per thread模式。

此模式的特点为：
1. 服务器一般只有一个main Reactor，有很多个sub Reactor。
2. 服务器管理一个线程池，每一个sub Reactor由一个线程来负责`Connection`上的事件循环，事件执行也在这个线程中完成。
3. main Reactor只负责`Acceptor`建立新连接，然后将这个连接分配给一个sub Reactor。

此时，服务器有如下成员：
```cpp
class Server {
private:
    EventLoop *mainReactor;     //只负责接受连接，然后分发给一个subReactor
    Acceptor *acceptor;                     //连接接受器
    std::map<int, Connection*> connections; //TCP连接
    std::vector<EventLoop*> subReactors;    //负责处理事件循环
    ThreadPool *thpool;     //线程池
};
```
在构造服务器时：
```cpp
Server::Server(EventLoop *_loop) : mainReactor(_loop), acceptor(nullptr){ 
    acceptor = new Acceptor(mainReactor);   //Acceptor由且只由mainReactor负责
    std::function<void(Socket*)> cb = std::bind(&Server::newConnection, this, std::placeholders::_1);
    acceptor->setNewConnectionCallback(cb);

    int size = std::thread::hardware_concurrency();     //线程数量，也是subReactor数量
    thpool = new ThreadPool(size);      //新建线程池
    for(int i = 0; i < size; ++i){
        subReactors.push_back(new EventLoop());     //每一个线程是一个EventLoop
    }

    for(int i = 0; i < size; ++i){
        std::function<void()> sub_loop = std::bind(&EventLoop::loop, subReactors[i]);
        thpool->add(sub_loop);      //开启所有线程的事件循环
    }
}
```
在新连接到来时，我们需要将这个连接的socket描述符添加到一个subReactor中：
```cpp
int random = sock->getFd() % subReactors.size();    //调度策略：全随机
Connection *conn = new Connection(subReactors[random], sock);   //分配给一个subReactor
```
这里有一个很值得研究的问题：当新连接到来时应该分发给哪个subReactor，这会直接影响服务器效率和性能。这里采用了最简单的hash算法实现全随机调度，即将新连接随机分配给一个subReactor。由于socket fd是一个`int`类型的整数，只需要用fd余subReactor数，即可以实现全随机调度。

这种调度算法适用于每个socket上的任务处理时间基本相同，可以让每个线程均匀负载。但事实上，不同的业务传输的数据极有可能不一样，也可能受到网络条件等因素的影响，极有可能会造成一些subReactor线程十分繁忙，而另一些subReactor线程空空如也。此时需要使用更高级的调度算法，如根据繁忙度分配，或支持动态转移连接到另一个空闲subReactor等，读者可以尝试自己设计一种比较好的调度算法。

至此，今天的教程就结束了。在今天，一个简易服务器的所有核心模块已经开发完成，采用主从Reactor多线程模式。在这个模式中，服务器以事件驱动作为核心，服务器线程只负责mainReactor的新建连接任务，同时维护一个线程池，每一个线程也是一个事件循环，新连接建立后分发给一个subReactor开始事件监听，有事件发生则在当前线程处理。这种模式几乎是目前最先进、最好的服务器设计模式，本教程之后也会一直采用此模式。

虽然架构上已经完全开发完毕了，但现在我们还不算拥有一个完整的网络库，因为网络库的业务是写死的`echo`服务，十分单一，如果要提供其他服务，如HTTP服务、FTP服务等，需要重新开发、重新写代码，这打破了通用性原则。我们希望将服务器业务处理也进一步抽象，实现用户特例化，即在`main`函数新建`Server`的时候，可以自己设计、绑定相应的业务，在之后的教程将会实现这一功能。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day12](https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day12)

## ThreadPoolTest.cpp
```cpp
#include <iostream>
#include <string>
#include "src/ThreadPool.h"

void print(int a, double b, const char *c, std::string d){
    std::cout << a << b << c << d << std::endl;
}

void test(){
    std::cout << "hellp" << std::endl;
}

int main(int argc, char const *argv[])
{
    ThreadPool *poll = new ThreadPool();
    std::function<void()> func = std::bind(print, 1, 3.14, "hello", std::string("world"));
    poll->add(func);
    func = test;
    poll->add(func);
    delete poll;
    return 0;
}

```

## client.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/Socket.h"

using namespace std;

int main() {
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();
    
    while(true){
        sendBuffer->getline();
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("message from server: %s\n", readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
    return 0;
}

```

## server.cpp
```cpp
#include "src/EventLoop.h"
#include "src/Server.h"

int main() {
    EventLoop *loop = new EventLoop();
    Server *server = new Server(loop);
    loop->loop();
    return 0;
}

```

## test.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include <functional>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/Socket.h"
#include "src/ThreadPool.h"

using namespace std;

void oneClient(int msgs, int wait){
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    // sock->setnonblocking(); 客户端使用阻塞式连接比较好，方便简单不容易出错
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();

    sleep(wait);
    int count = 0;
    while(count < msgs){
        sendBuffer->setBuf("I'm client!");
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("count: %d, message from server: %s\n", count++, readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
}

int main(int argc, char *argv[]) {
    int threads = 100;
    int msgs = 100;
    int wait = 0;
    int o;
    const char *optstring = "t:m:w:";
    while ((o = getopt(argc, argv, optstring)) != -1) {
        switch (o) {
            case 't':
                threads = stoi(optarg);
                break;
            case 'm':
                msgs = stoi(optarg);
                break;
            case 'w':
                wait = stoi(optarg);
                break;
            case '?':
                printf("error optopt: %c\n", optopt);
                printf("error opterr: %d\n", opterr);
                break;
        }
    }

    ThreadPool *poll = new ThreadPool(threads);
    std::function<void()> func = std::bind(oneClient, msgs, wait);
    for(int i = 0; i < threads; ++i){
        poll->add(func);
    }
    delete poll;
    return 0;
}

```

## Makefile
```makefile
src=$(wildcard src/*.cpp)

server:
	g++ -std=c++11 -pthread -g \
	$(src) \
	server.cpp \
	-o server
	
client:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp client.cpp -o client

th:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest

test:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp src/ThreadPool.cpp \
	-pthread \
	test.cpp -o test

clean:
	rm server && rm client && rm test
```

---

# day13-支持业务逻辑自定义、完善Connection类

回顾之前的教程，可以看到服务器Echo业务的逻辑在`Connection`类中。如果我们需要不同的业务逻辑，如搭建一个HTTP服务器，或是一个FTP服务器，则需要改动`Connection`中的代码，这显然是不合理的。`Connection`类作为网络库的一部分，不应该和业务逻辑产生联系，业务逻辑应该由网络库用户自定义，写在`server.cpp`中。同时，作为一个通用网络库，客户端也可以使用网络库来编写相应的业务逻辑。今天我们需要完善`Connection`类，支持业务逻辑自定义。

首先来看看我们希望如何自定义业务逻辑，这是一个echo服务器的完整代码：

```cpp
int main() {
  EventLoop *loop = new EventLoop();
  Server *server = new Server(loop);
  server->OnConnect([](Connection *conn) {  // 业务逻辑
    conn->Read();
    std::cout << "Message from client " << conn->GetSocket()->GetFd() << ": " << conn->ReadBuffer() << std::endl;
    if (conn->GetState() == Connection::State::Closed) {
      conn->Close();
      return;
    }
    conn->SetSendBuffer(conn->ReadBuffer());
    conn->Write();
  });
  loop->Loop(); // 开始事件循环
  delete server;
  delete loop;
  return 0;
}
```

这里新建了一个服务器和事件循环，然后以回调函数的方式编写业务逻辑。通过`Server`类的`OnConnection`设置lambda回调函数，回调函数的参数是一个`Connection`指针，代表服务器到客户端的连接，在函数体中可以书写业务逻辑。这个函数最终会绑定到`Connection`类的`on_connect_callback_`，也就是`Channel`类处理的事件（这个版本只考虑了可读事件）。这样每次有事件发生，事件处理实际上都在执行用户在这里写的代码逻辑。

关于`Connection`类的使用，提供了两个函数，分别是`Write()`和`Read()`。`Write()`函数表示将`write_buffer_`里的内容发送到该`Connection`的socket，发送后会清空写缓冲区；而`Read()`函数表示清空`read_buffer_`，然后将TCP缓冲区内的数据读取到读缓冲区。

在业务逻辑中，`conn->Read()`表示从客户端读取数据到读缓冲区。在发送回客户端之前，客户端有可能会关闭连接，所以需要先判断`Connection`的状态是否为`Closed`。然后将写缓冲区设置为和读缓冲区一样的内容`conn->SetSendBuffer(conn->ReadBuffer())`，最后调用`conn->Write()`将写缓冲区的数据发送给客户端。

可以看到，现在`Connection`类只有从socket读写数据的逻辑，与具体业务没有任何关系，业务完全由用户自定义。

在客户端我们也希望使用网络库来写业务逻辑，首先来看看客户端的代码：

```cpp
int main() {
  Socket *sock = new Socket();
  sock->Connect("127.0.0.1", 1234);
  Connection *conn = new Connection(nullptr, sock);
  while (true) {
    conn->GetlineSendBuffer();
    conn->Write();
    if (conn->GetState() == Connection::State::Closed) {
      conn->Close();
      break;
    }
    conn->Read();
    std::cout << "Message from server: " << conn->ReadBuffer() << std::endl;
  }
  delete conn;
  return 0;
}
```

注意这里和服务器有很大的不同，之前设计的`Connection`类显然不能满足要求，所以需要完善`Connection`。

首先，这里没有服务器和事件循环，仅仅使用了一个裸的`Connection`类来表示从客户端到服务器的连接。所以此时`Read()`表示从服务器读取到客户端，而`Write()`表示从客户端写入到服务器，和之前服务器的`Connection`类方向完全相反。这样`Connection`就可以同时表示Server->Client或者Client->Server的连接，不需要新建一个类来区分，大大提高了通用性和代码复用。

其次，客户端`Connection`没有绑定事件循环，所以将第一个参数设置为`nullptr`表示不使用事件循环，这时将不会有`Channel`类创建来分配到`EventLoop`，表示使用一个裸的`Connection`。因此业务逻辑也不用设置服务器回调函数，而是直接写在客户端代码中。

另外，虽然服务器到客户端（Server->Client）的连接都使用非阻塞式socket IO（为了搭配epoll ET模式），但客户端到服务器（Client->Server）的连接却不一定，很多业务都需要使用阻塞式socket IO，比如我们当前的echo客户端。之前`Connection`类的读写逻辑都是非阻塞式socket IO，在这个版本支持了非阻塞式读写，代码如下：

```cpp
void Connection::Read() {
  ASSERT(state_ == State::Connected, "connection state is disconnected!");
  read_buffer_->Clear();
  if (sock_->IsNonBlocking()) {
    ReadNonBlocking();
  } else {
    ReadBlocking();
  }
}
void Connection::Write() {
  ASSERT(state_ == State::Connected, "connection state is disconnected!");
  if (sock_->IsNonBlocking()) {
    WriteNonBlocking();
  } else {
    WriteBlocking();
  }
  send_buffer_->Clear();
}
```

ps.如果连接是从服务器到客户端，所有的读写都应采用非阻塞式IO，阻塞式读写是提供给客户端使用的。

至此，今天的教程已经结束了。教程里只会包含极小一部分内容，大量的工作都在代码里，请务必结合源代码阅读。在今天的教程中，我们完善了`Connection`类，将`Connection`类与业务逻辑完全分离，业务逻辑完全由用户自定义。至此，我们的网络库核心代码已经完全脱离了业务，成为一个真正意义上的网络库。今天我们也将`Connection`通用化，同时支持Server->Client和Client->Server，使其可以在客户端脱离`EventLoop`单独绑定socket使用，读写操作也都支持了阻塞式和非阻塞式两种模式。

到今天，本教程已经进行了一半，我们开发了一个真正意义上的网络库，使用这个网络库，只需要不到20行代码，就可以搭建一个echo服务器、客户端（完整程序在`test`目录）。但这只是一个最简单的玩具型网络库，需要做的工作还很多，在今后的教程里，我们会对这个网络库不断完善、不断提升性能，使其可以在生产环境中使用。

完整源代码：[https://github.com/yuesong-feng/30dayMakeCppServer/tree/main/code/day13](https://github.com/wlgls/30daysCppServer/tree/main/code/day13)

## ThreadPoolTest.cpp
```cpp
#include <iostream>
#include <string>
#include "src/ThreadPool.h"

void print(int a, double b, const char *c, std::string d){
    std::cout << a << b << c << d << std::endl;
}

void test(){
    std::cout << "hellp" << std::endl;
}

int main(int argc, char const *argv[])
{
    ThreadPool *poll = new ThreadPool();
    std::function<void()> func = std::bind(print, 1, 3.14, "hello", std::string("world"));
    poll->add(func);
    func = test;
    poll->add(func);
    delete poll;
    return 0;
}

```

## server.cpp
```cpp
#include "src/Server.h"
#include <iostream>
#include "src/Buffer.h"
#include "src/Connection.h"
#include "src/EventLoop.h"
#include "src/Socket.h"

int main() {
  EventLoop *loop = new EventLoop();
  Server *server = new Server(loop);
  server->OnConnect([](Connection *conn) {
    conn->Read();
    if (conn->GetState() == Connection::State::Closed) {
      conn->Close();
      return;
    }
    std::cout << "Message from client " << conn->GetSocket()->getFd() << ": " << conn->ReadBuffer() << std::endl;
    conn->SetSendBuffer(conn->ReadBuffer());
    conn->Write();
  });

  loop->loop();
  delete server;
  delete loop;
  return 0;
}
```

## test.cpp
```cpp
#include <iostream>
#include <unistd.h>
#include <string.h>
#include <functional>
#include "src/util.h"
#include "src/Buffer.h"
#include "src/Socket.h"
#include "src/ThreadPool.h"

using namespace std;

void oneClient(int msgs, int wait){
    Socket *sock = new Socket();
    InetAddress *addr = new InetAddress("127.0.0.1", 1234);
    // sock->setnonblocking(); 客户端使用阻塞式连接比较好，方便简单不容易出错
    sock->connect(addr);

    int sockfd = sock->getFd();

    Buffer *sendBuffer = new Buffer();
    Buffer *readBuffer = new Buffer();

    sleep(wait);
    int count = 0;
    while(count < msgs){
        sendBuffer->setBuf("I'm client!");
        ssize_t write_bytes = write(sockfd, sendBuffer->c_str(), sendBuffer->size());
        if(write_bytes == -1){
            printf("socket already disconnected, can't write any more!\n");
            break;
        }
        int already_read = 0;
        char buf[1024];    //这个buf大小无所谓
        while(true){
            bzero(&buf, sizeof(buf));
            ssize_t read_bytes = read(sockfd, buf, sizeof(buf));
            if(read_bytes > 0){
                readBuffer->append(buf, read_bytes);
                already_read += read_bytes;
            } else if(read_bytes == 0){         //EOF
                printf("server disconnected!\n");
                exit(EXIT_SUCCESS);
            }
            if(already_read >= sendBuffer->size()){
                printf("count: %d, message from server: %s\n", count++, readBuffer->c_str());
                break;
            } 
        }
        readBuffer->clear();
    }
    delete addr;
    delete sock;
}

int main(int argc, char *argv[]) {
    int threads = 100;
    int msgs = 100;
    int wait = 0;
    int o;
    const char *optstring = "t:m:w:";
    while ((o = getopt(argc, argv, optstring)) != -1) {
        switch (o) {
            case 't':
                threads = stoi(optarg);
                break;
            case 'm':
                msgs = stoi(optarg);
                break;
            case 'w':
                wait = stoi(optarg);
                break;
            case '?':
                printf("error optopt: %c\n", optopt);
                printf("error opterr: %d\n", opterr);
                break;
        }
    }

    ThreadPool *poll = new ThreadPool(threads);
    std::function<void()> func = std::bind(oneClient, msgs, wait);
    for(int i = 0; i < threads; ++i){
        poll->add(func);
    }
    delete poll;
    return 0;
}

```

## Makefile
```makefile
src=$(wildcard src/*.cpp)

server:
	g++ -std=c++11 -pthread -g \
	$(src) \
	server.cpp \
	-o server
	
client:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp client.cpp -o client

th:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest

test:
	g++ src/util.cpp src/Buffer.cpp src/Socket.cpp src/InetAddress.cpp src/ThreadPool.cpp \
	-pthread \
	test.cpp -o test

clean:
	rm server && rm client && rm test
```

---

# day13-重构核心库、使用智能指针

* 在断开连接时，会发生内存泄漏。

之前的操作已经对完成了一个分离业务逻辑的简单网络库，但是整个项目越来越复杂，模块越来越多。为了弥补之前的设计、细节缺陷。应该对程序进行重构和梳理，以方便自己进一步的去处理和实现功能。

本次重构主要包含以下几个方面：

* 更换了部分函数名。减少无用的函数，使代码看起来更简洁，可读。
* 进行内存管理。在之前的操作所有的内存都是由裸指针进行处理的，在类的构造阶段分配内存，析构释放内存，为了更加方便的管理内存，对于类自己拥有的资源使用了智能指针`std::unique_ptr<>`进行管理，对于不属于自己的资源，但是借用的资源，使用裸指针进行处理。
* 避免资源的复制操作 ，尽量使用移动语义进行所有权转移，以提升程序性能。

### 关于common.h

对于大部分的类，我们都不希望实现其拷贝构造函数，移动构造函数和赋值运算符，简单的操作可以在每一个类中使用`=delete`来保证其不被编译器自动实现。但是如果每个类都这么写，显然不够清晰且冗余，因此采用了宏来实现。
```cpp
// common.h
#define DISALLOW_COPY(cname)     \
  cname(const cname &) = delete; \
  cname &operator=(const cname &) = delete;

#define DISALLOW_MOVE(cname) \
  cname(cname &&) = delete;  \
  cname &operator=(cname &&) = delete;

#define DISALLOW_COPY_AND_MOVE(cname) \
  DISALLOW_COPY(cname);               \
  DISALLOW_MOVE(cname);
```

### 关于Socket类

Socket类主要是对socket操作进行了封装，并主要应用在`Acceptor`类中和`Connection`类中，但是非常明显的可以发现，在`Connection`中，`Socket`成员变量并没有发挥太大的作用，只是单纯的获取`Socket`中的文件描述符，因此，对于`Connection`类其成员变量在一定程度上是冗余的。因此完全可以删掉`Socket`类，并将相应的操作直接封装在`Acceptor`中。

### 关于Channel类

`Channel`类是网络库的核心组建之一，他对`socket`进行了更深度的封装，保存了我们需要对`socket`监听的事件，当前`socket`已经准备好的事件并进行处理。此外，为了更新和获取在`epoller`中的状态，需要使用`EventLoop`进行管理，由于只是使用`EventLoop`，因此采用裸指针进行内存管理。

```cpp
class Channel {
    public:
        DISALLOW_COPY_AND_MOVE(Channel);
        Channel(int fd, EventLoop * loop);
        
        ~Channel();

        void HandleEvent() const; // 处理事件
        void EnableRead();  // 允许读
        void EnableWrite(); // 允许写
        void EnableET(); // 以ET形式触发
        void DisableWrite();

        int fd() const;  // 获取fd
        short listen_events() const; // 监听的事件
        short ready_events() const; // 准备好的事件

        bool IsInEpoll() const; // 判断当前channel是否在poller中
        void SetInEpoll(bool in = true); // 设置当前状态为poller中
        

        void SetReadyEvents(int ev);
        void set_read_callback(std::function<void()> const &callback);// 设置回调函数
        void set_write_callback(std::function<void()> const &callback);

    private:
        int fd_;
        EventLoop *loop_;
        
        short listen_events_;
        short ready_events_;
        bool in_epoll_{false};
        std::function<void()> read_callback_;
        std::function<void()> write_callback_;

};
```

### 针对Epoller类

主要是进行IO多路复用，保证高并发。在Epoller类主要是对epoll中channel的监听与处理。
```cpp
class Epoller
{
public:
    DISALLOW_COPY_AND_MOVE(Epoller);

    Epoller();
    ~Epoller();

    // 更新监听的channel
    void UpdateChannel(Channel *ch) const;
    // 删除监听的通道
    void DeleteChannel(Channel *ch) const;

    // 返回调用完epoll_wait的通道事件
    std::vector<Channel *> Poll(long timeout = -1) const;

    private:
        int fd_;
        struct epoll_event *events_;
};
```

### 针对EventLoop类

该类是对事件的轮询和处理。由于每一个EventLoop主要是不断地调用`epoll_wait`来获取激活的事件，并处理。这也就意味着`Epoll`是独属于`EventLoop`的成员变量，随着`EventLoop`的析构而析构，因此可以采用智能指针
```cpp
class EventLoop
{
public:
    DISALLOW_COPY_AND_MOVE(EventLoop);
    EventLoop();
    ~EventLoop();

    void Loop() const;
    void UpdateChannel(Channel *ch) const;
    void DeleteChannel(Channel *ch) const;

private:
    std::unique_ptr<Epoller> poller_;
};
```

### 针对Acceptor类

Acceptor主要用于服务器接收连接，并在接受连接之后进行相应的处理。这个类需要独属于自己的Channel，因此采用了智能指针管理。并且将socket相应的操作也直接封装在了`Accptor`中，并且为了方便自定义ip地址和port端口，不直接将ip和port绑死，而是通过传参的方式。
```cpp
// Acceptor.h
class Acceptor{
    public:
        DISALLOW_COPY_AND_MOVE(Acceptor);
        Acceptor(EventLoop *loop, const char * ip, const int port);
        ~Acceptor();

        void set_newconnection_callback(std::function<void(int)> const &callback);
        
        // 创建socket
        void Create();

        // 与ip地址绑定
        void Bind(const char *ip, const int port);
        
        // 监听Socket
        void Listen();

        // 接收连接
        void AcceptConnection();

    private:
        EventLoop *loop_;
        int listenfd_;
        std::unique_ptr<Channel> channel_;
        std::function<void(int)> new_connection_callback_;
};

// Acceptor.cpp
Acceptor::Acceptor(EventLoop *loop, const char * ip, const int port) :loop_(loop), listenfd_(-1){
    Create();
    Bind(ip, port);
    Listen();
    channel_ = std::make_unique<Channel>(listenfd_, loop);
    std::function<void()> cb = std::bind(&Acceptor::AcceptConnection, this);
    channel_->set_read_callback(cb);
    channel_->EnableRead();
}
```

### 针对TcpConnection类

对于每个TCP连接，都可以使用一个类进行管理，在这个类中，将注意力转移到对客户端socket的读写上，除此之外，他还需要绑定几个回调函数，例如当接收到信息时，或者需要关闭时进行的操作。
并且增加了一个conn_id的成员变量，主要是`fd`可能被复用，在debug时，可以更清晰的追寻问题。
```cpp
class TcpConnection
{
public:
    enum ConnectionState
    {
        Invalid = 1,
        Connected,
        Disconected
    };

    DISALLOW_COPY_AND_MOVE(TcpConnection);

    TcpConnection(EventLoop *loop, int connfd, int connid);
    ~TcpConnection();

     // 关闭时的回调函数
    void set_close_callback(std::function<void(int)> const &fn);   
    // 接受到信息的回调函数                                  
    void set_message_callback(std::function<void(TcpConnection *)> const &fn); 


    // 设定send buf
    void set_send_buf(const char *str); 
    Buffer *read_buf();
    Buffer *send_buf();

    void Read(); // 读操作
    void Write(); // 写操作
    void Send(const std::string &msg); // 输出信息
    void Send(const char *msg, int len); // 输出信息
    void Send(const char *msg);


    void HandleMessage(); // 当接收到信息时，进行回调

    // 当TcpConnection发起关闭请求时，进行回调，释放相应的socket.
    void HandleClose(); 


    ConnectionState state() const;
    EventLoop *loop() const;
    int fd() const;
    int id() const;

private:
    // 该连接绑定的Socket
    int connfd_;
    int connid_;
    // 连接状态
    ConnectionState state_;

    EventLoop *loop_;

    std::unique_ptr<Channel> channel_;
    std::unique_ptr<Buffer> read_buf_;
    std::unique_ptr<Buffer> send_buf_;

    std::function<void(int)> on_close_;
    std::function<void(TcpConnection *)> on_message_;

    void ReadNonBlocking();
    void WriteNonBlocking();
};
```

### 关于TcpServer类

`TcpServer`是对整个服务器的管理，他通过创建`acceptor`来接收连接。并管理`TcpConnection`的添加。

在这个类中，由于`TcpConnection`的生命周期模糊，暂时使用了裸指针，后续将会改造成智能指针。
```cpp
// TcpServer.h
class TcpServer
{
    public:
    DISALLOW_COPY_AND_MOVE(TcpServer);
    TcpServer(const char *ip, const int port);
    ~TcpServer();

    void Start();

    void set_connection_callback(std::function < void(TcpConnection *)> const &fn);
    void set_message_callback(std::function < void(TcpConnection *)> const &fn);

    void HandleClose(int fd);
    void HandleNewConnection(int fd);

    private:
        std::unique_ptr<EventLoop> main_reactor_;
        int next_conn_id_;
        std::unique_ptr<Acceptor> acceptor_;
        std::vector<std::unique_ptr<EventLoop>> sub_reactors_;
	    std::unordered_map<int, TcpConnection *> connectionsMap_;
        std::unique_ptr<ThreadPool> thread_pool_;
        std::function<void(TcpConnection *)> on_connect_;
        std::function<void(TcpConnection *)> on_message_;
};

// TcpServer.cpp
void TcpServer::HandleClose(int fd){
    auto it =  connectionsMap_.find(fd);
    assert(it != connectionsMap_.end());
    TcpConnection * conn = connectionsMap_[fd];
    connectionsMap_.erase(fd);
    // 如果析构会导致内存泄漏
    // delete conn;
    // 但是没有析构就不会close，服务端停留在`close_wait`状态，客户端停留在`fin_wait`状态。所以在这里暂时进行了close以先关闭连接
    // 可以尝试着两种操作所带来的问题
    ::close(fd);
    conn = nullptr;
}
```
## echo_server.cpp
```cpp
#include "tcp/Acceptor.h"
#include "tcp/EventLoop.h"
#include "tcp/TcpServer.h"
#include "tcp/Buffer.h"
#include "tcp/ThreadPool.h"
#include "tcp/TcpConnection.h"
#include <iostream>
#include <functional>


int main(int argc, char *argv[]) {
    
    TcpServer *server = new TcpServer("127.0.0.1", 1234);

    server->set_message_callback([](TcpConnection *conn)
                                 {
        std::cout << "Message from client " << conn->id() << " is " << conn->read_buf()->c_str() << std::endl;
        conn->Send(conn->read_buf()->c_str()); });

    server->Start();

    delete server;
    return 0;
}
```

## Makefile
```makefile
TCP=$(wildcard tcp/*.cpp)

server:
	g++ -std=c++14 -pthread -g \
	$(TCP) \
	echo_server.cpp \
	-o server
	
th:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest

clean:
	rm server 

```

---

# day15-重构TcpConnection、修改生命周期

* 首先，在debug过程中，对内容在此进行了精简，去掉了一些无效的代码，例如将`Socket`类去掉了，这是因为`Socket`类定义的操作一般只由`Accpetor`来调用，直接将其封装在`Acceptor`中更容易让人理解。

* 本章内容偏多，主要是为了理清程序运行的逻辑时，对代码进行了大幅度的更改。

在昨天的重构中，将每个类独属的资源使用`unique_ptr`进行了包装。但是对于`TcpConnection`这个类，其生命周期模糊，使用`unique_ptr`很容易导致内存泄漏。这是因为我们的对于`TcpConnection`是被动关闭，当我们`channel`在`handleEvent`时，发现客户端传入了关闭连接的信息后，直接对`onClose`进行了调用。因此如果使用`unqiue_ptr`时，我们在调用`onclose`时已经销毁了`tcpconnection`，而对应的`channel`也会被移除，但是此时的`HandleEvent`并没有结束，因此存在了内存泄漏。

* 针对，这个问题，总要从三个步骤进行。
  1. 使用`shared_ptr`智能指针管理`TcpConnection`。
  2. 在`HandleEvent`和销毁时，增加引用计数。
  3. 将`HandleClose`操作移交给`main_reactor_`进行。

### 使用`shared_ptr`对`TcpConnection`进行管理

为了解决这个问题，我们采用`shared_ptr`对`TcpConnection`进行了管理。这样就方便延长`TcpConnection`的生命周期。

具体的应用并不赘述，将`TcpConnection`继承自`enable_shared_from_this`即可使用`shared_ptr`管理。并在`TcpServer`中使用`shared_ptr`保存`TcpConnection`。
```c++
// TcpConnection.h
class TcpConnection : public std::enable_shared_from_this<TcpConnection>{
    //...
}

// TcpServer.h
class TcpServer{
    private:
        std::map<int, std::shared_ptr<TcpConnection>> connectionsMap_;
}
```

### 增加`TcpConnection`的引用计数

在当前状态下，在创建`TcpConnection`会将其加入到`connectionsMap_`使其引用计数变成了`1`，之后当`TcpConnection`处理`HandleEvent`受到关闭信号时，会直接调用`HandleClose`，这时会将`TcpConnection`从`connectionsMaps_`释放，引用计数变成`0`，直接销毁，但是`HandleEvent`并没有处理结束，从而导致了内存泄漏。

为了解决该问题，进行了两点处理。
1. 在`HandleEvent`时，增加了引用计数。

具体的，在`Channel`处增加一个指向`TcpConnection`的`weak_ptr`，当进行`HandleEvent`时，增加其应用计数。

```c++
// Channel.h
class Channel{
public:
    void HandleEvent() const;
    void HandleEventWithGuard() const;
    void Tie(const std::shared_ptr<void> &ptr);
private:
    std::weak_ptr<void> tie_;
}
//Channel.cpp
void Channel::HandleEvent() const{
    if(tie_){
        std::shared_ptr<void> guard() = tie_.lock();
        HandleEventWithGuard();
    }else{
        HandleEventWithGuard();
    }
}
void Channel::HandleEventWithGuard() const{
    if(ready_events_ & READ_EVENT){
        read_callback_();
    }
    if(ready_events_ & WRITE_EVENT){
        write_callback_();
    }
}
```

当我们建立`TcpConnection`时，会首先将其绑定在`Channel`的`tie_`上，由于`shared_from_this`无法在构造函数处调用，因此将部分操作进行分离，并保证在构造函数执行结束后调用该函数。随后，在令其进行监听读操作，这样就可以保证`Channel`在`HandleEvent`时，会增加`TcpConnection`的引用计数。
```c++
// TcpConnection.cpp
void TcpConnection::ConnectionEstablished(){
    state_ = ConnectionState::Connected;
    channel_->Tie(shared_from_this());
    channel_->EnableRead();
    if (on_connect_){
        on_connect_(shared_from_this());
    }
}

// TcpServer.cpp
inline void TcpServer::HandleNewConnection(int fd){
    assert(fd != -1);
    uint64_t random = fd % sub_reactors_.size();
    
    // 创建TcpConnection对象
    std::shared_ptr<TcpConnection> conn = std::make_shared<TcpConnection>(sub_reactors_[random].get(), fd, next_conn_id_);
    std::function<void(const std::shared_ptr<TcpConnection> &)> cb = std::bind(&TcpServer::HandleClose, this, std::placeholders::_1);
    conn->set_connection_callback(on_connect_);
    conn->set_close_callback(cb);
    conn->set_message_callback(on_message_);

    connectionsMap_[fd] = conn;
    // 分配id
    ++next_conn_id_;
    if(next_conn_id_ == 1000){
        next_conn_id_ = 1;
    }

    // 将connection分配给Channel的tie,增加计数 并开始监听读事件
    conn->ConnectionEstablished();
}
```

这样就保证了只有当`HandleEvent`结束后，`TcpConnection`的引用计数才会变成`0`。

2. 在销毁时，`HandleEvent`结束后，增加引用计数。

上述操作主要是在`HandleEvent`进行时，增加了`TcpConnection`的引用计数。在`HandleEvent`之后增加引用计数可以使程序更加鲁棒。

具体的，我们在`EventLoop`处，增加一个`to_do_list_`列表，并在每次`TcpConnection`的销毁时，向`to_do_list_`处增加一个`TcpConnection`销毁程序从而增加`TcpConnection`的计数，这个列表中的任务只有在`HandleEvent`之运行，这样就保证了`TcpConnection`的销毁，必然时在`HandleEvent`之后的。

```c++
void EventLoop::Loop(){
    while(true){
        for (Channel *active_ch : poller_->Poll()){
            active_ch->HandleEvent();
        }
        DoToDoList();
    }
}

void EventLoop::DoToDoList(){
    // 此时已经epoll_wait出来，可能存在阻塞在epoll_wait的可能性。
    std::vector < std::function<void()>> functors;
    {
        // 加锁 保证线程同步
        std::unique_lock<std::mutex> lock(mutex_); 
        functors.swap(to_do_list_);
    }
    for(const auto& func: functors){
        func();
    }
}
```

在`HandleClose`时，会将`TcpConnection`的`ConnectionDestructor`加入到`to_do_list_`中.
```cpp
// TcpServer.cpp

void TcpConnection::ConnectionDestructor(){
    //std::cout << CurrentThread::tid() << " TcpConnection::ConnectionDestructor" << std::endl;
    // 将该操作从析构处，移植该处，增加性能，因为在析构前，当前`TcpConnection`已经相当于关闭了。
    // 已经可以将其从loop处离开。
    loop_->DeleteChannel(channel_.get());
}

inline void TcpServer::HandleClose(const std::shared_ptr<TcpConnection> & conn){

    auto it = connectionsMap_.find(conn->fd());
    assert(it != connectionsMap_.end());
    connectionsMap_.erase(connectionsMap_.find(conn->fd()));

    EventLoop *loop = conn->loop();
    loop->QueueOneFunc(std::bind(&TcpConnection::ConnectionDestructor, conn));
}

// EventLoop.cpp
void EventLoop::QueueOneFunc(std::function<void()> cb){
    {
        // 加锁，保证线程同步
        std::unique_lock<std::mutex> lock(mutex_);
        to_do_list_.emplace_back(std::move(cb));
    }
}
```

当前的版本对`TcpConnection`的生命周期管理已经差不多是安全的了。在连接到来时，创建`TcpConnection`,并用`shared_ptr`管理，加入到`ConnectionsMap_`中，此时引用计数为1.

而当`HandleEvent`时，使用`weak_ptr.lock`增加`TcpConnection`的应用计数，引用计数为2。

当关闭时，`TcpServer`中`erase`后`TcpConnection`引用计数变为了1。之后将再次当前连接的销毁程序加入到`DoToDoList`使引用计数变为2, 而`HandleEvent`之后完之后引用计数变为了1。当`DoToDoList`执行完成之后，引用计数变成了0。便自动销毁。

### 将从`ConnectionsMaps_`释放`TcpConnection`的操作移交给`main_reactor_`

考虑这样一个问题，当同时有多个连接来连接时，而正好某个连接正好在关闭时，程序会发生什么。

当`sub_reactor_`在处理`HandleEvent`时，接收到关闭请求，此时其会调用`HandleClose`，在这个函数中，会有一个`connectionsMap_.erase()`操作。但是此时`main_reactor_`可能正在接收连接会向`connectionsMap_`中添加连接。由于`connectionsMap_`底层是红黑树，并不支持同时读写操作。因此这是线程冲突的。

因此对于此操作有两种可能，一个是加锁，另一个就是将`HandleClose`的中的`connectionsMap_.erase`操作移交给`main_reactor_`来操作。

在这里实现了第二种操作，为了实现这种操作，必须要获得当前运行线程的`id`，并判断其与对应`reactor_`的线程`id`是否相同。

我们使用定义了`CurrenntThread`来获取当前运行线程的线程id.

由于`EventLoop`的创建是在主线程中，只是将`EventLoop::Loop`分配给了不同的子线程，因此在`Loop`函数中调用`get_id()`并将其保存在`EventLoop`的成员变量中。

```c++
// EventLoop.cpp
void EventLoop::Loop(){
    // 将Loop函数分配给了不同的线程，获取执行该函数的线程
    tid_ = CurrentThread::tid();
    while (true)
    {
        for (Channel *active_ch : poller_->Poll()){
            active_ch->HandleEvent();
        }
        DoToDoList();
    }
}
```

当我们判断当前运行的线程是否是`EventLoop`对应的线程，只需要比较`tid_`即可。
```c++
bool EventLoop::IsInLoopThread(){
    return CurrentThread::tid() == tid_;
}
```

通过以上操作，我们就可以将其保证`connectionsMap_.erase`操作由`main_reactor_`线程进行操作。

具体的，我们对`HandleClose`进行一层额外的封装。当调用`HandleClose`时，会判断调用该函数的线程是否是`main_reactor_`对应的线程,如果是，就直接运行，如果不是，则加入`main_reactor_`的`to_do_list_`中，由`main_reactor_`后续进行操作。

```c++
// TcpServer.cpp
inline void TcpServer::HandleClose(const std::shared_ptr<TcpConnection> & conn){
    std::cout <<  CurrentThread::tid() << " TcpServer::HandleClose"  << std::endl;
    // 由main_reactor_来执行`HandleCloseInLoop`函数，来保证线程安全
    main_reactor_->RunOneFunc(std::bind(&TcpServer::HandleCloseInLoop, this, conn));
}

inline void TcpServer::HandleCloseInLoop(const std::shared_ptr<TcpConnection> & conn){
    std::cout << CurrentThread::tid() << " TcpServer::HandleCloseInLoop - Remove connection id: " <<  conn->id() << " and fd: " << conn->fd() << std::endl;
    auto it = connectionsMap_.find(conn->fd());
    assert(it != connectionsMap_.end());
    connectionsMap_.erase(connectionsMap_.find(conn->fd()));

    EventLoop *loop = conn->loop();
    loop->QueueOneFunc(std::bind(&TcpConnection::ConnectionDestructor, conn));
}

// EventLoop.cpp
void EventLoop::RunOneFunc(std::function<void()> cb){
    if(IsInLoopThread()){
        cb();
    }else{
        QueueOneFunc(cb);
    }
}
```

### eventfd异步唤醒机制

但是上述仍然存在一个比较严重的问题，由于`to_do_list_`只有在`HandleEvent`之后进行处理，如果当前`Epoller`监听的没有事件发生，那么就会堵塞在`epoll_wait`处，这对于服务器的性能影响是灾难性的。为此，我们希望在将任务加入`to_do_list_`时，唤醒相应的`Epoller`。

为了实现该操作，在`EventLoop`处，增加了一个`wakeup_channel_`，并对其进行监听读操作。当我们为`to_do_list_`添加任务时，如果如果不是当前线程，就随便往`wakeup_channel_`对应的`fd`写点东西，此时，读事件会监听到，就不会再阻塞在epoll_wait中了，并可以迅速执行`HandleCloseInLoop`操作，释放`TcpConnection`。

muduo中主要是通过`eventfd`来实现的。

```cpp
// EventLoop.cpp
EventLoop::EventLoop() : tid_(CurrentThread::tid()) { 
    poller_ = std::make_unique<Epoller>();
    wakeup_fd_ = ::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    wakeup_channel_ = std::make_unique<Channel>(wakeup_fd_, this);
    calling_functors_ = false;

    wakeup_channel_->set_read_callback(std::bind(&EventLoop::HandleRead, this));
    wakeup_channel_->EnableRead();
}


void EventLoop::QueueOneFunc(std::function<void()> cb){
    {
        // 加锁，保证线程同步
        std::unique_lock<std::mutex> lock(mutex_);
        to_do_list_.emplace_back(std::move(cb));
    }

    // 如果调用当前函数的并不是当前当前EventLoop对应的的线程，将其唤醒。主要用于关闭TcpConnection
    // 由于关闭连接是由对应`TcpConnection`所发起的，但是关闭连接的操作应该由main_reactor所进行(为了释放ConnectionMap的所持有的TcpConnection)
    if (!IsInLoopThread() || calling_functors_) {
        uint64_t write_one_byte = 1;  
        ssize_t write_size = ::write(wakeup_fd_, &write_one_byte, sizeof(write_one_byte));
        (void) write_size;
        assert(write_size == sizeof(write_one_byte));
    } 
}


void EventLoop::HandleRead(){
    // 用于唤醒EventLoop
    uint64_t read_one_byte = 1;
    ssize_t read_size = ::read(wakeup_fd_, &read_one_byte, sizeof(read_one_byte));
    (void) read_size;
    assert(read_size == sizeof(read_one_byte));
    return;
}

```


## echo_server.cpp
```cpp
#include "tcp/Acceptor.h"
#include "tcp/EventLoop.h"
#include "tcp/TcpServer.h"
#include "tcp/Buffer.h"
#include "tcp/ThreadPool.h"
#include "tcp/TcpConnection.h"
#include "tcp/CurrentThread.h"
#include <iostream>
#include <functional>
#include <arpa/inet.h>
#include <vector>

class EchoServer{
    public:
        EchoServer(EventLoop *loop, const char *ip, const int port);
        ~EchoServer();

        void start();
        void onConnection(const std::shared_ptr<TcpConnection> & conn);
        void onMessage(const std::shared_ptr<TcpConnection> & conn);

    private:
        TcpServer server_;
};

EchoServer::EchoServer(EventLoop *loop, const char *ip, const int port) :  server_(loop, ip, port){
    server_.set_connection_callback(std::bind(&EchoServer::onConnection, this, std::placeholders::_1));
    server_.set_message_callback(std::bind(&EchoServer::onMessage, this, std::placeholders::_1));
};
EchoServer::~EchoServer(){};

void EchoServer::start(){
    server_.Start();
}

void EchoServer::onConnection(const std::shared_ptr<TcpConnection> & conn){
    // 获取接收连接的Ip地址和port端口
    int clnt_fd = conn->fd();
    struct sockaddr_in peeraddr;
    socklen_t peer_addrlength = sizeof(peeraddr);
    getpeername(clnt_fd, (struct sockaddr *)&peeraddr, &peer_addrlength);

    std::cout << CurrentThread::tid()
              << " EchoServer::OnNewConnection : new connection "
              << "[fd#" << clnt_fd << "]"
              << " from " << inet_ntoa(peeraddr.sin_addr) << ":" << ntohs(peeraddr.sin_port)
              << std::endl;
};

void EchoServer::onMessage(const std::shared_ptr<TcpConnection> & conn){
    // std::cout << CurrentThread::tid() << " EchoServer::onMessage" << std::endl;
    if (conn->state() == TcpConnection::ConnectionState::Connected)
    {
        std::cout << CurrentThread::tid() << "Message from clent " << conn->read_buf()->c_str() << std::endl;
        conn->Send(conn->read_buf()->c_str());
        conn->HandleClose();
    }
}

int main(int argc, char *argv[]){
    int port;
    if (argc <= 1)
    {
        port = 1234;
    }else if (argc == 2){
        port = atoi(argv[1]);
    }else{
        printf("error");
        exit(0);
    }
    EventLoop *loop = new EventLoop();
    EchoServer *server = new EchoServer(loop, "127.0.0.1", port);
    server->start();
    
    // delete loop;
    // delete server;
    return 0;
}

```

## Makefile
```makefile
TCP=$(wildcard tcp/*.cpp)

server:
	g++ -std=c++14 -pthread -g \
	$(TCP) \
	echo_server.cpp \
	-o server
	
th:
	g++ -pthread src/ThreadPool.cpp ThreadPoolTest.cpp -o ThreadPoolTest

clean:
	rm server 

```

---

# day16-使用CMake工程化

最开始只想实现功能，而忽视其他，但是随着文件越来越多，项目的管理就愈加繁杂，例如`common.h`与`tcp`并没有关系，因此，想要将其分离，最终还是编写了简单的`CMakeLists.txt`进行管理

在当前的版本中，一共主要有两个文件夹，`base`文件夹存放基础的组件，`tcp`存放TCP的地层文件
```c++
include_directories(
    base
    tcp
)
```

在编译，可以根据不同的环境设置不同的编译参数：
```shell
SET(CMAKE_CXX_FLAGS "-g -Wall -Werror -std=c++14")
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
```

最后我们只需要收集对应目录下的所有源文件并编译连接即可，最后
```bash
# 查找包
find_package(Threads REQUIRED)

aux_source_directory(base SRC_LIST1)
aux_source_directory(tcp SRC_LIST2)

set (EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/test/)

# 指定生成目标
add_executable(echoserver test/echo_server.cpp ${SRC_LIST1} ${SRC_LIST2})

# 添加连接库 主要针对多线程
target_link_libraries(echoserver ${CMAKE_THREAD_LIBS_INIT})
```

配置好`CMakeLists.txt`之后，就可以尝试编译项目，首先创建`build`文件夹，防止文件和项目混在一起。
```bash
mkdir build
cd build
```

然后使用`cmake`生成`Makefile`:
```bash
cmake ..
```
然后使用make指令即可生成对应的可执行文件
```bash
make
```

生成的可知性文件被放在`build/test`中，只需要使用`./test/echoerver`即可运行服务器

这是一个非常简单的`CMakeLists.txt`，只是保证了当前项目可以运行起来，如果需要更加复杂的变化，就需要学习相关的代码，并查阅相应的资料了

---

# day17-使用EventLoopThreadPool、移交EventLoop

在之前的操作中， 我们在`main_reactor`中创建了`sub_reactor`，但是这意味着只有在`Loop`时才能够调用`CurrentThread::tid()`获取j对应的线程ID，并将其认定为自身的`sub_reactor`的所属线程ID，这并没有问题，但是条理上不够清晰。

我们期望在将创建相应的线程，之后将`sub_reactor`的任务直接分配给相应的线程，并在初始化直接绑定线程ID，这更方便理解，也更方便将不同的模块进行分离。

此外，对于我们的多线程服务器，线程池其实并不需要`task_queue`，因为每一个线程执行的任务是确定且绑定的，因此也可以使用更简单且便于理解的线程池。

为了将构造`EventLoop`也就是构造`sub_reactor`的任务交给子线程并且我们的主线程能够调用相应的`EventLoop`绑定相应的`TcpConnection`。创建了`EventLoopThread`类，这个类将由主线程进行管理。该类主要是`EventLoop`与线程之间的操作。

当我们创建线程时，子线程将首先创建一个`EventLoop`对象，之后由主线程获取该对象的地址，并执行`Loop`函数。

```c++
void EventLoopThread::ThreadFunc(){
    // 由IO线程创建EventLoop对象
    EventLoop loop;
    {
        // 加锁
        std::unique_lock<std::mutex> lock(mutex_);
        loop_ = &loop; // 获取子线程的地址
        cv_.notify_one(); // loop_被创建成功，发送通知，唤醒主线程。
    }

    loop_->Loop(); // 开始循环，直到析构
    {
        std::unique_lock<std::mutex> lock(mutex_);
        loop_ = nullptr;
    }
}
```

而我们的主线程，将创建执行该函数的子线程，并获得由子线程所创建的`EventLoop`的地址。
```c++
EventLoop *EventLoopThread::StartLoop(){
    // 绑定当前线程的所执行的函数，并创建子线程
    // 在这个线程中创建EventLoop.
    thread_ = std::thread(std::bind(&EventLoopThread::ThreadFunc, this));
    EventLoop *loop = nullptr;
    {
        std::unique_lock<std::mutex> lock(mutex_);
        while (loop_ == NULL){
            cv_.wait(lock); // 当IO线程未创建LOOP时，阻塞
        }
        // 将IO线程创建的loop_赋给主线程。
        loop = loop_;
    }
    // 返回创建好的线程。
    return loop;
}
```

构造了`EventLoopThread`之后，`EventLoopThreadPool`就非常简单了，创建相应的`EventLoopThread`对象，并执行`StartLoop`函数，保存创建的`EventLoop`的地址，并在需要时返回即可。


```c++
// EventLoopThreadPool
class EventLoopThreadPool{

    public:
        DISALLOW_COPY_AND_MOVE(EventLoopThreadPool);
        EventLoopThreadPool(EventLoop *loop);
        ~EventLoopThreadPool();

        void SetThreadNums(int thread_nums);

        void start();

        // 获取线程池中的EventLoop
        EventLoop *nextloop();

    private:
        EventLoop *main_reactor_;
        // 保存对应的线程对象
        std::vector<std::unique_ptr<EventLoopThread>> threads_;
        // 保存创建的EventLoop
        std::vector<EventLoop *> loops_;

        int thread_nums_;

        int next_;
};
EventLoopThreadPool::EventLoopThreadPool(EventLoop *loop)
    : main_reactor_(loop),
      thread_nums_(0),
      next_(0){};

EventLoopThreadPool::~EventLoopThreadPool(){}

void EventLoopThreadPool::start(){
    for (int i = 0; i < thread_nums_; ++i){
        // 创建EventLoopThread对象，并保存由子线程创建的EventLoop的地址
        std::unique_ptr<EventLoopThread> ptr = std::make_unique<EventLoopThread>();
        threads_.push_back(std::move(ptr));
        loops_.push_back(threads_.back()->StartLoop());
    }
}

EventLoop *EventLoopThreadPool::nextloop(){
    EventLoop *ret = main_reactor_;
    if (!loop_.empty()){
        ret = loops_[next_++];
        // 采用轮询法调度。
        if (next_ == static_cast<int>(loops_.size())){
            next_ = 0;
        }
    }
    return ret;
}
```

而我们只需要在`TcpServer`中创建一个`EventLoopThreadPool`对象，并对这个对象进行操作即可。并在启动服务器时，创建子线程EventLoop。
```c++
// TcpServer.cpp
TcpServer::TcpServer(EventLoop *loop, const char * ip, const int port){
    // ...
    // 创建线程池
    thread_pool_ = std::make_unique<EventLoopThreadPool>(loop);
}


void TcpServer::Start(){
    // 创建子线程和对应的EventLoop
    thread_pool_->start();
    // 主线程启动
    main_reactor_->Loop();
}
```

上述的`EventLoopThreadPool`与之前的`ThreadPool`并没有性能上的提高，但是其将对线程的操作与`TcpServer`分离，将代码进一步的模块化，使可读性大大增强。
---

# day18-HTTP有限状态转换机

为了实现`Http`服务器，首先需要对`Http`进行解析。对于`Http`请求报文。首先由四个部分组成，分别是请求行，请求头，空行和请求体组成。

其格式为
```
请求方法 URL HTTP/版本号
请求头字段
空行
body
```
例如
```
GET /HEELO HTTP/1.1\r\n
Host: 127.0.0.1:1234\r\n
Connection: Keep-alive\r\n
Content-Length: 12\r\n
\r\n
hello world;
```
可以看出，其格式是非常适合使用有限状态转换机。

为了实现这个功能，首先需要创建一个`HttpContext`解析器。这个解析器需要一个`HttpRequest`类来保存解析结果。
对于`HttpRequest`，他主要保存请求中的各种信息，如METHOD，URL等
```c++
class HttpRequest{
private:
    Method method_; // 请求方法
    Version version_; // 版本

    std::map<std::string, std::string> request_params_; // 请求参数

    std::string url_; // 请求路径

    std::string protocol_; // 协议

    std::map<std::string, std::string> headers_; // 请求头

    std::string body_; // 请求体
};
```

解析时，我们逐个字符遍历客户端发送的信息，首先设定`HttpContext`的初始状态为`START`。当我们遇到大写字母时，必然会是请求方法，因此此时，我们将此时的状态转成`METHOD`。当继续遇到大写字母时，说明`METHOD`的解析还在进行，而一旦遇到空格，说明我们的请求方法解析就结束了，我们使用`start`和`end`两个指针指向`METHOD`的起始位置和结束位置，获取相应的结果送入到`HttpRequest`中，之后更新`start`和`end`的位置，并更新当前的解析状态，进行下一个位置的解析。

```c++
class HttpContext
{
public:
    enum HttpRequestParaseState
    {
        kINVALID,         // 无效
        kINVALID_METHOD,  // 无效请求方法
        kINVALID_URL,     // 无效请求路径
        kINVALID_VERSION, // 无效的协议版本号
        kINVALID_HEADER,  // 无效请求头

        START,  // 解析开始
        METHOD, // 请求方法

        BEFORE_URL, // 请求连接前的状态，需要'/'开头
        IN_URL,     // url处理
        ...
        COMPLETE, // 完成
    };
    // 状态转换机，保存解析的状态
    bool ParaseRequest(const char *begin, int size);

private:
    std::unique_ptr<HttpRequest> request_;
    HttpRequestParaseState state_;
};

// HttpContext.cpp
bool HttpContext::ParamRequest(const char *begin, int size){
    //
    char *start = const_cast<char *>(begin);
    char *end = start;
    while(state_ != HttpRequestParaseState::kINVALID 
        && state_ != HttpRequestParaseState::COMPLETE
        && end - begin <= size){
        
        char ch = *end; // 当前字符
        switch(state_){
            case HttpRequestParaseState::START:{
                if(isupper(ch)){
                    state_ = HttpRequestParaseState::METHOD;
                }
                break;
            }
            case HttpRequestParaseState::METHOD:{
                if(isblank(ch)){
                    // 遇到空格表明，METHOD方法解析结束，当前处于即将解析URL，start进入下一个位置
                    request_->SetMethod(std::string(start, end));
                    state_ = HttpRequestParaseState::BEFORE_URL;
                    start = end + 1; // 更新下一个指标的位置
                    }
                break;
            }
            case HttpRequestParaseState::BEFORE_URL:{
                // 对请求连接前的处理，请求连接以'/'开头
                if(ch == '/'){
                    // 遇到/ 说明遇到了URL，开始解析
                    state_ = HttpRequestParaseState::IN_URL;
                }
                break;
            }
            ...
        }
        end ++;
    }
}
```

实际上这个版本并不鲁棒，而且性能并不是十分优异，但是作为一个玩具而言，并且去熟悉HTTP协议而言，还是有些价值的。

在本日额外实现了一个`test_httpcontext.cpp`文件用于测试`HttpContext`的效果。在`CMakeLists.txt`加入`http`的路径，并创建`build`文件，在`build`中运行`cmake ..`，之后`make test_context`并运行`./test/test_contxt`即可。

特别的，感谢[若_思CSDN C++使用有限状态自动机变成解析HTTP协议](https://blog.csdn.net/qq_39519014/article/details/112317112)本文主要参考了该博客进行了修改和实现


---

# day19-创建HTTP响应，实现HTTP服务器.md

与HTTP请求相似，HTTP响应也存在四个部分分别是状态行，响应头，空行和响应正文

具体的
```
HTTP/版本 状态码 状态描述符
响应头
空行
响应体
```
举例说明
```
HTTP\1.1 200 OK\r\n
Content-Encoding: gzip\r\n
Content-Type: text/html\r\n
Content-Length: 5\r\n
\r\n
hello
```

因此我们只需要根据这个格式创建我们的响应即可，因此创建`HttpResponse`,具体的其保存有响应的信息
```c++
class HttpResponse{
    public:
        HttpResponse(bool close_connection);
        ~HttpResponse();
        void SetStatusCode(HttpStatusCode status_code); // 设置回应码
        void SetStatusMessage(const std::string &status_message);
        void SetCloseConnection(bool close_connection);
        void SetContentType(const std::string &content_type); 
        void AddHeader(const std::string &key, const std::string &value); // 设置回应头
        void SetBody(const std::string &body);
        std::string message(); 
        bool IsCloseConnection();
    private:
        std::map<std::string, std::string> headers_;

        HttpStatusCode status_code_;
        std::string status_message_;
        std::string body_;
        bool close_connection_;
};
```

为了将这些信息整合，以发送至客户端，简单的创建一个`string`来保存这些信息，以备后续使用
```c++
std::string HttpResponse::message(){
    std::string message;
    message += ("HTTP/1.1 " +
                std::to_string(status_code_) + " " +
                status_message_ + "\r\n"
    );
    if(close_connection_){
        message += ("Connection: close\r\n");
    }else{
        message += ("Content-Length: " + std::to_string(body_.size()) + "\r\n");
        message += ("Connection: Keep-Alive\r\n");
    }

    for (const auto&header : headers_){
        message += (header.first + ": " + header.second + "\r\n");
    }

    message += "\r\n";
    message += body_;

    return message;
}
```
自此，我们的HTTP请求和HTTP响应都已经创建完成。为了在建立连接时，能够对HTTP请求进行解析，我们在`TcpConnection`创建一个`HttpContext`，这样，当`TcpConnection`的读缓冲区有信息时，可以将内部消息放到`HttpContext`中进行解析。为了便于实现，在此处实现了每个`TcpConnection`都有一个独有的`HttpContext`,并使用智能指针进行管理。
```c++
// TcpConnection.h
class TcpConnection : public std::enable_shared_from_this<TcpConnection>
{
public:
    HttpContext *context() const;
private:
    std::unique_ptr<HttpContext> context_;
}


//TcpConnection.cpp

TcpConnection::TcpConnection(EventLoop *loop, int connfd){
    //...
    context_ = std::make_unique<HttpContext>();
}
HttpContext * TcpConnection::context() const{
    return context_.get();
}
```

随后，我们使用类似于`EchoServer`的方法来创建`HttpServer`，具体的通过设置回调函数的方法，当我们的`TcpConnection`接收到消息时，将读缓冲区中的数据送入到`HttpContext`中解析并构建响应的HTTP响应报文，返回给客户端。

具体的，我们创建`HttpServer`类，该类包含一个`TcpServer`，在创建`HttpServer`时创建`TcpServer`，并传入响应的回调函数，从而间接为为`TcpConnection`创建回调

```c++
HttpServer::HttpServer(const char *ip, const int port)  {
    server_ = std::make_unique<TcpServer>(ip, port);
    server_->set_connection_callback(
        std::bind(&HttpServer::onConnection, this, std::placeholders::_1));

    server_->set_message_callback(
        std::bind(&HttpServer::onMessage, this, std::placeholders::_1)
    );
};
```

我们的`TcpConnection`处理可读信息时，会首先获得自身的`Context`解析器，并尝试解析`read_buf`中的信息，如果解析失败，服务器主动断开连接，否则则对请求报文进行处理并创建响应报文返回。

```c++
void HttpServer::onMessage(const TcpConnectionPtr &conn){
    HttpContext *context = conn->context();
    if (!context->ParaseRequest(conn->read_buf()->c_str(), conn->read_buf()->Size()))
    {
        conn->Send("HTTP/1.1 400 Bad Request\r\n\r\n");
        conn->OnClose();
    }

    if (context->GetCompleteRequest())
    {
        onRequest(conn, *context->request());
        context->ResetContextStatus();
    }
}

void HttpServer::onRequest(const TcpConnectionPtr &conn, const HttpRequest &request){
    std::string connection_state = request.GetHeader("Connection");
    bool close = (connection_state == "Close" ||
                  request.version() == HttpRequest::Version::kHttp10 &&
                      connection_state != "keep-alive");
    HttpResponse response(close);
    response_callback_(request, &response);

    conn->Send(response.message().c_str());
    if(response.IsCloseConnection()){
        conn->OnClose();
    }
}

```

这样，我们只需要在业务层定义`response_callback`即可。我们以get请求做做了相应的测试

```c++
const std::string html = " <font color=\"red\">This is html!</font> ";
void HttpResponseCallback(const HttpRequest &request, HttpResponse *response)
{
    if(request.method() != HttpRequest::Method::kGet){
        response->SetStatusCode(HttpResponse::HttpStatusCode::k400BadRequest);
        response->SetStatusMessage("Bad Request");
        response->SetCloseConnection(true);
    }

    {
        std::string url = request.url();
        std::cout << url << std::endl;
        if(url == "/"){
            response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
            response->SetBody(html);
            response->SetContentType("text/html");
        }else if(url == "/hello"){
            response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
            response->SetBody("hello world\n");
            response->SetContentType("text/plain");
        }else{
            response->SetStatusCode(HttpResponse::HttpStatusCode::k404NotFound);
            response->SetStatusMessage("Not Found");
            response->SetBody("Sorry Not Found\n");
            response->SetCloseConnection(true);
        }
    }
    return;
}

int main(){
    HttpServer *server = new HttpServer("127.0.0.1", 1234);
    server->SetHttpCallback(HttpResponseCallback);
    server->start();
    return 0;
}
```

通过运行`make http_server`获得响应的可执行文件，然后运行可执行文件，并在任意浏览器中键入`http://127.0.0.1:1234/hello`或`http://127.0.0.1:1234`或其他路径查看服务器的返回情况。

---

# day20-定时器的创建和使用

为了在特定时间执行特定任务，定时器在服务器上扮演着非常重要的功能。使用`TCP`长连接需要客户端定时向服务端发送心跳请求。或者在特定时间执行特定任务，比如定点秒杀等任务。

因此，在定时器中，我们需要实现的功能主要包含以下部分：
1. 获取一个时间
2. 保存一个特定时间，并在抵达该时间时执行特定的任务。
3. 由于一个项目中，不可能只存在一个定时任务，因此还需要对定时任务进行管理。

定时器功能中，最基础的就是获取相应的时间，我们封装了`TimeStamp`类，并且使用`gettimeofday`来获取当前的时间，时间精度达到了1微秒，基本满足了本项目的需求。

其定义为，在这个类中基本定义了我们所需要的函数，主要包括对当前时间的获取，已经对时间的比较。:
```c++
class TimeStamp{

    public:
        TimeStamp();
        explicit TimeStamp(int64_t micro_seconds);
        // 重载运算符用于比较
        bool operator<(const TimeStamp &rhs) const;
        bool operator==(const TimeStamp &rhs) const;
        // 获取事件的字符串表示，用于日志库
        std::string ToFormattedString() const;
        int64_t microseconds() const;
        
        // 获取当前时间
        static TimeStamp Now();
        // 获取当前时间+add_seconds后的时间
        static TimeStamp AddTime(TimeStamp timestamp, double add_seconds);
    private:
        int64_t micro_seconds_;
};

// 静态函数
inline TimeStamp TimeStamp::Now(){
    struct timeval time;
    gettimeofday(&time, NULL);
    return TimeStamp(time.tv_sec * kMicrosecond2Second + time.tv_usec);
}

inline TimeStamp TimeStamp::AddTime(TimeStamp timestamp, double add_seconds){
    int64_t add_microseconds = static_cast<int64_t>(add_seconds) * kMicrosecond2Second;   
    return TimeStamp(timestamp.microseconds() + add_microseconds);
}

```

上述只是封装了对时间的获取，而我们实现定时器，还需要保存对应的任务，因此，我们还需要定义一个`Timer`，其内部有两个关键的成员变量时间戳`TimeStamp expiration_`和对应需要执行的函数`std::function<void()> callback_`。

除此之外，我们可能会需要重复的执行某些任务，因此还定义了`double interval_`表示重复的时间间隔。

具体的定义如下：

```c++
class Timer
{
public:
    DISALLOW_COPY_AND_MOVE(Timer);
    Timer(TimeStamp timestamp, std::function<void()>const &cb, double interval);

    TimeStamp expiration() const;

    // 抵达时间，运行
    void run() const;
    
    // 如果是重复任务
    void ReStart(TimeStamp now);
    bool repeat() const;

private:
    TimeStamp expiration_; // 定时器的绝对时间
    std::function<void()> callback_; // 到达时间后进行回调
    double interval_; // 如果重复，则重复间隔
    bool repeat_;
};
```

`TimeStamp`和`Timer`只是作为定时器的最基础的组件。对于多个定时器任务。我们采用了`c++`中`set`数据结构对`Timer`进行存储，并以时间戳进行排序。以方便获取所有超过当前时间的定时任务。

而对于获得当前超时的定时任务。我们采用`timerfd`将定时计时的任务交给了系统，由系统负责，当到达时间后，`timerfd`变成了可读，此时就可以执行相应的定时器任务，这样就可以将其加入到`Epoll`中由`Epoll`监控。

```c++
TimerQueue::TimerQueue(EventLoop *loop)
    : loop_(loop)
{
    CreateTimerfd();
    channel_ = std::make_unique<Channel>(timerfd_, loop_);
    channel_->set_read_callback(std::bind(&TimerQueue::HandleRead, this));
    channel_->EnableRead();
}
```

当超时时`timerfd`会变得可读，此时调用`HandleRead`操作，获取所有可执行的定时任务，并进行执行。
```c++
void TimerQueue::HandleRead(){
    ReadTimerFd(); // 将事件读出来，防止loop陷入忙碌状态
    active_timers_.clear(); 
    
    auto end = timers_.lower_bound(Entry(TimeStamp::Now(), reinterpret_cast<Timer *>(UINTPTR_MAX)));
    active_timers_.insert(active_timers_.end(), timers_.begin(), end); // 将所有超时事件放入到激活序列中
    timers_.erase(timers_.begin(), end);

    // 执行
    for (const auto &entry : active_timers_)
    {
        entry.second->run();
    }
    ResetTimers(); // 对于部分事件，可能存在重复属性，需要将其重新加入到定时器队列中，并且需要重新设定`timerfd`超时时间
}

void TimerQueue::ResetTimers() {
    // 将带有重复属性的定时任务重新加入到set中
    for (auto& entry: active_timers_) {
        if ((entry.second)->repeat()) {
            auto timer = entry.second;
            timer->ReStart(TimeStamp::Now());
            Insert(timer);
        } else {
            delete entry.second;
        }
    } 

    if (!timers_.empty()) {
        // 重新设定`timerfd`超时时间
        ResetTimerFd(timers_.begin()->second);
    }
}
```

当我们向定时器加入一个定时任务时，我们需要判断是否将该任务加入到了队首，如果加入到了队首，那么就需要更新`timerfd`的状态，设置一个新的超时时间。

```c++
void TimerQueue::AddTimer(TimeStamp timestamp, std::function<void()> const &cb, double interval){
    Timer * timer = new Timer(timestamp, cb, interval);

    if (Insert(timer))
    {
        ResetTimerFd(timer);
    }
}

bool TimerQueue::Insert(Timer * timer){
    bool reset_instantly = false;

    // 如果时间比对首要早，就更新。
    if(timers_.empty() || timer->expiration() < timers_.begin()->first){
        reset_instantly = true;
    }
    timers_.emplace(std::move(Entry(timer->expiration(), timer)));
    return reset_instantl;
}

void TimerQueue::ResetTimerFd(Timer *timer){
    struct itimerspec new_;
    struct itimerspec old_;
    memset(&new_, '\0', sizeof(new_));
    memset(&old_, '\0', sizeof(old_));

    int64_t micro_seconds_dif = timer->expiration().microseconds() - TimeStamp::Now().microseconds();
    if (micro_seconds_dif < 100){
        micro_seconds_dif = 100;
    }

    new_.it_value.tv_sec = static_cast<time_t>(
        micro_seconds_dif / kMicrosecond2Second);
    new_.it_value.tv_nsec = static_cast<long>((
        micro_seconds_dif % kMicrosecond2Second) * 1000);
    // 获取监控的事件的时间距离当前有多久。

    int ret = ::timerfd_settime(timerfd_, 0, &new_, &old_);
}
```

至此，一个基础的定时器任务就完成了，我们在`EventLoop`保存一个成员变量, 并创建三个回调函数以方便在最外层定义相应的定时任务。
```c++
class EventLoop
{
public: 
    void RunAt(TimeStamp timestamp, std::function<void()> const & cb);
    void RunAfter(double wait_time, std::function < void()>const & cb);
    void RunEvery(double interval, std::function<void()> const & cb);
private:
    std::unique_ptr<TimerQueue> timer_queue_;
};
```


为了对定时器进行测试，在`HttpServer`定义了一些函数进行了简单的测试，更加复杂的操作还需要进一步的探索。

进入`build`，运行`./test/webserver`以观察程序的运行效果。
---

# day21-服务器主动关闭连接

在上一天实现了一个基础的定时器功能。考虑了半天，我似乎还没有学习到应用到定时器的场景。因此做了一个简单的应用，也就是服务器主动关闭连接，当某个连接连接时间过长时，则服务端将主动关闭连接。

这个功能实现起来并不复杂，首先，在服务端创建连接回调时，加入一个`RunAfter`事务，这个函数将服务端关闭连接的函数传入,当距离上一个上一次活跃时间间隔`autoclosetimeout`时，则尝试关闭连接。

```c++
void HttpServer::onConnection(const TcpConnectionPtr &conn){
    if(auto_close_conn_){
        loop_->RunAfter(AUTOCLOSETIMEOUT, std::move(std::bind(&HttpServer::ActiveCloseConn, this, std::weak_ptr<TcpConnection>(conn))));
    }
}
```

服务端关闭时，将计算当前时间距离当前连接`conn`上一次活跃的时间是否满足定义的自动断开的时长，如果是，则直接关闭，如果不是，则重新加入`RunAfter`事务，我们在主动释放连接时，并不需要去管理`connection`的生命周期，而是简单的使用它，因此采用了`weak_ptr`作为参数。
```c++
void HttpServer::ActiveCloseConn(std::weak_ptr<TcpConnection> & connection){
    TcpConnectionPtr conn = connection.lock(); // 防止conn已经被释放
    if (conn)
    {
        if(TimeStamp::AddTime(conn->timestamp(), AUTOCLOSETIMEOUT) < TimeStamp::Now()){
            conn->Shutdown();
        }else{
            loop_->RunAfter(AUTOCLOSETIMEOUT, std::move(std::bind(&HttpServer::ActiveCloseConn, this, connection)));
        }
    }
}
```
为了保存TCP连接的时长，则为`TcpConnection`增加一个`TimeStamp`成员变量保存当前连接的最后一次活跃时间，并在每次客户端与服务端进行交互时，将`TimeStamp`进行更新。
```c++
void HttpServer::onMessage(const TcpConnectionPtr &conn){
    if (conn->state() == TcpConnection::ConnectionState::Connected)
    {
        if(auto_close_conn_)
            conn->UpdateTimeStamp(TimeStamp::Now());
        // ...
    }
}
```

这只是一个简单的定时器的应用，此外还有许多应用场景，但是并不在本文中赘述。
---

# day22-初步涉及日志库，定义自己的输出流LogStream

在服务器编程中，日志是必不可少的，生产环境中应做到Log Everything All The Time。

一个日志库需要完成的功能主要有:

* 多种日志级别
* 日志输出目的地为本地文件
* 支持日志文件rooling(按天，按大小)，简化日志归档
* 日志文件命名(进程名+创建日期+创建时间+机器名+进程id+后缀log)
* 日志消息格式固定(日期+时间+线程id+日志级别+源文件名和行号+日志信息)

在之前的操作中，在代码中加入各种信息的输出就是一个简陋的输出端为终端的同步日志系统。如果当我们的服务器发送日志信息后，必须等待日志系统完成写操作才可以继续执行。尽管这个方式可以保证日志数据的完整性和准确率，但是在高并发场景下，会导致服务器的性能下降的非常严重。

而异步日志库在服务器产生日志消息时，会将相应的缓冲区存储起来，等到合适的时机，用一个后台线程统一处理日志信息。这就避免了服务器阻塞在日志系统写操作上，提升服务器的响应性能。

为了存储相应的日志信息，我们需要一个额外的`Buffer`类，这个类与网络端的`Buffer`带有一些不同，在网络端中暂时使用了`std::string`作为存储空间，尽管其非常方便，但是由于其内部是使用动态分配内存的，在频繁的字符串操作中，需要进行内存的动态分配和释放，因此其效率比较低。在日志库中，我们使用了**定长**的字符数组来存储日志信息，可以直接开辟对应的内存空间用于存储信息，在日志库中，将其定义为`FixedBuffer`。
```c++
class FixedBuffer{
    public:
        FixedBuffer();
        ~FixedBuffer();

        void append(const char *buf, int len); // 添加数据

        const char *data() const; // 数据
        int len() const; // 目前的长度

        char *current(); // 获取当前的指针
        int avail() const; // 剩余的可用空间

        void reset(); // 重置缓冲区
        const char *end() const; // 获取末端指针
            
    private:
        char data_[FixedBufferSize];
        char *cur_;
}
```
在这个类中，通过`cur_`保存当前可写内存空间的位置，并在加入新的数据时，直接从该位置写入，并更新`cur_`
```c++
FixedBuffer::FixedBuffer():cur_(data_){};

void FixedBuffer::append(const char *buf, int len){
    if(avail() > len){
        memcpy(cur_, buf, len);
        cur_ += len;
    }
}
```
在日志系统中，并非所有的数据都是字符数据，因此为了进行类型转换，并且采用类似`c++`风格的`stream <<`风格。首先需要定义自己的`LogStream`类，重载`<<`操作符，之所以不直接时用`iostream`是因为，其格式化输出麻烦，并且其操作并不是原子化的。

```c++
class LogStream{
    typedef LogStream self;
    typedef FixedBuffer Buffer;

public:
    self& operator<<(int num)
    self& operator<<(unsigned int num)
    self& operator<<(char v);
    
private:

    Buffer buffer_;
};
```

在实现时，会首先将相应的类别转换成字符形式，然后加入到`buffer`中。
```c++
LogStream &LogStream::operator<<(int num){
    formatInteger(num);
    return *this;
}
LogStream &LogStream::operator<<(const double& num){
    char buf[32];
    int len = snprintf(buf, sizeof(buf), "%g", num);
    buffer_.append(buf, len);
    return *this;
}
```

此外还有其他重载，就不一一赘述了，具体的对于一般类型，都先将其转成字符或者字符串然后加入到`buffer`中，在`muduo`中，针对整形进行了额外的优化，即使用了Matthew wilson设计的旋转除余法进行了转换。

但是`LogStream`本身是并不支持格式化的，因此需要额外的定义一个不影响其状态的`Fmt`类。将一个数值类型数据转换成一个长度不超过32位字符串对象`Fmt`，并重载了支持`Fmt`输出到`LogStream`的`<<`操作符。

在`Fmt`内部，调用了`snprintf`函数，将数据进行了格式化。

```c++
// LogStream.h
template<typename T>
Fmt::Fmt(const char* fmt, T val)
{
  static_assert(std::is_arithmetic<T>::value == true, "Must be arithmetic type");
  length_ = snprintf(buf_, sizeof(buf_), fmt, val);
  assert(static_cast<size_t>(length_) < sizeof(buf_));
}

inline LogStream & operator<<(LogStream& s, const Fmt& fmt){
    s.append(fmt.data(), fmt.length());
    return s;
}
```

一个简单的流式`LogStream`就简单的实现了，在`/test/test_logstream.cpp`对其进行了简单的测试。
进入`build`文件，并运行`make test_logstream`会生成相应的可执行文件，执行他就可以进行简单的测试了。
---

# day23-定义前端日志库，实现同步输出

在之前的工作中，定义了日志库的输出流。而一个完整的异步日志库系统还需要其前端内容和后端处理。

对于前端的内容，其主要是提供给用户访问日志库的接口，并对日志信息进行一定的格式化，提供给用户将日志信息写入缓冲区的功能。

为了实现该功能，我们创建一个`Logger`类。

为了针对不同的日志等级进行不同的操作，首先需要定义不同的日志等级，通常，日志等级包含如下几个部分:
* DEBUG 指出细粒度信息事件对调试应用程序是非常有帮助的（开发过程中使用）

* INFO 表明消息在粗粒度级别上突出强调应用程序的运行过程。

* WARN 系统能正常运行，但可能会出现潜在错误的情形。

* ERROR 指出虽然发生错误事件，但仍然不影响系统的继续运行。

* FATAL 指出每个严重的错误事件将会导致应用程序的退出。

因此首先定义这几个日志等级。
```c++
class Logger
{
public:
    enum LogLevel
    {
        DEBUG,
        INFO,
        WARN,
        ERROR,
        FATAL
    };
}
```

通常，我们希望日志系统包含时间发生的时间，日志等级，发生的事务已经所在的源码位置，例如
```shell
20230703 19:56:51.441099Z347201 INFO  HttpServer Listening on 127.0.0.1:1234 - HttpServer.cpp:31
```
而这些内容通常用户并不关心如何实现。为了方便实现该功能，创建一个`Impl`类，该类主要是对日志信息进行组装，将相应的数据放入到`Buffer`。
```c++
class Impl{
    public:
        DISALLOW_COPY_AND_MOVE(Impl);
        typedef Logger::LogLevel LogLevel;
        Impl(const SourceFile &source, int line, Logger::LogLevel level);
        void FormattedTime();// 格式化时间信息
        void Finish();// 完成格式化，并补充输出源码文件和源码位置

        LogStream &stream();
        const char *loglevel() const;// 获取LogLevel的字符串
        LogLevel level_;// 日志级别

    private:
        Logger::SourceFile sourcefile_; // 源代码名称
        int line_;// 源代码行数
        
        LogStream stream_;// 日志缓存流
};
```
在该类中定义了相应的格式化操作，并在实例化时，我们就直接将相应的信息放入到缓存中。
```c++

Logger::Impl::Impl(const Logger::SourceFile &source, int line, Logger::LogLevel level)
    : sourcefile_(source),
      line_(line),
      level_(level){

    // 格式化时间
    FormattedTime();
    // 输出线程id
    stream_ << std::this_thread::get_id();
    // 日志等级
    stream_ << Template(loglevel(), 6);
}
void Logger::Impl::FormattedTime(){
    //格式化输出时间
    TimeStamp now = TimeStamp::Now();
    time_t seconds = static_cast<time_t>(now.microseconds() / kMicrosecond2Second);
    int microseconds = static_cast<int>(now.microseconds() % kMicrosecond2Second);

    // 变更日志记录的时间，如果不在同一秒，则更新时间。
    // 方便在同一秒内输出多个日志信息
    if (t_lastsecond != seconds) {
        struct tm tm_time;
        localtime_r(&seconds, &tm_time);
        snprintf(t_time, sizeof(t_time), "%4d%02d%02d %02d:%02d:%02d.",
                tm_time.tm_year + 1900, tm_time.tm_mon + 1, tm_time.tm_mday,
                tm_time.tm_hour, tm_time.tm_min, tm_time.tm_sec);
        t_lastsecond = seconds;
    }

    Fmt us(".%06dZ", microseconds);
    stream_ << Template(t_time, 17) << Template(us.data(), 9);
}


void Logger::Impl::Finish(){
    stream_ << "-" << sourcefile_.data_ << ":" << line_ << "\n";
}

```

当前的内容知识将日志的信息进行了组装和放入缓冲区中，而对于实际的日志信息还没有进行任何处理。 我们希望用户在使用该日志库时可以通过简单的操作即可，例如
```c++
LOG_INFO << "LOG Message";
```
通过`LOG_INFO`来规定日志的等级，并输入相应的日志信息。

`MUDUO`通过定义一系列的宏来实现了这一操作，具体的当使用`LOG_*`之类的宏会创建一个临时匿名`Logger`对象，这个对象中包含一个`Impl`对象，而`Impl`对象拥有一个`LogStream`对象。`LOG_*`宏就会返回一个`LogStream`的引用。用于将内容输入到该`LogStream`中的`Buffer`中。

```c++
#define LOG_DEBUG if (loglevel() <= Logger::DEBUG) \
  Logger(__FILE__, __LINE__, Logger::DEBUG, __func__).stream()
#define LOG_INFO if (loglevel() <= Logger::INFO) \
  Logger(__FILE__, __LINE__, Logger::INFO).stream()
#define LOG_WARN Logger(__FILE__, __LINE__, Logger::WARN).stream()
#define LOG_ERROR Logger(__FILE__, __LINE__, Logger::ERROR).stream()
#define LOG_FATAL Logger(__FILE__, __LINE__, Logger::FATAL).stream()
```

在析构时，则会将相应的信息输出，如果发生了`FATAL`错误，还会更新缓存区并终止程序。为了设置日志的输出位置，`Logger`定义了两个函数指针用于指定输出位置和更新缓存区。并设置默认输出为`stdout`。
```c++
// Logger.h
typedef void (*OutputFunc)(const char *data, int len); // 定义函数指针
typedef void (*FlushFunc)();
// 默认fwrite到stdout
static void setOutput(OutputFunc);
// 默认fflush到stdout
static void setFlush(FlushFunc);

// Logger.cpp
void defaultOutput(const char* msg, int len){
    fwrite(msg, 1, len, stdout);  // 默认写出到stdout
}
void defaultFlush(){
    fflush(stdout);    // 默认flush到stdout
}
Logger::OutputFunc g_output = defaultOutput;
Logger::FlushFunc g_flush = defaultFlush;
```

一个完整的析构过程为:
```c++
Logger::~Logger()
{
    impl_.Finish(); // 补足源代码位置和行数
    const LogStream::Buffer& buf(stream().buffer());  // 获取缓冲区
    g_output(buf.data(), buf.len());  // 默认输出到stdout
 
    // 当日志级别为FATAL时，flush设备缓冲区并终止程序
    if (impl_.level_ == FATAL) {
        g_flush();
        abort();
    }
}
```

至此，一个简单的同步日志库基本实现了，其主要流程是，当用户使用一个`LOG_*`的日志宏时，会创建一个临时匿名对象`Logger`，然后`Logger`内部会有一个`Impl`对象，当该对象创建时，会将当前的时间，线程等信息加入到`Buffer`中。之后会该日志宏返回`Impl`中`LogStream`的引用，并将相应的信息输入其拥有的`Buffer`中。当调用结束`Logger`对象被析构时，会调用`g_output`将日志信息输出。并根据不同的日志等级执行不同的操作。


在`HttpServer`和`TcpServer`处增加了两个简单的日志处理，运行
---

# day24-异步日志库

在实现同步日志库时，我们设定了`Logger`的输出和刷新为`stdout`，而异步日志库主要是将`Logger`的输出交由了后端程序来处理。

对于异步日志库的实现，主要是通过准备两块缓冲区，前端负责往buffer A中写日志消息，后端负责将buffer B中的日志消息写入磁盘文件。当buffer A写满之后，后端线程中会交换buffer A和buffer B，让前端往buffer B中写入日志消息，后端将buffer A中的日志消息写到磁盘文件中，如此往复。同时，为了及时将生成的日志消息写入文件，便于管理者分析日志消息，即使buffer A未满，日志库也会每3秒执行交换写入操作。这就避免了前端每生成一条日志消息就传送给后端，而是将多条日志消息拼成一个大buffer传送给后端线程，相当于批量处理，减少了后端线程的唤醒频率，降低了服务器开销。

这明显是一个生产者消费者模式，只有当我们的后端线程创建成功之后，我们才可以不断的往`Buffer A`中写入数据，否则当`Buffer A`已满，我们无法将其写入到磁盘文件中，可能会有丢失信息的问题。为了保证他的线程安全，需要使用`Latch`机制，其机制对于线程同步机制来说很简单，主要针对一个线程等待另一个或多个线程，其内部实现就是一些线程能够等待直到计数器变为零。但是`std::latch`在`c++20`才被引入，本次并不使用该方法，而是定义一个`Latch`类来实现该机制。

在这个类中有一个`count_`变量，构造时给定一个初值，代表需要等待的线程数。每个线程完成一个任务，`count_`减1，当`count_`值减到0时，代表所有线程已经完成了所有任务，在`Latch`上等待的线程就可以继续执行了。

```c++
class Latch
{
private:
    std::mutex mux_;
    std::condition_variable cv_;
    int count_;

public:
    DISALLOW_COPY_AND_MOVE(Latch);

    explicit Latch(int count) : count_(count){}
    void wait(){
        std::unique_lock<std::mutex> lock(mux_);
        while(count_ > 0){
            cv_.wait(lock);
        }
    }

    void notify(){
        std::unique_lock<std::mutex> lock(mux_);
        --count_;
        if(count_ == 0){
            cv_.notify_all();
        }
    }
};
```

上述的操作只是定义了一个`Latch`类，当然如果使用`c++20`的话，也可以直接使用`std::latch`来进行管理。

而对于日志库的主要逻辑而言，其关键的工作在于，
1. 如何往buffer A中写入日志信息。
2. 后端如何操作并将相应的信息写入磁盘文件。

在同步日志库中，我们设定了`Logger`的输出和刷新都是`stdout`。我们只要将其变为往`Buffer A`中添加数据即可。
为了实现这个目的，定义了一个`AsyncLogging`。
```c++
class AsyncLogging{
    public:
        typedef FixedBuffer<FixedLargeBuffferSize> Buffer;

        AsyncLogging(const char *filepath = nullptr);
        ~AsyncLogging();

        void Stop();
        void Start();

        void Append(const char* data, int len);
        void Flush();
        void ThreadFunc();
    
    private:
        
        bool running_;
        const char *filepath_;

        // 线程相关
        std::mutex mutex_;
        std::condition_variable cv_;
        Latch latch_;
        std::thread thread_;

        std::unique_ptr<Buffer> current_; // 当前的缓存
        std::unique_ptr<Buffer> next_; // 预备的缓冲
        std::vector<std::unique_ptr<Buffer>> buffers_;// 已满的缓冲区
};
```

在这个类中拥有两个`Buffer`成员变量。主要是为了防止当一次性产生大量日志信息时，单个buffer无法及时的保存所有的信息，`next_`作为预备役被定义。

在添加数据时，我们会判断`current_`剩余空间是否充足，如果不充足，就可以往第一个缓冲区中添加数据，如果第二个也被使用了，就需要重新开辟内存空间，但是这种情况是极少的，因此对运行的效率的影响应该是微乎其微。

此外，还有一个`Buffer`的`vector`数组，这其实就相当于异步日志库中的`Buffer A`。
```c++
// AsyncLogging.cpp
void AsyncLogging::Append(const char *data, int len){
    std::unique_lock<std::mutex> lock(mutex_);
    if(current_->avail() >= len){
        current_->append(data, len);
    }else{
        // 如果当前缓存没有空间，就将当前缓存放入到已满列表中
        buffers_.push_back(std::move(current_));
        if (next_){ // 如果预备缓冲区未被使用，则
            current_ = std::move(next_);
        }else{
            current_.reset(new Buffer());
        }
        // 向新的缓冲区写入信息。
        current_->append(data, len);
    }
    // 唤醒后端线程
    cv_.notify_one();
}
```
在之后，我们就可以将该函数作为`Logger`的输出对象，这就保证了`Logger`产生的日志信息将存放在`Buffer A`中。例如：
```c++
// test_httpserver.cpp
std::unique_ptr<AsyncLogging> asynclog;
// 由于`Append`不是静态函数，所以需要先声明一个实例对象。
void AsyncOutputFunc(const char *data, int len)
{
    asynclog->Append(data, len);
}
int main(){
    asynclog = std::make_unique<AsyncLogging>();
    Logger::setOutput(AsyncOutputFunc);
}

```
同理,`Flush`也可以进行相同的操作。

对于后端线程的建立，其主要就是对`Buffer A`和`Buffer B`的交换，并写入日志文件中，在后端线程中，会额外创建一个存储`Buffer`的`Vector`，作为我们的`Buffer B`.

其余的操作并不关键，只是增加运行的效率，例如在线程开始时开辟两个`Buffer`空间后续直接分配给主线程的`current_`和`next_`就省去了主线程重新开辟空间的时间，在最后保留两个已满`Buffer`不释放，而是清空并分配也是为了减少重新开辟空间的次数。
```c++
void AsyncLogging::ThreadFunc(){
    // 创建成功，提醒主线程
    latch_.notify();

    std::unique_ptr<Buffer> new_current = std::make_unique<Buffer>();
    std::unique_ptr<Buffer> new_next = std::make_unique<Buffer>();


    std::unique_ptr<LogFile> logfile = std::make_unique<LogFile>();

    new_current->bzero();
    new_next->bzero();

    std::vector<std::unique_ptr<Buffer>> active_buffers;
    
    while(running_){
        std::unique_lock<std::mutex> lock(mutex_);
        if(buffers_.empty()){
            // 如果还没有已满缓冲区，则等待片刻
            cv_.wait_until(lock, std::chrono::system_clock::now() + BufferWriteTimeout * std::chrono::milliseconds(1000),
                          []{ return false; });
        }

        // 直接将当前的缓冲区看错已满缓冲区中，减少操作。
        buffers_.push_back(std::move(current_));

        // Buffer A与Buffer B交换
        active_buffers.swap(buffers_);

        current_ = std::move(new_current);

        if(!next_){
            next_ = std::move(new_next);
        }

        // 写入日志文件
        for (const auto & buffer: active_buffers){
            logfile->Write(buffer->data(), buffer->len());
        }

        if(logfile->writtenbytes() >= FileMaximumSize){
            // 如果文件已写内容超过最大空间，新建一个。
            logfile.reset(new LogFile(filepath_));
        }

        if (active_buffers.size() > 2)
        {
            // 留两个，用户后续直接分配，不需要再额外的进行开辟内存空间，增加效率。
            active_buffers.resize(2);
        }

        if(!new_current){
            new_current = std::move(active_buffers.back());
            active_buffers.pop_back();
            new_current->bzero();
        }
        if(!new_next){
            new_next = std::move(active_buffers.back());
            active_buffers.pop_back();
            new_next->bzero();
        }

        active_buffers.clear();
    }
    
}
```

为了保证首先创建了日志库的后端线程，因此在此处采用了`Latch`机制，在`AsyncLogging`处定义了一个`Latch`变量，因为一般一个服务器只有一个后端日志线程，因此初始化`count`为1, 当该线程被创建时，`count`变为0，前端线程可以继续执行。

具体的其被定义在
```c++
// AsyncLogging.cpp
void AsyncLogging::Start(){
    running_ = true;
    thread_ = std::thread(std::bind(&AsyncLogging::ThreadFunc, this));

    // 等待线程启动完成。
    latch_.wait();
}
```

上述就是一个简单的异步日志库的实现，上述代码中还提到了`LogFile`,其内部实现非常简单,只是打开文件,并定义了一个写入文件的函数,此处就不再赘述。

至此，一个完整的日志库就实现了。在本教程中，为了实现前端、后端的异步操作，同时避免前端每次生成日志消息都唤醒后端线程，提高日志处理效率，采用的是双缓冲技术，具体的思想就是：准备两块缓冲区，前端负责往buffer A中写日志消息，后端负责将buffer B中的日志消息写入磁盘文件。当buffer A写满之后，后端线程中会交换buffer A和buffer B，让前端往buffer B中写入日志消息，后端将buffer A中的日志消息写到磁盘文件中，如此往复。这就避免了前端每生成一条日志消息就传送给后端，而是将多条日志消息拼成一个大buffer传送给后端线程，相当于批量处理，减少了后端线程的唤醒频率，降低了服务器开销。

除此之外，我们还定义了`Latch`类用于处理线程同步，并将`FixedBuffer`类修改为了模板类来处理前端和后端对不同`Buffer`大小的需求。

在`test_httpserver.cpp`中添加了`异步日志库`的代码，通过之前的操作编译连接并运行它即可测试异步日志库的效果。需要注意的是，需要首先创建一个`LogFiles`文件夹用于存储日志文件，这是因为`fopen`并不会根据路径创建文件夹。
---

# day25-更有效的缓冲区

在过去的操作中，我们使用了`std::string`作为缓冲区的，虽然便于理解，但是由于频繁的操作内存，性能上还是存在一些问题。

另外一个方面就是，整个服务器仍然只有监听读时间，写的操作在读事件发生时立刻被执行了，并且只有当`tcpconnection`中的`send_buffer`中的所有数据都被输出写入之后才会进行下一步，尽管其具有可行性，但是仍然有一些性能上的影响。比如当写的数据量过多，需要多次写操作，那么每次就需要`socket`的写缓冲区清空后再进行写操作，就非常容易阻塞在此处。因此将写事件也放入`Epoll`中显得是有必要的。

那么为了保证`ET`模式写，写数据能够写完，一个解决方法就是如果如果`socket`的写缓冲区还有空间且`send_buffer`的数据还有剩余数据就一直写，当写完之后，就重新注册写事件等待下一次写入。这样就需要能够获得`Buffer`中还有多少数据。之前的操作是在发送数据时将`send_buffer`中的数据加入到一个固定长度的`char`数组中，并设定一个`data_left`来保存每次发送的数据量，来保证每次将`send_buffer`中的数据发送完成。这是可行的，但是如果可以直接在`send_buffer`上获取其剩余的数据量，无疑更加简洁。

考虑到上述内容，我们重新设计了`Buffer`类，这个类由固定长度的`vector<char>`数组进行存储，使用`vector`有一个比较好的好处，就是当我们加入的数据超过`Buffer`的可写空间时，`Buffer`可以自动增长到容纳全部数据。

在程序的内部，我们的`Buffer`的数据结构可以看做三块，即`prependable`, `readable`, `writable`。

```shell
| prependable | readable | writeable |
```

这三个块并不是固定的，而是根据读写操作动态变化的，具体的我们已经写入的数据将被存放在`readable`中，`writable`是剩余的可写空间，随着写入数据增多`readable`将增加，`writable`将降低。而`prependable`则让程序能以很低的代价在数据前面添加几个字节。最简单的例子时，当我们不知道需要增加的消息长度时，可以先进行增加数据，当增加完成后，再在`prependable`前方添加消息的长度。


`Buffer`的定义如下:
```c++
static const int kPrePendIndex = 8; // prependindex长度
static const int kInitalSize = 1024; // 初始化开辟空间长度

class Buffer{
    public:
        DISALLOW_COPY_AND_MOVE(Buffer);

        Buffer();
        ~Buffer();

        // buffer的起始位置
        char *begin();
        // const对象的begin函数，使得const对象调用begin函数时
        // 所得到的迭代器只能对数据进行读操作，而不能进行修改
        const char *begin();

        char *beginread();
        const char *beginread();

        char *beginwrite();
        const char *beginwrite();


        // 添加数据
        void Append(const char *message);
        void Append(const char *message, int len);
        void Append(const std::string &message);


        // 获得可读大小等
        int readablebytes() const;
        int writablebytes() const;
        int prependablebytes() const;

        // 取数据
        // 定长
        void Retrieve(int len);
        std::string RetrieveAsString(int len);

        // 全部
        void RetrieveAll();
        std::string RetrieveAsString();

        // 某个索引之前
        void RetrieveUtil(const char *end);
        std::string RetrieveUtilAsString(const char *end);

        // 查看数据，但是不更新`read_index_`位置
        char *Peek();
        const char *Peek() const;
        std::string PeekAsString(int len);
        std::string PeekAllAsString();

        //查看空间
        void EnsureWritableBytes(int len);

    private:
        std::vector<char> buffer_;
        int read_index_;
        int write_index_;
}
```


在添加消息时，会首先检查当前可写空间是否充足，如果充足的话，就直接写入即可，如果不充足，就需要先进行扩展空间。但是随着不断的从`Buffer`中读取数据，`read_index_`会逐渐后移，导致前方大部分空间被浪费，因此会首先检查`read_index_`前方是否有充足的可写空间，如果充足，就可以先使用这部分空间，而不用额外的开辟内存空间。

```c++
void Buffer::Append(const char* message, int len) {
    EnsureWritableBytes(len);
    std::copy(message, message + len, beginwrite());
    write_index_ += len;
}
void Buffer::EnsureWritableBytes(int len){
    if(writablebytes() >= len)
        return;
    if(writablebytes() + prependablebytes() >= kPrePendIndex + len){
        // 如果此时writable和prepenable的剩余空间超过写的长度，则先将已有数据复制到初始位置，
        // 将不断读导致的read_index_后移使前方没有利用的空间利用上。
        std::copy(beginread(), beginwrite(), begin() + kPrePendIndex);
        write_index_ = kPrePendIndex + readablebytes();
        read_index_ = kPrePendIndex;
    }else{
        buffer_.resize(write_index_ + len);
    }
}
```

从`Buffer`读取数据也非常简单，我们提供了两种读取方式，一种方式是只进行了读取，但是并不改变`read_index_`的位置，也就意味着，这可以重复读取。而另外一种方式则读出后会更改`read_index_`的位置，这意味着，调用这种函数只能读取一次消息。

特别的，我们将读取的数据保存为了字符串形式，以方便后续的处理。

```c++
void Buffer::Retrieve(int len){
    assert(readablebytes() > len);
    if(len + read_index_ < write_index_){
        // 如果读的内容不超过可读空间，则只用更新read_index_
        read_index_ += len;
    }else{
        // 否则就是正好读完，需要同时更新write_index_;
        RetrieveAll();
    }
}

std::string Buffer::RetrieveAsString(int len){
    assert(read_index_ + len <= write_index_);

    std::string ret = std::move(PeekAsString(len));
    Retrieve(len);
    return ret;
}

char *Buffer::Peek() { return beginread(); }
std::string Buffer::PeekAsString(int len){
    return std::string(beginread(), beginread() + len);
}

```

至此，一个简单的缓冲区就实现了，它采用`muduo`的方式，使用`read_index_`和`write_index_`索引将缓冲区的内容分为三块：perpendable、readable、writable。之所以使用索引，而不直接使用指针，主要是为了防止迭代器失效。此外，为了应对不同的应用需求，对`buffer`的读取提供了两种不同的方式。这个缓冲区在一定程度上已经满足了本服务器的需求。后续将把读事件进行监听。

由于本`Buffer`与之前的`Buffer`调用接口发生了变换，因此在`HttpContext`中重载了`ParaseRequest`函数来应对不同的传入参数。尽可能避免对已有函数进行改变。此外，由于还没有进行监听读事件，因此在用到`Buffer`的地方，如`TcpConnection`的`Read`和`Write`操作都需要对函数的调用进行小小的变动。




---

# day26-监听写事件

在`Channel`中提供了`EnableWrite`函数，但是在整个系统中，并没有对写操作进行监听，服务器对客户端的写入一般直接发生在读事件的过程中。并且会一次性将所有内容写入。尽管保证了数据的完整性，但是性能并不高。

因此我们希望将写事件也注册到`Epoll`中以提高服务器的性能。

由于我们的服务器，`TcpConnetion`的`socket`是`ET`模式的，在`ET`模式下，读事件很容易理解，当TCP缓冲区中从无到有，就会触发，这也意味着，在进行读操作时，必须要将TCP缓冲区中的所有数据一次接收干净，因此很难有再次接收数据的机会。

但是写事件`EPOLLOUT`的触发一般发生在刚刚添加事件或者TCP缓冲区从不可写变成可写时。所以一般不会在创建`socket`时就直接监听读事件(这会导致触发一次`EPOLLOUT`，但是可能没有数据可写，而之后就不再触发了)，而是有程序来控制，具体的来说，当我们调用`Send`函数时，我们会首先发送一次数据，如果此时TCP缓冲区满了导致后续数据没有发送才会注册一个`EPOLLOUT`事件，期待被通知进行下一次发送。


此外，`EPOLLOUT`也可以被强制触发，就是每次在`epoll_ctl`做`EPOLL_CTL_ADD`或者`EPOLL_CTL_MOD`时，如果此时是可写状态，也会被强制触发一次。

利用这两个机制，就可以重新实现服务器的`Send`函数。

在调用Send时，我们首先尝试先发一次数据测试，如果没有将所有数据发送，那么就进行监听写的操作等待后续机会继续发送。
```c++
void TcpConnection::Send(const char *msg, int len){

    int remaining = len;
    int send_size = 0;

    // 如果此时send_buf_中没有数据，则可以先尝试发送数据，
    if (send_buf_->readablebytes() == 0){
        // 强制转换类型，方便remaining操作
        send_size = static_cast<int>(write(connfd_, msg, len));

        if(send_size >= 0){
            // 说明发送了部分数据
            remaining -= send_size;
        }else if((send_size == -1) && 
                    ((errno == EAGAIN) || (errno == EWOULDBLOCK))){
            // 说明此时TCP缓冲区是慢的，没有办法写入，什么都不做
            send_size = 0;// 说明实际上没有发送数据
        }
        else{
            LOG_ERROR << "TcpConnection::Send - TcpConnection Send ERROR";
            return;
        }
    }
    
    // 将剩余的数据加入到send_buf中，等待后续发送。
    assert(remaining <= len);
    if(remaining > 0){
        send_buf_->Append(msg + send_size, remaining);
        // 到达这一步时
        // 1. 还没有监听写事件，在此时进行了监听
        // 2. 监听了写事件，并且已经触发了，此时再次监听，强制触发一次，如果强制触发失败，仍然可以等待后续TCP缓冲区可写。
        channel_->EnableWrite();
    }
}
```

由于我们使用了`Epoll`对写事件进行了监听，那么我们也没有必须一次性的将所有数据进行写完，我们只需要尽可能的将TCP缓冲区写满即可。并将剩余的数据等待下一次写事件被触发即可。

```c++
void TcpConnection::WriteNonBlocking(){

    int remaining = send_buf_->readablebytes();
    int send_size = static_cast<int>(write(connfd_, send_buf_->Peek(), remaining));
    if((send_size == -1) && 
                ((errno == EAGAIN) || (errno == EWOULDBLOCK))){
        // 说明此时TCP缓冲区是满的，没有办法写入，什么都不做 
        // 主要是防止，在Send时write后监听EPOLLOUT，但是TCP缓冲区还是满的，
        send_size = 0; // 在后续`Retrieve`处使用
    }
    else if (send_size == -1){
        LOG_ERROR << "TcpConnection::Send - TcpConnection Send ERROR";
    }

    remaining -= send_size;
    send_buf_->Retrieve(send_size);
}
```

最后，我们在`TcpConnection`的构造函数中，为`Channel`设置写回调即可。

上述修改了`Send`和`WriteNonBlocking`代码，使我们的服务器在面对需要写入大量数据时的情况下不会阻塞在写的操作上。进一步提高服务器的性能。

---

# day27-处理静态文件，实现POST请求

在最外层对网络库的应用中，主要是对`HTTP`报文的各种处理，因此熟悉`HTTP`协议是进一步学习的关键。

在之前的http服务器中，服务器对客户端的返回直接定义在了`c++`文件中，但是在实际应用中，一般都需要编写相应的前端页面，然后直接返回页面。

在`c++`中，实现这种方法并不复杂，只需要将相应的文件读取保存为字符串，之后依照正常流程进行发送即可。

我们使用`fstream`标准库来处理读取文件，其他的方法也可以达到相同的目的，此处就不再赘述。

整体的读取文件的代码十分简单。只需要打开文件并读取即可。我们在`http_server.cpp`中定义了这个文件。

```c++

std::string ReadFile(const std::string& path){
    std::ifstream is(path.c_str(), std::ifstream::in);

    // 寻找文件末端
    is.seekg(0, is.end);

    // 获取长度
    int flength = is.tellg();

    //重新定位
    is.seekg(0, is.beg);
    char * buffer = new char[flength];

    // 读取文件
    is.read(buffer, flength);
    std::string msg(buffer, flength);
    return msg;
}
```

随后，我们在设置回应时，先读取文件，然后在将作为回应体即可，需要注意的是，根据不同的数据类型，需要设定不同的`ContentType`
```c++
void HttpResponseCallback(const HttpRequest &request, HttpResponse *response)
{
    if(request.method() != HttpRequest::Method::kGet){
        response->SetStatusCode(HttpResponse::HttpStatusCode::k400BadRequest);
        response->SetStatusMessage("Bad Request");
        response->SetCloseConnection(true);
    }

    {
        std::string url = request.url();
        if(url == "/"){
            std::string body = ReadFile("../static/index.html");
            response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
            response->SetBody(body);
            response->SetContentType("text/html");
        }else if(url == "/mhw"){
            std::string body = ReadFile("../static/mhw.html");
            response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
            response->SetBody(body);
            response->SetContentType("text/html");
        }else if(url == "/cat.jpg"){
            std::string body = ReadFile("../static/cat.jpg");
            response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
            response->SetBody(body);
            response->SetContentType("image/jpeg");
        }else{
            response->SetStatusCode(HttpResponse::HttpStatusCode::k404NotFound);
            response->SetStatusMessage("Not Found");
            response->SetBody("Sorry Not Found\n");
            response->SetCloseConnection(true);
        }
    }
    return;
}
```

上述实现了简单的`get`请求，但是针对登陆注册等，使用`get`请求会将帐号密码暴露在`url`中，因此一般使用`post`请求。`post`和`get`请求的区别具体可以在网络搜索。在本教程中将简单的简述一下如何处理`post`请求。

在`index.html`中，有一个简单的登陆注册界面，通过点击登陆键将提交一个`Content-Type`为`application/x-www-form-urlencoded`的`post`请求，这种格式将提交一个类似`URL`中的`key=value&...`形式。此外还有`application/json`等此处并不再赘述，具体可以参见`HTTP`的各个头部字段。

因此，当我们接收到一个`post`请求时，依然需要首先判定它所请求的路径，针对不同的路径会进行不同的操作，由于本次只有`/login`的路径，因此只对其进行了设置，之后，开始分析请求体，对于一个登陆注册而言，其请求体是`username=username&password=password`这种形式的，因此对其解析即可。

```c++
if( request.method() == HttpRequest::Method::kPost){
    if(url == "/login"){
        // 进入登陆界面
        std::string rqbody = request.body();

        // 解析
        int usernamePos = rqbody.find("username=");
        int passwordPos = rqbody.find("password=");

        usernamePos += 9; // "username="的长度
        passwordPos += 9; // 

        // 找到中间分割符
        size_t usernameEndPos = rqbody.find('&', usernamePos);
        size_t passwordEndPos = rqbody.length();

        // Extract the username and password substrings
        std::string username = rqbody.substr(usernamePos, usernameEndPos - usernamePos);
        std::string password = rqbody.substr(passwordPos, passwordEndPos - passwordPos);

        // 简单的测试
        if (username == "wlgls"){
            response->SetBody("login ok!\n");
        }
        else{
            response->SetBody("error!\n");
        }
        response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
        response->SetStatusMessage("OK");
        response->SetContentType("text/plain");
    }
}
```

上述程序只是简单的应用，在现实中，还需要更加复杂的逻辑关系和代码，但是其整体的框架与这种形式是十分相似的，只需要进行内容的扩展即可。


---

# day28-文件服务器的简单实现，文件的展示和下载

对于一个文件服务器而言，它应该包含两个最基本的功能，即 1）文件列表的展示，2）文件的上传和下载和删除

对于文件列表的展示，一般情况下，存放的文件并不是一个固定的数量，因此在展示时，就需要动态的去获得文件列表，这个功能就需要在后端实现(我对前端不太懂，ChatGPT告诉我前端不能动态的获取文件列表)。

那么在后端需要实现的就是获取当前文件夹的文件列表，并生成对应的前端界面，然后才将所有的信息发送到客户端。

首先，我们需要实现对目录的遍历。这个操作是非常简单的，利用`opendir`和`readdir`两个函数就可以非常简单的遍历指定目录的所有文件，我们将文件名称存在`filelist`中，方便下一步处理
```c++
void FindAllFiles(const std::string& path, std::vector<std::string> &filelist){
    DIR *dir;
    struct dirent *dir_entry = NULL;
    if((dir = opendir(path.c_str())) == NULL){
        LOG_ERROR << "Opendir " << path << " failed";
        return;
    }
    
    while((dir_entry = readdir(dir))!= NULL){
        std::string filename = dir_entry->d_name;
        if (filename != "." && filename != ".."){
            filelist.push_back(filename);
        }
            
    }
}
```

当我们获得相应的的文件名称后，可以很方便的将每一个文件名称都生成一个前端模板。例如这样的一个模板，对于一个文件，它展示了文件名称，并在之后提供两个按键，点击这两个按键将发出`GET`请求。

```html
<tr> 示例
    <td>a.txt</td>
    <td>
        <a href="/download/a.txt">下载</a>
        <a href="/download/a.txt">删除</a>
    </td>
</tr>
```

如果想要将其中的`a.txt`替换成我们的文件，我们只需要进行简单的字符串处理即可。

例如，
```c++
std::string file = "";
for (auto filename : filelist)
{
    //将fileitem中的所有filename替换成
    file += "<tr><td>" + filename + "</td>" +
            "<td>" +
            "<a href=\"/download/" + filename + "\">下载</a>" +
            "<a href=\"/delete/" + filename + "\">删除</a>" +
            "</td></tr>" + "\n";
}
```

这样就可以为每一个文件都生成一个前端的展示，而将这些展示加入到相应的`html`页面也可以通过非常简单的操作实现，例如，我们在`html`文件中相应的位置嵌入`<!--filelist-->`这样的代码。这样我们就可以直接读取`html`文件，并找到相应的位置直接替换即可。

```c++
// 构建filelist.html
std::string BuildFileHtml(){
    std::vector<std::string> filelist;
    // 以/files文件夹为例
    FindAllFiles("../files", filelist);


    // 为文件生成模板
    std::string file = "";
    for (auto filename : filelist)
    {
        //将fileitem中的所有filename替换成
        file += "<tr><td>" + filename + "</td>" +
                "<td>" +
                "<a href=\"/download/" + filename + "\">下载</a>" +
                "<a href=\"/delete/" + filename + "\">删除</a>" +
                "</td></tr>" + "\n";
    }


    //生成html页面
    // 主要通过将<!--filelist-->直接进行替换实现
    std::string tmp = "<!--filelist-->";
    std::string filehtml = ReadFile("../static/fileserver.html");
    filehtml = filehtml.replace(filehtml.find(tmp), tmp.size(), file);
    return filehtml;
}
```

通过如上操作，就实现了对简单的文件展示页面。当客户端请求相应的资源时，只需要调用上述函数，并将生成的字符串作为我们的响应体即可。

在上述的前端页面中，下载和删除都是由`GET`请求实现的，并在`url`中加入了文件名称，因此对于上传和下载，只需要对应的处理即可。由于下载比较繁琐，首先先实现删除操作。

对于删除操作是十分简单的，我们只需要判断当前的请求是否是删除的请求，。并在`url`中提取出要删除的文件的名称，并对其进行删除即可。在删除之后，发送一个重定向报文，将页面重新指向文件列表即可。
```c++ 
if(url.substr(0, 7) == "/delete") {
            // 删除特定文件，由于使用get请求，并且会将相应删掉文件的名称放在url中
    RemoveFile(url.substr(8));
    // 发送重定向报文，删除后返回自身应在的位置
    response->SetStatusCode(HttpResponse::HttpStatusCode::k302K);
    response->SetStatusMessage("Moved Temporarily");
    response->SetContentType("text/html");
    response->AddHeader("Location", "/fileserver");
}
```

对于文件下载可以通过将文件内容进行读取加入到`response`的`body`中，然后传输给客户端即可。但是这种操作需要数据在内核空间和内存空间来回复制，从而会严重影响高并发的性能。面对这种场景就可以使用零拷贝技术，从而减少用户态和内核态的上下文交互。具体的零拷贝的概念我参考了[这篇博客](https://juejin.cn/post/6995519558475841550)。

在本文中，采用了`sendfile`函数来实现零拷贝，由于`sendfile`只能传输文件，那么在实际应用中，就需要将响应报文的消息体单独进行发送。并且在请求头发送结束后，对请求体进行发送。

我们首先在`TcpConnection`中定义`SendFile`操作。这个操作暂时非常简单，一直发送直到文件发送完成(因此面对大文件可能会造成阻塞)。
```c++
void TcpConnection::SendFile(int filefd, int size){
    ssize_t send_size = 0;
    ssize_t data_size = static_cast<ssize_t>(size);
    // 一次性把文件写完，虽然肯定不行。
    while(send_size < data_size){

        ssize_t bytes_write = sendfile(connfd_, filefd, (off_t *)&send_size, data_size - send_size);

        if (bytes_write == -1)
        {
            if ((errno == EAGAIN) || (errno == EWOULDBLOCK)){
                continue;
            }else{
                //continue;
                break;
            }
        }
        send_size += bytes_write;
    }
}
```

当我们接收到`download`时，将设定`response`的相关参数，其中，主要需要指定文件的描述符和相应的文件大小。为了区分正常响应和文件响应，在`response`中添加一个成员变量`body_type_`用于指示当前响应的类别。
```c++
void HttpResponseCallback(const HttpRequest &request, HttpResponse *response){
    if(url.substr(0, 9) == "/download"){
        DownloadFile(url.substr(10), response);
    }
}


void DownloadFile(const std::string &filename, HttpResponse *response){
    int filefd = ::open(("../files/" + filename).c_str(), O_RDONLY);
    if(filefd == -1){
        LOG_ERROR << "OPEN FILE ERROR";
        // 文件打开失败，重定向当前页面
        response->SetStatusCode(HttpResponse::HttpStatusCode::k302K);
        response->SetStatusMessage("Moved Temporarily");
        response->SetContentType("text/html");
        response->AddHeader("Location", "/fileserver");
    }else{
        // 获取文件信息
        struct stat fileStat;
        fstat(filefd, &fileStat);
        // 设置响应头字段
        response->SetStatusCode(HttpResponse::HttpStatusCode::k200K);
        response->SetContentLength(fileStat.st_size);
        response->SetContentType("application/octet-stream");
        
        response->SetBodyType(HttpResponse::HttpBodyType::FILE_TYPE);
        // 设置文件
        response->SetFileFd(filefd);
    }
}
```

通过上述设定就可以设定`response`的响应类型，并在服务器对响应处理时进行响应的操作，例如如果`body_type_ == FILE_TYPE`就执行发送文件的操作，在这个操作中，将先发送响应报文头部字段，随后在发送文件。
```c++
void HttpServer::onRequest(const TcpConnectionPtr &conn, const HttpRequest &request){
    if(response.bodytype() == HttpResponse::HttpBodyType::HTML_TYPE){
        conn->Send(response.message());
    }else{
        // 考虑到头部字段数据量不多，直接发送完头部字段后，直接发送文件。
        conn->Send(response.beforebody());
        //sleep(1);
        conn->SendFile(response.filefd(), response.GetContentLength());

        // 发送之后关闭文件
        int ret = ::close(response.filefd());
        if(ret == -1){
            LOG_ERROR << "Close File Error";
        }else{
            LOG_INFO << "Close File Ok";
        }
        void(ret);
    }
}

```

以上就实现了一个简单的文件展示和文件下载/删除的服务器。当请求展示页面时，将返回一个HTML界面，之后根据用户不同的操作进行不同的回调，对于删除操作非常简单，只需要收到请求时，删除对应的文件之后重定向当前页面即可。对于下载的操作可能稍微复杂一些，为了保证高性能的实现，采用了`sendfile`函数，这也导致了在发送文件时，需要先发送响应头，之后再发送响应体，为了实现这个功能，在`HttpResponse`类中增加了新的成员变量，并根据不同响应报文进行不同的操作。

这个服务器还存在许多问题，例如当处理大文件时，一次性发完所有数据时会发生严重的堵塞。另外，先发送响应头然后直接发送响应体的操作在极端情况下，如果一次没有把响应头完全发送，存在一部分数据等待后续发送，不知道之后直接调用`sendfile`是否会导致错误。因此在本教程中仅仅实现了简单的应用，对于实际场景更加复杂的内容并没有考虑到。

此外，随着代码量的增加，`http_server.cpp`的代码变得更加复杂，因此需要进行一定程度的细化和重构，但是并不在本日进行了。

---

# day29-文件的上传

在之前的工作中，实现了文件的展示和下载功能，而在文件的上传与上述两种具有很大的区别。

在文件的上传时，我们在前端简单设置了一个接口，规定上传时的方法为`POST`方法，并且设定`content-type`为`multipart/form-data`。至于为什么这么设定，可以查看`HTML`的`Content-Type`不同设置的不同之处。
```html
<form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" id="fileInput" accept=".txt,.pdf,.doc,.docx,.jpg,.png">
    <button type="submit">上传文件</button>
</form>
```

通过上述表单，当用户点击上传文件时，浏览器并不会只想服务器发送一个请求报文，而是将报文分为两个部分分别发送。
```shell
// 第一次信息
POST /upload HTTP/1.1
Host: 127.0.0.1:1252
Connection: keep-alive
Content-Length: 180
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryVarr6kdO6hEAmEvh



// 第二次信息
------WebKitFormBoundaryVarr6kdO6hEAmEvh
Content-Disposition: form-data; name="file"; filename="d.txt"
Content-Type: text/plain

d
------WebKitFormBoundaryVarr6kdO6hEAmEvh--
```

可以看到，在第一次发送时，会首先将请求报文的请求头字段发送过来，之后会再发送文件信息，主要包括文件名称和文件内容。这样之前接收请求的代码逻辑就不够完善了。之前的代码在接收到请求时，会直接对其进行解析，如果解析成功就对请求进行处理。
```c++
HttpContext *context = conn->context();
if (!context->ParaseRequest(conn->read_buf()->RetrieveAllAsString()))
{

    LOG_INFO << "HttpServer::onMessage : Receive non HTTP message";
    conn->Send("HTTP/1.1 400 Bad Request\r\n\r\n");
    conn->HandleClose();
}

if (context->GetCompleteRequest())
{

    onRequest(conn, *context->request());
    context->ResetContextStatus();
}
```

之前对于一个HTTP请求使用了上述逻辑，但是上述代码在面对上传文件时会存在严重问题，当上传文件时，对于第一个接收到的报文会认定为HTTP请求，但是遇到第二个时，就会存在问题。导致连接关闭。

对于此，可以通过两种方法，第一个是可以在收到第一个连接时，设置标志符，让服务器认定第二个虽然不是请求报文，但是仍然有用。第二个则是对context解析器进行一定程度的修改，在解析时如果遇到`content-length`但是又没有收到这么长的消息体时，就暂时保持在当前解析状态，等待后续接收数据。从而将一个报文组合在一起。

在此处使用了第二种方法。

在我们进行解析时，当进行到`body`时，只有判定接收到的数据与`content-length`相等，才会认定为解析成功。
```c++
case HttpRequestParaseState::BODY:{      
    int bodylength = size - (end - begin);
    request_->SetBody(std::string(start, start + bodylength));

    if (bodylength >= atoi(request_->GetHeader("Content-Length").c_str()))
    {
        state_ = HttpRequestParaseState::COMPLETE;
    }
    break;
}
```

而且无论是达到了`CONPLETE`还是`BODY`都会认定成功。`return state_ == HttpRequestParaseState::COMPLETE || state_ == HttpRequestParaseState::BODY;`，通过这样的操作，在第一次解析时，我们的`context`的状态保持在`HttpRequestParaseState::BODY`,由于还没有完成，因此也不会对该请求作出响应，当再接收数据时，直接从`BODY`开始解析，如果与之前保存的`Content-Length`一致，说明收到了一个完整的报文，解析完成。此时，才会对请求作出响应。

在响应该请求时，会判断`Content-Type`中是否包含`multipart/form-data`,如果包含，则很大概率代表该请求是一个文件上传请求，此时就可以通过是请求体分析，获取内部存储的文件名和文件信息等相关要素，并创建相应的文件写入数据即可。

```c++
if (request.GetHeader("Content-Type").find("multipart/form-data") != std::string::npos){
    // 对文件进行处理
    //
    // 先找到文件名，一般第一个filename位置应该就是文件名的所在地。
    // 从content-type中找到边界
    size_t boundary_index = request.GetHeader("Content-Type").find("boundary");
    std::string boundary = request.GetHeader("Content-Type").substr(boundary_index + std::string("boundary=").size());

    std::string filemessage = request.body();
    size_t begin_index = filemessage.find("filename");
    if(begin_index == std::string::npos ){
        LOG_ERROR << "cant find filename";
        return;
    }
    begin_index += std::string("filename=\"").size();
    size_t end_index = filemessage.find("\"\r\n", begin_index); // 能用

    std::string filename = filemessage.substr(begin_index, end_index - begin_index);

    // 对文件信息的处理
    begin_index = filemessage.find("\r\n\r\n") + 4; //遇到空行，说明进入了文件体
    end_index = filemessage.find(std::string("--") + boundary + "--"); // 对文件内容边界的搜寻

    std::string filedata = filemessage.substr(begin_index, end_index - begin_index);
    // 写入文件
    std::ofstream ofs("../files/" + filename, std::ios::out | std::ios::app | std::ios::binary);
    ofs.write(filedata.data(), filedata.size());
    ofs.close();
}
```

此外，后续的重定向报文则与删除类似，并不在此处赘述，可以参见代码`http_server.cpp`的代码。

上述就简单的实现了一个文件的上传处理，在实现功能时，对`HttpContext`做了小小的修订，并在处理请求时，进行了额外的判断，用于处理文件上传。

对于文件的上传和下载，通过这两个教程，可以看出大部分都是基于原有的网络库建立的，对于网络库的修改几乎没有，主要是对接收到的信息进行处理和应用。小部分对网络库的修改也只是使原有的代码更加鲁棒。当然随着需求的不断增加，定制网络库是不可避免的，比如我觉得对于文件的上传和下载，如果重新创建一个服务器`Socket`用于专门的处理文件内容的话应该会更好，这在一定程度会减少大文件上传下载对`TcpConnection`的阻塞，不像现在，必须要傻乎乎的等待文件上传和下载结束才能去浏览其他页面。

但是该教程本质上也只是一个入门级的，了解c++11特性和`Socket`基本用法和`muduo`设计理念的一个教程，因此并不进一步的去设计相应的代码了。有兴趣的话，则可以进一步的去优化和设计相应的代码逻辑。




---

# day30-WebBench的测试

关于WebBench的话，网络有许多教程，[官网](http://home.tiscali.cz/~cz210552/webbench.html)

测试时，运行当前服务器，并使用webbench命令即可。

```shell
➜  ~ webbench -c 10000 -t 5 http://127.0.0.1:1236/
Webbench - Simple Web Benchmark 1.5
Copyright (c) Radim Kolar 1997-2004, GPL Open Source Software.

Benchmarking: GET http://127.0.0.1:1236/
10000 clients, running 5 sec.

Speed=3010200 pages/min, 57294136 bytes/sec.
Requests: 250850 susceed, 0 failed.
```

大概就这样，更改客户端数量和时间和连接来测试不同的情况即可。
---

