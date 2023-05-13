#### 一、说明

乐橙的摄像头接入Home Assistant中只能通过ONVIF集成插件获取视频流，不能控制云台的运动。控制云台的唯一办法就是使用官方的API，github上有一个集成插件[IMOU_LIFE](https://github.com/user2684/imou_life)，但是这个插件只能在乐橙的海外服务器用，国内的服务器没找到插件，因此这里简单写一个控制摄像头云台的工具，用于在Home Assistant中直接控制。



#### 二、使用方法

##### 2.1 准备工作

1. 在[乐橙开放平台](https://oauth.imou.com/login?client=open)注册账号
2. 登录后开发平台的[控制台](https://open.imou.com/consoleNew/resourceManage/myResource)
3. 在**应用信息**中新建应用，获取**AppId**和**AppSecret**
4. 在**设备接入服务**中添加设备，获取设备id
5. 完成后将**AppId**和**AppSecret**填入配置文件`imou_config.json`中

##### 2.2 命令

```bash
python ./imou_ptz.py [deviceId] up
# 下
python ./imou_ptz.py [deviceId] down
# 左
python ./imou_ptz.py [deviceId] left
# 右
python ./imou_ptz.py [deviceId] right
# 缩小
python ./imou_ptz.py [deviceId] zoom_in
# 放大
python ./imou_ptz.py [deviceId] zoom_out
# 镜头遮蔽
python ./imou_ptz.py [deviceId] block
# 定位到指定位置
python ./imou_ptz.py [deviceId] location
```



#### 三、在Home Assistant中安装

##### 3.1 说明

我使用的是官方提供的虚拟机镜像，homeassistant的`homeassistant`、`supervisor`、`observer`等核心组件都是作为docker容器运行在底层系统上的，其他的addon也是作为docker容器运行在底层系统上，在addon中安装的ssh插件也是单独的docker容器，该容器和homeassistant的容器共享了`/config`目录。脚本作为`shell_command`运行是在homeassistant容器中，所以ssh连接后，将脚本放到`/config`目录中即可被homeassistant容器获取。同时也要确定homeassistant是否安装了`requests`的python模块，如果未安装，我使用的是pve虚拟机，从web的终端页面进入即是底层容器，可以使用docker命令在homeassistant容器中使用pip安装模块。

##### 3.2 安装

1. 在`/config`目录中新建`imou-ptz`目录，将`imou_ptz.py`和`imou_config.json`放入目录

2. 在`/config`目录中新建`shell_command.yaml`文件，并将下面一行代码添加到`configuration.yaml`文件中

   ```
   shell_command: !include shell_command.yaml
   ```

3. 在`shell_command.yaml`文件中添加命令，注意将`[deviceId]`替换为实际的设备id，修改完成后重启homeassistant

   ```yaml
     camera_up: python /config/imou-ptz/imou_ptz.py [deviceId] up
     camera_down: python /config/imou-ptz/imou_ptz.py [deviceId] down
     camera_left: python /config/imou-ptz/imou_ptz.py [deviceId] left
     camera_right: python /config/imou-ptz/imou_ptz.py [deviceId] right
     camera_zoom_in: python /config/imou-ptz/imou_ptz.py [deviceId] zoom_in
     camera_zoom_out: python /config/imou-ptz/imou_ptz.py [deviceId] zoom_out
     camera_block: python /config/imou-ptz/imou_ptz.py [deviceId] block
     camera_location: python /config/imou-ptz/imou_ptz.py [deviceId] location
   ```

4. 然后就可以在服务中调用了

   ```bash
   automation:
     - alias: "run_set_ac"
       trigger:
         platform: state
         entity_id: input_number.ac_temperature
       action:
         service: shell_command.camera_up  
   ```

##### 3.3 在frigate-card中集成

可以参考如下代码：

```yaml
 		- type: custom:frigate-card-conditional
            conditions:
              media_loaded: true
              view:
                - live
                - image
              camera:
                - '1'
              fullscreen: false
            elements:
              - type: custom:frigate-card-ptz
                orientation: horizontal
                style:
                  transform: none
                  right: 5%
                  top: 5%
                action_left:
                  tap_action:
                    action: call-service
                    service: shell_command.camera_left
                action_right:
                  tap_action:
                    action: call-service
                    service: shell_command.camera_right
                action_down:
                  tap_action:
                    action: call-service
                    service: shell_command.camera_down
                action_up:
                  tap_action:
                    action: call-service
                    service: shell_command.camera_up
```

