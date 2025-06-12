# import sys
# module_directory = '/home/scl60225/BertWithPretrained-main/Tasks'
# if module_directory not in sys.path:
#     sys.path.append(module_directory)
import sys
import os

# 获取当前文件所在的目录
current_directory = os.path.dirname(os.path.abspath(__file__))

# 构建模块目录的绝对路径
main_module_directory = os.path.join(current_directory, 'BertWithPretrained_main')

# 构建子模块目录的绝对路径
sub_module_directory = os.path.join(main_module_directory, 'Tasks')

# 将模块目录路径添加到 sys.path 中
if main_module_directory not in sys.path:
    sys.path.append(main_module_directory)

# 将模块目录路径添加到 sys.path 中
if sub_module_directory not in sys.path:
    sys.path.append(sub_module_directory)
