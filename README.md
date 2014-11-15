##simple id_rsa.pub batch mamage and web api

####原理很简单，就是提供一个master端来远程批量管理所有用户的key及其他集群上的key，支持web api。
用到的模块
* bottle
* gevent
* sh

#### CLI
```
In [1]: import commands

In [2]: commands.get('root','106.186.21.211','22','raw')
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0NLlSuuv6lKGT/ruhimOOuNx6zyrB7fJxMLdxlaWoYvFSUx8RLfuQRjd6dTBiHJkr28Dk17X/i+NW2BH8SaYETtclW7OAJ3WQ79sTeS6BAWtKBWEscNduTsfzhByXXPAFcjY068xt0z8xs81+cDxeF/wjz/RJEAMObq6k8xy7N+dSaPwUWHOqHK5xZnTgGfyz3DHghwBzECv8a7OlNvAlAjydc7Z9xNEnbQzS9uFwv6il10Ci9CQYjyhdw0cBCLwhoYzUsX1iyy7ykB6GbYRgvo07cGa+Kv900dcIPvjoa6NFv/XPOimzJ3DGImcdzW5Ii9Qp+JJiJaKbWs3MFM+P xiaorui@devops.local

In [3]: commands.post('root','106.186.21.211','22',['/opt/lisan.pub','/opt/zhilin.pub'])

In [4]: commands.delete('root','106.186.21.211','22',['/opt/lisan.pub',0])
```
#### web api
```
curl -XGET http://127.0.0.1:8080/get?user=root&host=106.186.21.212&port=22

curl -XPOST -H "Content-Type: application/json" -d '{"user":"root","host":"106.186.21.211","port":"22","keylist":"['/ops/lisan.pub']"}'  http://127.0.0.1:8080/add

curl -XDELETE -H "Content-Type: application/json" -d '{"user":"root","host":"106.186.21.211","port":"22","keyid":"['/ops/lisan.pub']"}'  http://127.0.0.1:8080/delete
```


TODO:
* api写的有些简陋,代码不优美，安全方面也没有做
* 加入leveldb数据库
* 加入页面


