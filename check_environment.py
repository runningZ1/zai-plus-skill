#!/usr/bin/env python3
"""
环境检查和验证工具
检查zai-plus-skill运行所需的环境配置
"""
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class EnvironmentChecker:
    """环境检查器"""

    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []

    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("检查Python版本...")
        version = sys.version_info

        if version.major == 3 and version.minor >= 8:
            self.checks_passed.append(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.checks_failed.append(
                f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)"
            )
            return False

    def check_node_installed(self) -> bool:
        """检查Node.js是否安装"""
        print("检查Node.js...")
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.checks_passed.append(f"✅ Node.js已安装: {version}")
                return True
            else:
                self.checks_failed.append("❌ Node.js未安装或无法执行")
                return False
        except Exception as e:
            self.checks_failed.append(f"❌ Node.js检查失败: {e}")
            return False

    def check_npm_packages(self) -> bool:
        """检查npm包是否安装"""
        print("检查npm包...")
        try:
            # 先检查本地安装
            result = subprocess.run(
                ['npm', 'list', 'zhipuai-sdk-nodejs-v4'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=Path(__file__).parent,
                shell=True  # Windows需要shell=True
            )

            if 'zhipuai-sdk-nodejs-v4@' in result.stdout:
                self.checks_passed.append("✅ zhipuai-sdk-nodejs-v4已安装（本地）")
                return True

            # 检查全局安装
            result_global = subprocess.run(
                ['npm', 'list', '-g', 'zhipuai-sdk-nodejs-v4'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if 'zhipuai-sdk-nodejs-v4@' in result_global.stdout:
                self.checks_passed.append("✅ zhipuai-sdk-nodejs-v4已安装（全局）")
                return True
            else:
                self.checks_failed.append("❌ zhipuai-sdk-nodejs-v4未安装")
                self.warnings.append("   运行: npm install zhipuai-sdk-nodejs-v4")
                return False

        except Exception as e:
            self.checks_failed.append(f"❌ npm包检查失败: {e}")
            return False

    def check_config_file(self) -> Tuple[bool, Dict]:
        """检查配置文件"""
        print("检查配置文件...")
        config_path = Path(__file__).parent / "mcp_config.json"

        if not config_path.exists():
            self.checks_failed.append(f"❌ 配置文件不存在: {config_path}")
            return False, {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.checks_passed.append("✅ 配置文件格式正确")

            # 检查必要字段
            if "env" not in config:
                self.checks_failed.append("❌ 配置文件缺少 'env' 字段")
                return False, config

            api_key = config.get("env", {}).get("Z_AI_API_KEY", "")

            if not api_key:
                self.checks_failed.append("❌ 配置文件中未找到 Z_AI_API_KEY")
                self.warnings.append("   请在 mcp_config.json 中配置 Z_AI_API_KEY")
                return False, config
            elif api_key.startswith("your-api-key") or len(api_key) < 10:
                self.checks_failed.append("❌ Z_AI_API_KEY 看起来无效")
                self.warnings.append("   请设置正确的智谱AI API密钥")
                return False, config
            else:
                masked_key = api_key[:8] + "..." + api_key[-4:]
                self.checks_passed.append(f"✅ Z_AI_API_KEY已配置: {masked_key}")
                return True, config

        except json.JSONDecodeError as e:
            self.checks_failed.append(f"❌ 配置文件JSON格式错误: {e}")
            return False, {}
        except Exception as e:
            self.checks_failed.append(f"❌ 读取配置文件失败: {e}")
            return False, {}

    def check_required_files(self) -> bool:
        """检查必要文件"""
        print("检查必要文件...")
        required_files = [
            "executor.py",
            "analyze_local_video.py",
            "SKILL.md",
            "requirements.txt"
        ]

        all_exist = True
        base_path = Path(__file__).parent

        for file_name in required_files:
            file_path = base_path / file_name
            if file_path.exists():
                self.checks_passed.append(f"✅ {file_name} 存在")
            else:
                self.checks_failed.append(f"❌ {file_name} 不存在")
                all_exist = False

        return all_exist

    def check_temp_files(self) -> None:
        """检查并清理临时文件"""
        print("检查临时文件...")
        base_path = Path(__file__).parent
        temp_patterns = [
            "temp_*.js",
            "temp_*.txt"
        ]

        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(base_path.glob(pattern))

        if temp_files:
            self.warnings.append(f"⚠️  发现 {len(temp_files)} 个临时文件:")
            for temp_file in temp_files:
                self.warnings.append(f"   - {temp_file.name}")
            self.warnings.append("   建议清理这些临时文件")
        else:
            self.checks_passed.append("✅ 无残留临时文件")

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("=" * 60)
        print("ZAI Plus Skill 环境检查")
        print("=" * 60)
        print()

        # 执行所有检查
        checks = [
            self.check_python_version(),
            self.check_node_installed(),
            self.check_npm_packages(),
            self.check_config_file()[0],
            self.check_required_files()
        ]

        # 额外检查（不影响总体结果）
        self.check_temp_files()

        print()
        print("=" * 60)
        print("检查结果")
        print("=" * 60)
        print()

        # 显示通过的检查
        if self.checks_passed:
            print("通过的检查:")
            for check in self.checks_passed:
                print(f"  {check}")
            print()

        # 显示失败的检查
        if self.checks_failed:
            print("失败的检查:")
            for check in self.checks_failed:
                print(f"  {check}")
            print()

        # 显示警告
        if self.warnings:
            print("警告和建议:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        # 总结
        total_checks = len(checks)
        passed_checks = sum(checks)

        print("=" * 60)
        print(f"总计: {passed_checks}/{total_checks} 项检查通过")
        print("=" * 60)

        return all(checks)


def main():
    """主函数"""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()

    if success:
        print("\n✅ 环境检查全部通过！可以开始使用 zai-plus-skill")
        print("\n快速开始:")
        print("  python analyze_local_video.py <视频路径>")
        sys.exit(0)
    else:
        print("\n❌ 环境检查未通过，请根据上述提示修复问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
