# 🦘 袋鼠沙漠大冒险 (Kangaroo Desert Adventure)

## 游戏简介
一款 2D 平台跳跃卷轴游戏，扮演一只澳洲袋鼠在沙漠中冒险！

## 游戏特色
- 🦘 主角：澳洲袋鼠，可以跳跃、移动
- 🌵 障碍：仙人掌、尖刺、蝎子、蛇、沙洞
- 🍇 道具：沙漠水果、仙人掌果（加血）
- 🏜️ 场景：三关沙漠主题关卡
- ❤️ 血条系统：碰到障碍减血，吃水果加血
- 🏁 胜利条件：到达每关终点

## 技术栈
- Python 3.8+
- Pygame 2.x
- PyInstaller (打包用)

## 运行方式

### 开发模式
```bash
pip install pygame
python kangaroo_game.py
```

### 打包后
双击 `KangarooAdventure.exe` 即可运行

## 关卡设计

### 第一关：沙漠入门
- 教学关卡，熟悉操作
- 少量仙人掌障碍
- 几个水果补给
- 终点：沙漠绿洲

### 第二关：危险沙丘
- 更多尖刺和洞穴
- 出现蝎子敌人
- 需要精准跳跃
- 终点：岩石峡谷

### 第三关：终极挑战
- 密集障碍
- 蛇和蝎子巡逻
- 限时挑战
- 终点：澳洲内陆小镇

## 控制方式
- ← → 或 A/D：移动
- 空格 或 W：跳跃
- R：重新开始当前关卡
- ESC：退出游戏

## 打包说明
```bash
pip install pyinstaller
pyinstaller kangaroo_game.spec
```

生成文件在 `dist/KangarooAdventure.exe`
