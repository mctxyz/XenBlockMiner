# 带UI界面的 XenBLOCKs 挖矿脚本

基于 Python 提供一个用户友好的界面，简化了设置和运行 XenMiner 的过程，兼容 Linux、macOS 和 Windows 操作系统。
修改自 XEN.pub 的 XenMiner Wrapper。

## 功能

1. **用户友好的界面**: 不用执行复杂的脚本. 直接在用户界面设置你的以太坊钱包地址和参数。
2. **脚本自动更新**: 每次运行时自动从 GitHub 获取 Jack 的最新 xenminer 脚本，确保始终使用最新和优化的版本。
3. **以太坊地址替换**: 自动用你的钱包地址替换 Jack 的默认地址，挖矿奖励直接进入您的账户。
4. **一键执行**: 仅需点击一次即可运行矿工脚本（根据您的计算机性能可多次运行）。
5. **并行执行**: 根据电脑物理CPU核心数，自动执行多个线程，最大化电脑挖矿性能。
6. **跨平台**: 使用 Python 编写, 兼容 Windows, Linux 和 macOS。
7. **区块计数器支持**:统计所有线程铸造的总块数。


## 最后更新

* ✅ 实时难度更新
* ✅ 跟踪所有线程的总哈希功率
* ✅ 出块总数统计
* ✅ 上次出块时间
* ✅ 挖矿时间显示
* ✅ 显示当前挖矿速率 (Est. Blocks/day)


## 如何开始

1. 确认你电脑安装了 Python 3.x 和 pip3 还有 python-tk
2. git clone 或者下载项目源文件
3. 进入目录, 执行 `pip install -U -r requirements.txt` 安装依赖包
4. 执行: `python3 XenMinerWrapper.py`
 
5. 输入你的钱包地址, 确认 Python 的安装路径
6. 点击 "Run" 按钮开始挖矿
7. 如果出块了可以去 https://hashhead.io/ 输入钱包地址查询
   

## Demo

演示视频:

https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/e4c9240f-fe0d-450b-aaa4-749b9c52f6e3


## 运行截图:

Windows | Ubuntu |  Mac

[<img src="https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/7ea6253e-758e-43cc-b825-90c4efee0999" width="200" height="150" alt="Windows">](https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/7ea6253e-758e-43cc-b825-90c4efee0999)
[<img src="https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/39feb6ba-ce7a-4ec8-96e0-b379fd628763" width="200" height="150" alt="Ubuntu">](https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/39feb6ba-ce7a-4ec8-96e0-b379fd628763)
[<img src="https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/2554b79f-20d1-42a5-ae70-521fb8fcd8f0" width="200" height="150" alt="Ubuntu">](https://github.com/JozefJarosciak/XenMinerWrapper/assets/3492464/2554b79f-20d1-42a5-ae70-521fb8fcd8f0)

## 其它

有问题可以在推特上找到我: [https://twitter.com/easymct](https://twitter.com/easymct)

感谢: https://Xen.pub

## License

This project is open-source. Please refer to the `LICENSE` file for more details.
