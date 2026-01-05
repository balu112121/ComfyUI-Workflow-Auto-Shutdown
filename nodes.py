import os
import time
import threading
import subprocess
import platform
from datetime import datetime
import folder_paths

class WorkflowAutoShutdown:
    """
    工作流自动关机插件小助手
    在工作流完成后自动保存结果并关机
    """
    
    def __init__(self):
        self.shutdown_scheduled = False
        self.shutdown_timer = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "启用自动关机": ("BOOLEAN", {"default": True}),
                "关机延迟时间": ("INT", {
                    "default": 60, 
                    "min": 10, 
                    "max": 600, 
                    "step": 5,
                    "display": "slider"
                }),
                "保存输出文件": ("BOOLEAN", {"default": True}),
                "输出目录": ("STRING", {
                    "default": "auto_shutdown_outputs",
                    "multiline": False
                }),
                "保存图像": ("BOOLEAN", {"default": True}),
                "保存视频": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "图像输入": ("IMAGE",),
                "视频输入": ("VHS_VIDEO",),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "VHS_VIDEO")
    RETURN_NAMES = ("图像输出", "视频输出")
    FUNCTION = "处理并关机"
    CATEGORY = "⚡ 自动关机小助手"
    OUTPUT_NODE = True
    
    def 处理并关机(self, 启用自动关机, 关机延迟时间, 保存输出文件, 输出目录, 保存图像, 保存视频, 图像输入=None, 视频输入=None):
        """
        处理工作流并计划关机
        """
        try:
            # 保存输出文件
            if 保存输出文件:
                self.保存输出文件(图像输入, 视频输入, 输出目录, 保存图像, 保存视频)
            
            # 计划关机
            if 启用自动关机 and not self.shutdown_scheduled:
                self.计划关机(关机延迟时间)
            
            return (图像输入, 视频输入)
            
        except Exception as e:
            print(f"🤖 自动关机插件错误: {e}")
            return (图像输入, 视频输入)
    
    def 保存输出文件(self, 图像输入, 视频输入, 输出目录, 保存图像, 保存视频):
        """
        保存图像和视频文件
        """
        try:
            # 创建输出目录
            完整输出路径 = os.path.join(folder_paths.get_output_directory(), 输出目录)
            os.makedirs(完整输出路径, exist_ok=True)
            
            # 获取当前时间戳
            时间戳 = datetime.now().strftime("%Y年%m月%d日_%H时%M分%S秒")
            
            # 保存图像
            if 保存图像 and 图像输入 is not None:
                self.保存图像文件(图像输入, 完整输出路径, 时间戳)
            
            # 保存视频
            if 保存视频 and 视频输入 is not None:
                self.保存视频文件(视频输入, 完整输出路径, 时间戳)
                
            print(f"✅ 文件已保存到: {完整输出路径}")
                    
        except Exception as e:
            print(f"❌ 保存文件时出错: {e}")
    
    def 保存图像文件(self, 图像输入, 输出路径, 时间戳):
        """保存图像文件"""
        import torch
        from PIL import Image
        import numpy as np
        
        # 将tensor转换为PIL图像并保存
        for i, 图像张量 in enumerate(图像输入):
            # 将tensor转换为numpy数组
            图像数组 = 图像张量.cpu().numpy()
            
            # 确保值在0-1范围内
            if 图像数组.max() > 1.0:
                图像数组 = 图像数组 / 255.0
            
            # 转换为0-255范围的整数
            图像数组 = (图像数组 * 255).astype(np.uint8)
            
            # 创建PIL图像
            if len(图像数组.shape) == 3:  # 单张图像
                pil图像 = Image.fromarray(图像数组.squeeze())
                文件名 = f"图像_{时间戳}_{i+1}.png"
                文件路径 = os.path.join(输出路径, 文件名)
                pil图像.save(文件路径)
                print(f"📸 已保存图像: {文件名}")
    
    def 保存视频文件(self, 视频输入, 输出路径, 时间戳):
        """保存视频文件"""
        # 这里假设videos是文件路径列表或单个文件路径
        if isinstance(视频输入, (list, tuple)):
            for i, 视频路径 in enumerate(视频输入):
                if isinstance(视频路径, str) and os.path.exists(视频路径):
                    文件名 = f"视频_{时间戳}_{i+1}{os.path.splitext(视频路径)[1]}"
                    目标路径 = os.path.join(输出路径, 文件名)
                    import shutil
                    shutil.copy2(视频路径, 目标路径)
                    print(f"🎥 已保存视频: {文件名}")
        elif isinstance(视频输入, str) and os.path.exists(视频输入):
            文件名 = f"视频_{时间戳}{os.path.splitext(视频输入)[1]}"
            目标路径 = os.path.join(输出路径, 文件名)
            import shutil
            shutil.copy2(视频输入, 目标路径)
            print(f"🎥 已保存视频: {文件名}")
    
    def 计划关机(self, 延迟秒数):
        """
        计划系统关机
        """
        def 关机任务():
            print(f"⏰ 工作流已完成，{延迟秒数}秒后系统将关机...")
            print("❌ 要取消关机，请使用'取消计划关机'节点或运行取消命令")
            
            # 倒计时显示
            for i in range(延迟秒数, 0, -1):
                if i % 30 == 0 or i <= 10:
                    print(f"⏳ 关机倒计时: {i}秒")
                time.sleep(1)
            
            # 执行关机命令
            self.执行关机()
        
        # 启动关机线程
        self.shutdown_scheduled = True
        self.shutdown_timer = threading.Thread(target=关机任务)
        self.shutdown_timer.daemon = True
        self.shutdown_timer.start()
    
    def 执行关机(self):
        """
        执行系统关机命令
        """
        try:
            系统类型 = platform.system().lower()
            
            print("🔌 正在执行关机命令...")
            
            if 系统类型 == "windows":
                # Windows关机命令
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
            elif 系统类型 == "darwin":
                # macOS关机命令
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            else:
                # Linux关机命令
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 关机命令执行失败: {e}")
            print("💡 请确保您有执行关机命令的权限")
        except Exception as e:
            print(f"❌ 关机过程中发生错误: {e}")
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")


class CancelScheduledShutdown:
    """
    取消计划关机节点
    用于取消已经计划的自动关机
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "确认取消": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ()
    FUNCTION = "取消关机"
    CATEGORY = "⚡ 自动关机小助手"
    OUTPUT_NODE = True
    
    def 取消关机(self, 确认取消):
        """
        取消计划的系统关机
        """
        if not 确认取消:
            print("❌ 取消关机操作已取消")
            return ()
            
        try:
            系统类型 = platform.system().lower()
            
            if 系统类型 == "windows":
                subprocess.run(["shutdown", "/a"], check=True)
                print("✅ Windows关机计划已取消")
            elif 系统类型 == "darwin":
                subprocess.run(["sudo", "killall", "shutdown"], check=True)
                print("✅ macOS关机计划已取消")
            else:
                subprocess.run(["sudo", "shutdown", "-c"], check=True)
                print("✅ Linux关机计划已取消")
                
        except Exception as e:
            print(f"❌ 取消关机失败: {e}")
            print("💡 可能没有正在进行的关机计划")
        
        return ()

# 全局变量用于跟踪关机状态
shutdown_manager = {
    'scheduled': False,
    'timer': None
}