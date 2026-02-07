#!/usr/bin/env python3
"""
AI NVCB One-Click Setup Script

Kết hợp chức năng từ ai_nvcb_utility.py và update_and_test.py thành một script setup duy nhất.
Script này sẽ tự động:
1. Thiết lập môi trường (.env.example → .env)
2. Stash và pull git changes
3. Tạo virtual environment (venv) để cô lập dependencies
4. Cài đặt dependencies (pip install -r requirements.txt)
5. Tải và cấu hình AI model (mặc định: qwen3:4b-instruct-2507-q4_K_M)
6. Kiểm tra dependencies

Usage:
    python one_click_setup.py                    # Chạy full setup
    python one_click_setup.py --skip-git         # Bỏ qua git operations
    python one_click_setup.py --skip-model       # Bỏ qua model setup
    python one_click_setup.py --skip-deps        # Bỏ qua cài đặt dependencies
    python one_click_setup.py --skip-venv        # Bỏ qua tạo virtual environment
    python one_click_setup.py --dry-run          # Xem trước không thực hiện
    python one_click_setup.py --force            # Bỏ qua xác nhận
"""

import os
import sys
import shutil
import subprocess
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


# ==================== CONSTANTS ====================
DEFAULT_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
SCRIPT_DIR = Path(__file__).parent
ENV_EXAMPLE_PATH = SCRIPT_DIR / ".env.example"
ENV_PATH = SCRIPT_DIR / ".env"
REQUIREMENTS_PATH = SCRIPT_DIR / "requirements.txt"
VENV_PATH = SCRIPT_DIR / ".venv"


def get_venv_python() -> Path:
    """Get the Python executable path for the virtual environment."""
    if sys.platform == "win32":
        return VENV_PATH / "Scripts" / "python.exe"
    return VENV_PATH / "bin" / "python"


def get_venv_pip() -> Path:
    """Get the pip executable path for the virtual environment."""
    if sys.platform == "win32":
        return VENV_PATH / "Scripts" / "pip.exe"
    return VENV_PATH / "bin" / "pip"


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Display application banner."""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║          🚀 AI NVCB One-Click Setup                       ║
║     Thiết lập môi trường và cấu hình hệ thống             ║
╚══════════════════════════════════════════════════════════╝{Colors.ENDC}
""")


def print_step(step_num: int, total_steps: int, description: str):
    """Print step header."""
    print(f"\n{Colors.BOLD}[{step_num}/{total_steps}] {Colors.BLUE}{description}{Colors.ENDC}")
    print("-" * 50)


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")


class OneClickSetup:
    """Combined setup utility for AI NVCB project."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.stashed = False
        self.stash_name = ""
        self.total_steps = self._calculate_steps()
        self.current_step = 0
        self.results: Dict[str, bool] = {}
    
    def _calculate_steps(self) -> int:
        """Calculate total number of steps based on args."""
        steps = 1  # Environment setup (always)
        if not self.args.skip_git:
            steps += 1  # Git operations
        if not self.args.skip_venv:
            steps += 1  # Virtual environment
        if not self.args.skip_deps:
            steps += 1  # Dependencies
        if not self.args.skip_model:
            steps += 1  # Model setup
        steps += 1  # Validation (always)
        return steps
    
    def next_step(self, description: str):
        """Move to next step and print header."""
        self.current_step += 1
        print_step(self.current_step, self.total_steps, description)
    
    # ==================== ENVIRONMENT SETUP ====================
    
    def setup_environment(self) -> bool:
        """Copy .env.example to .env and configure."""
        self.next_step("Thiết lập môi trường (.env)")
        
        if self.args.dry_run:
            print_info("Dry run: Sẽ sao chép .env.example → .env")
            return True
        
        try:
            # Check if .env.example exists
            if not ENV_EXAMPLE_PATH.exists():
                print_error(f"Không tìm thấy file .env.example!")
                print_info(f"Vị trí mong đợi: {ENV_EXAMPLE_PATH}")
                return False
            
            # Check if .env already exists
            if ENV_PATH.exists():
                if not self.args.force:
                    print_warning("File .env đã tồn tại!")
                    response = input("   Bạn có muốn ghi đè không? (y/N): ").strip().lower()
                    if response not in ('y', 'yes'):
                        print_info("Giữ nguyên file .env hiện tại.")
                        return True
            
            # Copy the file
            shutil.copy2(ENV_EXAMPLE_PATH, ENV_PATH)
            
            # Verify the copy
            if ENV_PATH.exists():
                print_success("Sao chép thành công .env.example → .env")
                
                # Show the content
                print(f"\n📄 Nội dung file .env:")
                print("-" * 40)
                with open(ENV_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
                print("-" * 40)
                
                return True
            else:
                print_error("Không thể tạo file .env")
                return False
                
        except PermissionError:
            print_error("Không có quyền truy cập!")
            print_info("Thử chạy với quyền Administrator.")
            return False
        except Exception as e:
            print_error(f"Lỗi: {str(e)}")
            return False
    
    # ==================== GIT OPERATIONS ====================
    
    def run_command(self, command: str, description: str = None) -> Tuple[bool, str]:
        """Run a shell command and return result."""
        if description:
            print(f"   ⏳ {description}...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                capture_output=True,
                cwd=str(SCRIPT_DIR)
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"{e.stderr}\n{e.stdout}"
    
    def git_operations(self) -> bool:
        """Handle git stash, pull, and restore."""
        self.next_step("Cập nhật từ Git")
        
        if self.args.dry_run:
            print_info("Dry run: Sẽ stash changes và git pull")
            return True
        
        # Check git status
        success, git_status = self.run_command("git status --porcelain", "Kiểm tra Git status")
        has_local_changes = git_status.strip() != ""
        
        # Stash local changes if present
        if has_local_changes:
            print_warning("Phát hiện thay đổi local, đang stash...")
            self.stash_name = f"one-click-setup-{time.strftime('%Y%m%d-%H%M%S')}"
            success, output = self.run_command(
                f'git stash push -m "{self.stash_name}"',
                "Stash local changes"
            )
            self.stashed = success and "No local changes to save" not in output
            if self.stashed:
                print_success("Đã stash local changes")
        
        # Pull latest changes
        success, output = self.run_command("git pull", "Pull latest changes")
        if success:
            print_success("Git pull thành công")
            if output.strip():
                print(f"   {output.strip()}")
        else:
            print_error(f"Git pull thất bại: {output}")
            # Restore stash if pull failed
            if self.stashed:
                self.restore_stash()
            return False
        
        # Restore stashed changes
        if self.stashed:
            self.restore_stash()
        
        return True
    
    def restore_stash(self):
        """Restore stashed changes."""
        print_info("Đang khôi phục local changes từ stash...")
        success, output = self.run_command("git stash pop", "Restore stashed changes")
        if success:
            print_success("Đã khôi phục local changes")
        else:
            print_warning(f"Không thể tự động khôi phục stash: {self.stash_name}")
            print_info("Bạn có thể khôi phục thủ công bằng: git stash pop")
    
    # ==================== VIRTUAL ENVIRONMENT ====================
    
    def setup_venv(self) -> bool:
        """Create virtual environment for isolated dependencies."""
        self.next_step("Tạo Virtual Environment")
        
        if self.args.dry_run:
            print_info(f"Dry run: Sẽ kiểm tra/tạo venv tại {VENV_PATH}")
            return True
        
        venv_python = get_venv_python()
        
        # Check if venv already exists and is valid
        if VENV_PATH.exists() and venv_python.exists():
            print_success(f"Virtual environment đã tồn tại: {VENV_PATH}")
            print_info(f"   Python: {venv_python}")
            print_info("Sẽ sử dụng venv hiện tại. Dependencies sẽ được cập nhật ở bước tiếp theo.")
            return True
        
        # Venv doesn't exist or is broken - create new one
        if VENV_PATH.exists() and not venv_python.exists():
            print_warning("Venv tồn tại nhưng không hợp lệ (thiếu Python executable)")
            print_info("Đang xóa venv hỏng và tạo lại...")
            try:
                shutil.rmtree(VENV_PATH)
            except Exception as e:
                print_error(f"Không thể xóa venv hỏng: {e}")
                return False
        
        print_info(f"Đang tạo virtual environment mới tại: {VENV_PATH}")
        
        try:
            import venv
            # Create venv with pip
            venv.create(VENV_PATH, with_pip=True)
            
            if venv_python.exists():
                print_success(f"Đã tạo virtual environment!")
                print_info(f"   Python: {venv_python}")
                return True
            else:
                print_error("Tạo venv thất bại - không tìm thấy Python executable")
                return False
                
        except Exception as e:
            print_error(f"Lỗi khi tạo virtual environment: {e}")
            return False
    
    # ==================== DEPENDENCIES ====================
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies using pip."""
        self.next_step("Cài đặt Dependencies")
        
        if self.args.dry_run:
            print_info("Dry run: Sẽ chạy pip install -r requirements.txt")
            return True
        
        # Check if requirements.txt exists
        if not REQUIREMENTS_PATH.exists():
            print_error(f"Không tìm thấy file requirements.txt!")
            return False
        
        # Determine which Python/pip to use
        venv_python = get_venv_python()
        if not self.args.skip_venv and venv_python.exists():
            python_exe = str(venv_python)
            print_info(f"Sử dụng venv Python: {venv_python}")
        else:
            python_exe = sys.executable
            print_warning("Cài đặt vào Python hệ thống (không dùng venv)")
        
        print_info("Đang cài đặt dependencies từ requirements.txt...")
        print_info("(Quá trình này có thể mất vài phút)")
        
        try:
            # Use subprocess to show real-time output
            process = subprocess.Popen(
                [python_exe, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(SCRIPT_DIR)
            )
            
            # Stream output
            output_lines = []
            for line in process.stdout:
                line = line.strip()
                if line:
                    output_lines.append(line)
                    # Show progress for important lines
                    if any(keyword in line.lower() for keyword in ['installing', 'successfully', 'requirement']):
                        print(f"   {line[:80]}...")
            
            process.wait()
            
            if process.returncode == 0:
                print_success("Cài đặt dependencies thành công!")
                return True
            else:
                print_error("Cài đặt dependencies thất bại!")
                print("\n".join(output_lines[-10:]))  # Show last 10 lines
                return False
                
        except Exception as e:
            print_error(f"Lỗi khi cài đặt dependencies: {e}")
            return False
    
    # ==================== MODEL MANAGEMENT ====================
    
    def get_current_model(self) -> str:
        """Get the current model from .env file."""
        try:
            if ENV_PATH.exists():
                with open(ENV_PATH, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('MODEL_NAME='):
                            return line.split('=', 1)[1].strip()
            return DEFAULT_MODEL
        except Exception:
            return DEFAULT_MODEL
    
    def get_ollama_models(self) -> Optional[List[Dict[str, Any]]]:
        """Get list of installed Ollama models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # Timeout 30 giây
            )
            
            models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        name = parts[0]
                        size = parts[2] if len(parts) > 2 else "Unknown"
                        models.append({
                            'name': name,
                            'size': size,
                            'raw_line': line
                        })
            
            return models
        except subprocess.TimeoutExpired:
            print_error("Ollama không phản hồi (timeout 30s)")
            print_info("Kiểm tra xem Ollama có đang chạy không: ollama serve")
            return None
        except subprocess.CalledProcessError:
            print_error("Không thể kết nối với Ollama")
            print_info("Đảm bảo Ollama đang chạy: ollama serve")
            return None
        except FileNotFoundError:
            print_error("Không tìm thấy Ollama")
            print_info("Cài đặt Ollama từ: https://ollama.ai")
            return None
    
    def pull_model(self, model_name: str) -> bool:
        """Download/pull a model using Ollama."""
        try:
            print_info(f"Đang tải model: {model_name}...")
            print_info("(Quá trình này có thể mất vài phút tùy thuộc vào kích thước model)")
            
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"   {line}")
            
            process.wait()
            
            if process.returncode == 0:
                print_success(f"Tải thành công model: {model_name}")
                return True
            else:
                print_error(f"Lỗi khi tải model {model_name}")
                return False
                
        except FileNotFoundError:
            print_error("Không tìm thấy Ollama")
            print_info("Cài đặt Ollama từ: https://ollama.ai")
            return False
    
    def setup_model(self) -> bool:
        """Setup AI model (download if needed, cleanup unused)."""
        self.next_step("Thiết lập AI Model")
        
        target_model = self.get_current_model()
        print_info(f"Model cần thiết: {target_model}")
        
        if self.args.dry_run:
            print_info(f"Dry run: Sẽ kiểm tra và tải model {target_model} nếu cần")
            return True
        
        # Get installed models
        models = self.get_ollama_models()
        if models is None:
            return False
        
        # Check if target model exists
        model_exists = any(model['name'] == target_model for model in models)
        
        if model_exists:
            print_success(f"Model {target_model} đã được cài đặt!")
        else:
            print_warning(f"Model {target_model} chưa được cài đặt")
            
            if not self.args.force:
                response = input(f"   Bạn có muốn tải model {target_model} không? (Y/n): ").strip().lower()
                if response in ('n', 'no'):
                    print_warning("Bỏ qua tải model. Bạn cần tải model thủ công sau.")
                    return True
            
            if not self.pull_model(target_model):
                return False
        
        # Show installed models
        models = self.get_ollama_models()
        if models:
            print(f"\n📋 Các model đã cài đặt:")
            for model in models:
                status = "📌 (đang sử dụng)" if model['name'] == target_model else ""
                print(f"   - {model['name']} ({model['size']}) {status}")
        
        return True
    
    # ==================== VALIDATION ====================
    
    def validate_setup(self) -> bool:
        """Validate the setup by checking dependencies."""
        self.next_step("Kiểm tra và xác nhận")
        
        if self.args.dry_run:
            print_info("Dry run: Sẽ kiểm tra các dependencies")
            return True
        
        all_passed = True
        
        # List of dependencies to test
        dependencies = [
            ("fastapi", "import fastapi"),
            ("uvicorn", "import uvicorn"),
            ("streamlit", "import streamlit"),
            ("langchain", "import langchain"),
            ("requests", "import requests"),
            ("python-dotenv", "import dotenv"),
        ]
        
        print("🧪 Kiểm tra dependencies:")
        for name, import_statement in dependencies:
            try:
                print(f"   Testing {name}... ", end="")
                exec(import_statement)
                print(f"{Colors.GREEN}✅{Colors.ENDC}")
            except ImportError as e:
                print(f"{Colors.FAIL}❌ - {e}{Colors.ENDC}")
                all_passed = False
            except Exception as e:
                print(f"{Colors.WARNING}⚠️ - {e}{Colors.ENDC}")
        
        # Check .env file
        print(f"\n📄 Kiểm tra cấu hình:")
        if ENV_PATH.exists():
            print(f"   .env file: {Colors.GREEN}✅ Tồn tại{Colors.ENDC}")
            model = self.get_current_model()
            print(f"   MODEL_NAME: {Colors.CYAN}{model}{Colors.ENDC}")
        else:
            print(f"   .env file: {Colors.FAIL}❌ Không tồn tại{Colors.ENDC}")
            all_passed = False
        
        # Check Ollama
        if not self.args.skip_model:
            print(f"\n🤖 Kiểm tra Ollama:")
            models = self.get_ollama_models()
            if models is not None:
                target_model = self.get_current_model()
                model_exists = any(model['name'] == target_model for model in models)
                if model_exists:
                    print(f"   Model {target_model}: {Colors.GREEN}✅ Sẵn sàng{Colors.ENDC}")
                else:
                    print(f"   Model {target_model}: {Colors.FAIL}❌ Chưa cài đặt{Colors.ENDC}")
                    all_passed = False
        
        return all_passed
    
    # ==================== MAIN RUN ====================
    
    def run(self) -> bool:
        """Run the complete setup process."""
        print_banner()
        
        print(f"📋 Cấu hình setup:")
        print(f"   • Skip Git: {'Có' if self.args.skip_git else 'Không'}")
        print(f"   • Skip Venv: {'Có' if self.args.skip_venv else 'Không'}")
        print(f"   • Skip Dependencies: {'Có' if self.args.skip_deps else 'Không'}")
        print(f"   • Skip Model: {'Có' if self.args.skip_model else 'Không'}")
        print(f"   • Dry Run: {'Có' if self.args.dry_run else 'Không'}")
        print(f"   • Force: {'Có' if self.args.force else 'Không'}")
        print(f"   • Model mặc định: {DEFAULT_MODEL}")
        
        if not self.args.force and not self.args.dry_run:
            print()
            response = input("Bạn có muốn tiếp tục? (Y/n): ").strip().lower()
            if response in ('n', 'no'):
                print_info("Hủy bỏ setup.")
                return False
        
        start_time = time.time()
        
        # Step 1: Environment setup
        self.results['environment'] = self.setup_environment()
        
        # Step 2: Git operations (if not skipped)
        if not self.args.skip_git:
            self.results['git'] = self.git_operations()
        
        # Step 3: Virtual environment setup (if not skipped)
        if not self.args.skip_venv:
            self.results['venv'] = self.setup_venv()
        
        # Step 4: Install dependencies (if not skipped)
        if not self.args.skip_deps:
            self.results['dependencies'] = self.install_dependencies()
        
        # Step 4: Model setup (if not skipped)
        if not self.args.skip_model:
            self.results['model'] = self.setup_model()
        
        # Step 5: Validation
        self.results['validation'] = self.validate_setup()
        
        # Summary
        duration = time.time() - start_time
        self.print_summary(duration)
        
        return all(self.results.values())
    
    def print_summary(self, duration: float):
        """Print setup summary."""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║                    📊 KẾT QUẢ SETUP                       ║
╚══════════════════════════════════════════════════════════╝{Colors.ENDC}
""")
        
        for step, success in self.results.items():
            status = f"{Colors.GREEN}✅ Thành công{Colors.ENDC}" if success else f"{Colors.FAIL}❌ Thất bại{Colors.ENDC}"
            step_name = {
                'environment': 'Thiết lập môi trường',
                'git': 'Git operations',
                'venv': 'Virtual environment',
                'dependencies': 'Cài đặt dependencies',
                'model': 'Thiết lập AI model',
                'validation': 'Kiểm tra xác nhận'
            }.get(step, step)
            print(f"   {step_name}: {status}")
        
        print(f"\n⏱️  Thời gian: {duration:.1f} giây")
        
        if all(self.results.values()):
            print(f"""
{Colors.GREEN}🎉 SETUP HOÀN TẤT!{Colors.ENDC}

💡 Bây giờ bạn có thể chạy ứng dụng:
   python run_backend.py     # Khởi động Backend API
   python run_frontend.py    # Khởi động Frontend UI
""")
        else:
            print(f"""
{Colors.WARNING}⚠️  Một số bước setup thất bại.{Colors.ENDC}
   Vui lòng kiểm tra lỗi ở trên và thử lại.
""")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI NVCB One-Click Setup - Thiết lập môi trường và cấu hình hệ thống",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python one_click_setup.py                    # Full setup
  python one_click_setup.py --skip-git         # Bỏ qua git operations
  python one_click_setup.py --skip-venv        # Bỏ qua tạo virtual environment
  python one_click_setup.py --skip-model       # Bỏ qua model setup
  python one_click_setup.py --skip-deps        # Bỏ qua cài đặt dependencies
  python one_click_setup.py --dry-run          # Xem trước không thực hiện
  python one_click_setup.py --force            # Bỏ qua xác nhận
        """
    )
    
    parser.add_argument(
        '--skip-git',
        action='store_true',
        help='Bỏ qua git stash/pull operations'
    )
    parser.add_argument(
        '--skip-venv',
        action='store_true',
        help='Bỏ qua tạo virtual environment (cài vào Python hệ thống)'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Bỏ qua cài đặt dependencies'
    )
    parser.add_argument(
        '--skip-model',
        action='store_true',
        help='Bỏ qua thiết lập AI model'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Xem trước các bước sẽ thực hiện (không thay đổi gì)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Bỏ qua tất cả xác nhận (cẩn thận!)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        setup = OneClickSetup(args)
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}👋 Đã hủy bởi người dùng.{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Lỗi không mong đợi: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
